"""
routes.py - FastAPI routes for the Tokopedia scraper pipeline.

Pipeline:
  preflight (optional)
  -> scrape raw products
  -> normalize
  -> optional budget filter (local, after raw data exists)
  -> Qwen relevance filter
  -> result
  -> feedback learning

Removed: category_filter (hardcoded keywords pretending to be AI).
Qwen IS the semantic filter.
"""
from __future__ import annotations

import asyncio
import traceback
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from src.ai.learning import save_feedback
from src.ai.relevance import filter_relevance
from src.ai.reset import reset_ai_memory
from src.scraper.budget_filter import FilterResult, filter_by_budget
from src.scraper.dedupe import deduplicate_products
from src.scraper.engine_selector import EngineRunResult, EngineSelectionResult, run_scraper_engines
from src.scraper.normalizer import normalize_products_with_report
from src.server.lifecycle import register_task, unregister_task
from src.server.progress import complete_progress, fail_progress, get_progress, init_progress, update_progress
from src.server.schemas import FeedbackRequest, ProgressResponse, SearchRequest
from src.utils.currency import calculate_budget_range, format_rupiah, parse_rupiah
from src.utils.debug import safe_save_debug, save_json_debug
from src.utils.eta import ETACalculator
from src.utils.logger import log


router = APIRouter()
_results_store: dict[str, dict[str, Any]] = {}


def cleanup_task(search_id: str, task: asyncio.Task) -> None:
    try:
        exc = task.exception()
        if exc:
            log(f"[{search_id}]", f"Unhandled task exception: {exc}", "ERROR")
    except asyncio.CancelledError:
        pass
    finally:
        unregister_task(search_id)


@router.post("/api/search")
async def start_search(req: SearchRequest):
    search_id = str(uuid.uuid4())
    target_count = max(1, min(int(req.target_count), 100))
    raw_target = max(100, target_count * 4)

    req.target_count = target_count
    init_progress(search_id, target_count, raw_target, req.engine_mode)

    task = asyncio.create_task(run_scrape_job_wrapper(search_id, req, raw_target))
    register_task(search_id, task)
    task.add_done_callback(lambda t: cleanup_task(search_id, t))
    return {"success": True, "search_id": search_id}


@router.get("/api/progress/{search_id}", response_model=ProgressResponse)
async def fetch_progress(search_id: str):
    progress = get_progress(search_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Search ID not found")
    return progress


@router.get("/api/result/{search_id}")
async def fetch_result(search_id: str):
    result = _results_store.get(search_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found or not ready")
    return result


@router.post("/api/feedback")
async def handle_feedback(req: FeedbackRequest):
    """Save user feedback to teach Qwen. Supports multi-category correction."""
    try:
        save_feedback(
            query=req.query,
            product=req.product,
            ai_decision=req.ai_decision or {},
            correction=req.correction,
            categories=req.categories or [],
            note=req.note or "",
        )
        # Save debug artifact for this feedback
        if req.search_id:
            save_json_debug(req.search_id, "feedback_saved.json", {
                "query": req.query,
                "product_title": req.product.get("title", ""),
                "correction": req.correction,
                "categories": req.categories,
                "note": req.note,
            })
        return {"success": True, "message": "Feedback saved."}
    except Exception as exc:
        log("API", f"Feedback save error: {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/api/ai/reset")
async def handle_ai_reset():
    """Reset AI learning files only. Does NOT touch the Ollama model."""
    if reset_ai_memory():
        return {"success": True, "message": "AI memory reset. Ollama model untouched."}
    raise HTTPException(status_code=500, detail="Failed to reset AI memory.")


@router.get("/api/preflight/{engine}")
async def run_preflight_check(engine: str, query: str = "laptop gaming"):
    """
    Run a preflight check for the given engine and return opened_real_page status.
    Use this to diagnose ERR_HTTP2_PROTOCOL_ERROR before starting a full scrape.
    """
    from src.scraper.preflight import run_preflight
    search_id = f"preflight_{uuid.uuid4().hex[:8]}"
    result = await run_preflight(search_id, engine, query)
    return result


async def run_scrape_job_wrapper(search_id: str, req: SearchRequest, raw_target: int) -> None:
    try:
        await run_scrape_job(search_id, req, raw_target)
    except asyncio.CancelledError:
        log(f"[{search_id}]", "Scrape job cancelled.", "WARN")
        update_progress(search_id, stage="cancelled", done=True, error="Server shutting down")
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        log(f"[{search_id}]", f"Unhandled exception:\n{tb}", "ERROR")
        fail_progress(search_id, f"Internal Error: {exc}")
        safe_save_debug(search_id, error=f"{exc}\n{tb}", products=[], progress=get_progress(search_id))


def _budget_info(filter_result: FilterResult) -> dict[str, Any] | None:
    if filter_result.budget_value is None:
        return None
    return {
        "budget": filter_result.budget_value,
        "min": filter_result.min_price,
        "max": filter_result.max_price,
        "tolerance": filter_result.tolerance,
        "debug_path": filter_result.debug_path,
        "reasons": filter_result.reasons,
    }


def _sort_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by AI confidence first, then cheapest valid price."""
    return sorted(
        products,
        key=lambda p: (
            -float(p.get("relevance_score") or 0),
            p.get("price_value") if p.get("price_value") is not None else 10**18,
        ),
    )


async def _filter_pipeline(
    search_id: str,
    req: SearchRequest,
    raw_products: list[dict[str, Any]],
    eta_calc: ETACalculator,
    engine_name: str = "selected",
) -> dict[str, Any]:
    """
    Normalize -> dedupe -> optional budget filter -> Qwen relevance filter.
    No category_filter. Qwen is the semantic filter.
    """
    engine = engine_name or "selected"
    normalizer = normalize_products_with_report(raw_products, engine, search_id)
    normalized = normalizer.output
    deduped = deduplicate_products(normalized)

    update_progress(
        search_id,
        stage="budget_filtering",
        percent=78,
        message="Filtering budget..." if req.budget else "Budget kosong: filter dinonaktifkan",
        found=len(deduped),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    # Budget filter: local, runs after raw products exist, optional
    budget_result = filter_by_budget(deduped, req.budget, req.tolerance)
    candidates = budget_result.kept  # all products if no budget; budget-filtered if budget set

    if budget_result.budget_value is not None:
        from src.utils.debug import save_budget_filter_debug
        budget_result.debug_path = save_budget_filter_debug(search_id, budget_result.debug_payload(), engine)

    update_progress(
        search_id,
        stage="ai_filtering",
        percent=85,
        message="Validasi relevansi (Qwen AI)..." if req.use_ai else "AI mati: filter fallback...",
        found=len(deduped),
        valid=len(candidates),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    # Qwen relevance filter: THIS is the semantic filter. Not hardcoded keywords.
    ai_valid = await filter_relevance(req.query, candidates, req.use_ai, search_id)
    final = _sort_products(ai_valid)[: req.target_count]

    error = ""
    if not candidates and budget_result.budget_value is not None:
        error = (
            f"0 produk lolos budget {format_rupiah(budget_result.min_price)} - "
            f"{format_rupiah(budget_result.max_price)}. "
            f"Coba naikkan budget/tolerance."
        )
    elif not ai_valid:
        error = "Semua produk ditolak oleh Qwen AI. Coba disable AI atau tambah feedback."
    elif not final:
        error = "Tidak ada produk setelah filter final."

    return {
        "raw_products": raw_products,
        "normalizer": normalizer,
        "deduped": deduped,
        "budget": budget_result,
        "ai_valid": ai_valid,
        "final": final,
        "error": error,
    }


def _engine_run_payload(run: EngineRunResult) -> dict[str, Any]:
    """Serialize one engine run for API output. Includes opened_real_page."""
    return {
        "engine": run.engine,
        "ok": run.ok,
        "opened_real_page": run.opened_real_page,
        "error_type": run.error_type,
        "raw_count": run.raw_products_found,
        "raw_scraped": run.raw_products_found,
        "duration_seconds": round(run.duration_seconds, 2),
        "status": "success" if run.ok else "fail",
        "error": run.error,
        "debug_files": [p for p in run.debug_files if p],
    }


async def _finish_compare(
    search_id: str,
    req: SearchRequest,
    selection: EngineSelectionResult,
    eta_calc: ETACalculator,
) -> None:
    """Filter both engine outputs and store comparison metrics."""
    comparison: list[dict[str, Any]] = []

    for run in selection.runs:
        if not run.ok or not run.products:
            comparison.append({
                **_engine_run_payload(run),
                "budget_valid_count": 0,
                "ai_valid_count": 0,
                "data": [],
                "budget_debug_path": None,
                "normalizer_debug_path": None,
            })
            continue

        update_progress(
            search_id,
            active_engine=run.engine,
            stage="compare_filtering",
            percent=75,
            message=f"Compare: filter {run.engine}...",
            found=len(run.products),
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        filtered = await _filter_pipeline(search_id, req, run.products, eta_calc, run.engine)
        budget_result: FilterResult = filtered["budget"]
        normalizer = filtered["normalizer"]
        data = filtered["final"]

        comparison.append({
            **_engine_run_payload(run),
            "budget_valid_count": len(budget_result.kept),
            "ai_valid_count": len(filtered["ai_valid"]),
            "data": data,
            "products": data,
            "error": filtered["error"] if not data else "",
            "normalizer_debug_path": normalizer.debug_path,
            "budget_debug_path": budget_result.debug_path,
        })

    # Best engine = most AI-valid products
    selected = max(
        comparison,
        key=lambda c: (c["ai_valid_count"], c["budget_valid_count"], c["raw_count"]),
        default=None,
    )
    selected_engine = selected["engine"] if selected else None
    final_data = (selected or {}).get("data", [])[: req.target_count]

    _results_store[search_id] = {
        "success": True,
        "search_id": search_id,
        "query": req.query,
        "engine_mode": req.engine_mode,
        "selected_engine": selected_engine,
        "count": len(final_data),
        "requested_count": req.target_count,
        "data": final_data,
        "comparison": comparison,
        "budget_info": None,
    }
    complete_progress(search_id)


async def run_scrape_job(search_id: str, req: SearchRequest, raw_target: int) -> None:
    log(f"[{search_id}]", f"Starting '{req.query}' target={req.target_count} mode={req.engine_mode}", "INFO")
    eta_calc = ETACalculator()

    selection = await run_scraper_engines(
        search_id, req.query, raw_target, eta_calc,
        req.engine_mode, req.budget, req.tolerance
    )

    if req.engine_mode == "compare" and selection.runs:
        await _finish_compare(search_id, req, selection, eta_calc)
        return

    if not selection.ok or not selection.products:
        # Build a clear error message that includes opened_real_page diagnosis
        error_msg = selection.error or "Tidak ada produk ditemukan."

        # Check if any run reported a preflight failure
        for run in selection.runs:
            if not run.opened_real_page and run.error_type:
                error_msg = (
                    f"Browser tidak bisa membuka halaman Tokopedia. "
                    f"error_type={run.error_type}. "
                    f"Ini bukan masalah selector - browser membuka Chrome error page. "
                    f"Lihat debug: data/debug/{search_id}/"
                )
                break

        fail_progress(search_id, error_msg)
        return

    update_progress(
        search_id,
        active_engine=selection.selected_engine or "unknown",
        stage="deduplicating",
        percent=74,
        message="Menghapus duplikat...",
        found=len(selection.products),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    filtered = await _filter_pipeline(
        search_id, req, selection.products, eta_calc,
        selection.selected_engine or "selected",
    )
    budget_result: FilterResult = filtered["budget"]

    if not filtered["final"]:
        fail_progress(search_id, filtered["error"])
        return

    update_progress(
        search_id,
        stage="finalizing",
        percent=95,
        message="Menyiapkan hasil...",
        valid=len(filtered["final"]),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    _results_store[search_id] = {
        "success": True,
        "search_id": search_id,
        "query": req.query,
        "engine_mode": req.engine_mode,
        "selected_engine": selection.selected_engine,
        "fallback_message": selection.fallback_message,
        "engine_runs": [_engine_run_payload(run) for run in selection.runs],
        "raw_count": len(selection.products),
        "deduped_count": len(filtered["deduped"]),
        "budget_valid_count": len(budget_result.kept),
        "ai_valid_count": len(filtered["ai_valid"]),
        "count": len(filtered["final"]),
        "requested_count": req.target_count,
        "data": filtered["final"],
        "budget_info": _budget_info(budget_result),
    }

    complete_progress(search_id)
    log(f"[{search_id}]", f"Job complete. raw={len(selection.products)} ai_valid={len(filtered['ai_valid'])} returned={len(filtered['final'])}", "OK")
