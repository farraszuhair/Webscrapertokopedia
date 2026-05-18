"""
routes.py - FastAPI routes and scrape job pipeline.
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
from src.scraper.category_filter import CategoryFilterResult, filter_laptop_candidates
from src.scraper.dedupe import deduplicate_products
from src.scraper.engine_selector import EngineRunResult, run_scraper_engines
from src.scraper.normalizer import normalize_products_with_report
from src.server.lifecycle import register_task, unregister_task
from src.server.progress import complete_progress, fail_progress, get_progress, init_progress, update_progress
from src.server.schemas import FeedbackRequest, ProgressResponse, SearchRequest
from src.utils.currency import calculate_budget_range, format_rupiah, parse_rupiah
from src.utils.debug import safe_save_debug, save_budget_filter_debug, save_category_filter_debug
from src.utils.eta import ETACalculator
from src.utils.logger import log


router = APIRouter()
_results_store: dict[str, dict[str, Any]] = {}


def cleanup_task(search_id: str, task: asyncio.Task) -> None:
    """Remove task from lifecycle registry after it finishes."""
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
    task.add_done_callback(lambda done_task: cleanup_task(search_id, done_task))
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
    try:
        save_feedback(req.query, req.product, req.feedback, req.reason)
        return {"success": True, "message": "Feedback saved."}
    except Exception as exc:
        log("API", f"Feedback save error: {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/api/ai/reset")
async def handle_ai_reset():
    if reset_ai_memory():
        return {"success": True, "message": "AI memory reset successfully."}
    raise HTTPException(status_code=500, detail="Failed to reset memory.")


async def run_scrape_job_wrapper(search_id: str, req: SearchRequest, raw_target: int) -> None:
    """Keep background exceptions visible and saved to debug files."""
    try:
        await run_scrape_job(search_id, req, raw_target)
    except asyncio.CancelledError:
        log(f"[{search_id}]", "Scrape job cancelled.", "WARN")
        update_progress(search_id, stage="cancelled", done=True, error="Server shutting down, scrape cancelled")
        raise
    except Exception as exc:
        tb = traceback.format_exc()
        log(f"[{search_id}]", f"Unhandled exception in job:\n{tb}", "ERROR")
        fail_progress(search_id, f"Internal Error: {exc}")
        safe_save_debug(search_id, error=f"{exc}\n{tb}", products=[], progress=get_progress(search_id))


def _budget_progress_message(filter_result: FilterResult) -> str:
    """Build progress text for the active budget range."""
    if filter_result.budget_value is None:
        return "Budget kosong: filter budget dinonaktifkan"
    return f"Filtering budget {format_rupiah(filter_result.min_price)} - {format_rupiah(filter_result.max_price)}"


def _budget_info(filter_result: FilterResult) -> dict[str, Any] | None:
    """Return result metadata only when budget is active."""
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


def _category_failure_message(raw_count: int, category_result: CategoryFilterResult) -> str:
    """Specific error when scraping found products but none are laptop candidates."""
    message = (
        f"Produk ditemukan {raw_count}. Kandidat laptop: 0. "
        f"Aksesori ditolak: {category_result.rejected_accessory_count}."
    )
    if category_result.debug_path:
        message += f" Debug: {category_result.debug_path}"
    return message


def _budget_failure_message(raw_count: int, category_result: CategoryFilterResult, budget_result: FilterResult) -> str:
    """Specific error when candidates exist but budget removes all of them."""
    below = budget_result.reasons.get("below_budget_range", 0)
    above = budget_result.reasons.get("above_budget_range", 0)
    invalid = budget_result.reasons.get("invalid_price", 0)
    message = (
        f"Produk ditemukan {raw_count}, tapi 0 kandidat laptop gaming sesuai budget "
        f"{format_rupiah(budget_result.min_price)} - {format_rupiah(budget_result.max_price)}. "
        f"Aksesori ditolak {category_result.rejected_accessory_count}. "
        f"Laptop di bawah budget {below}, di atas budget {above}, harga tidak valid {invalid}."
    )
    if budget_result.debug_path:
        message += f" Debug: {budget_result.debug_path}"
    return message


def _sort_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by AI score first, then cheapest valid price."""
    return sorted(
        products,
        key=lambda item: (
            -float(item.get("relevance_score") or 0),
            item.get("price_value") if item.get("price_value") is not None else 10**18,
        ),
    )


async def _filter_pipeline(
    search_id: str,
    req: SearchRequest,
    raw_products: list[dict[str, Any]],
    eta_calc: ETACalculator,
    engine_name: str | None = None,
    compare_mode: bool = False,
) -> dict[str, Any]:
    """Run normalize, category filter, budget filter, and AI filter."""
    engine = engine_name or "selected"
    raw_count = len(raw_products or [])
    normalizer = normalize_products_with_report(raw_products, engine, search_id)
    normalized = normalizer.output
    deduped = deduplicate_products(normalized)
    budget_value = parse_rupiah(req.budget)
    min_price, max_price = calculate_budget_range(budget_value, req.tolerance)

    update_progress(
        search_id,
        stage="category_filtering",
        percent=76,
        message="Menyaring aksesori sebelum budget...",
        found=len(deduped),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    category_result = filter_laptop_candidates(deduped, req.query)
    category_result.debug_path = save_category_filter_debug(search_id, category_result.debug_payload(), engine)

    update_progress(
        search_id,
        stage="budget_filtering",
        percent=80,
        message=(
            f"Filtering budget {format_rupiah(min_price)} - {format_rupiah(max_price)}"
            if budget_value and budget_value > 0
            else "Budget kosong: filter budget dinonaktifkan"
        ),
        found=len(deduped),
        valid=category_result.candidate_count,
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    filter_result = filter_by_budget(category_result.candidates, req.budget, req.tolerance)
    if filter_result.budget_value is not None:
        filter_result.debug_path = save_budget_filter_debug(search_id, filter_result.debug_payload(), engine)

    update_progress(
        search_id,
        stage="budget_filtering",
        percent=84,
        message=(
            f"Produk ditemukan {len(deduped)}. Kandidat laptop: {category_result.candidate_count}. "
            f"Aksesori ditolak: {category_result.rejected_accessory_count}. Budget valid: {len(filter_result.kept)}."
        ),
        found=len(deduped),
        valid=len(filter_result.kept),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    if not category_result.candidates:
        return {
            "raw_products": raw_products,
            "normalizer": normalizer,
            "deduped": deduped,
            "category": category_result,
            "budget": filter_result,
            "ai_valid": [],
            "final": [],
            "error": _category_failure_message(raw_count, category_result),
        }

    if not filter_result.kept:
        return {
            "raw_products": raw_products,
            "normalizer": normalizer,
            "deduped": deduped,
            "category": category_result,
            "budget": filter_result,
            "ai_valid": [],
            "final": [],
            "error": _budget_failure_message(raw_count, category_result, filter_result),
        }

    update_progress(
        search_id,
        stage="ai_filtering",
        percent=86,
        message="Validasi relevansi (AI)..." if req.use_ai else "AI mati: memakai rule filter ringan...",
        found=len(deduped),
        valid=len(filter_result.kept),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    ai_valid = await filter_relevance(req.query, filter_result.kept, req.use_ai)
    final = _sort_products(ai_valid)[: req.target_count]

    return {
        "raw_products": raw_products,
        "normalizer": normalizer,
        "deduped": deduped,
        "category": category_result,
        "budget": filter_result,
        "ai_valid": ai_valid,
        "final": final,
        "error": "" if final else "Semua produk ditolak oleh AI validator.",
    }


def _engine_run_payload(run: EngineRunResult) -> dict[str, Any]:
    """Serialize one engine run for API output."""
    return {
        "engine": run.engine,
        "ok": run.ok,
        "raw_count": run.raw_products_found,
        "raw_products_found": run.raw_products_found,
        "duration_seconds": round(run.duration_seconds, 2),
        "duration": round(run.duration_seconds, 2),
        "status": "success" if run.ok else "fail",
        "error": run.error,
        "debug_files": [path for path in run.debug_files if path],
    }


async def _finish_compare(search_id: str, req: SearchRequest, selection, eta_calc: ETACalculator) -> None:
    """Filter both engine outputs and store comparison metrics."""
    comparison: list[dict[str, Any]] = []

    for run in selection.runs:
        if not run.ok:
            comparison.append({
                **_engine_run_payload(run),
                "candidate_count": 0,
                "laptop_candidates": 0,
                "rejected_accessories": 0,
                "budget_valid_count": 0,
                "valid_after_budget": 0,
                "ai_valid_count": 0,
                "valid_after_ai": 0,
                "data": [],
                "products": [],
                "category_debug_path": None,
                "budget_debug_path": None,
                "normalizer_debug_path": None,
                "debug_files": [path for path in run.debug_files if path],
            })
            continue

        update_progress(
            search_id,
            active_engine=run.engine,
            stage="compare_filtering",
            percent=75,
            message=f"Compare: filter hasil {run.engine}...",
            found=len(run.products),
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        filtered = await _filter_pipeline(search_id, req, run.products, eta_calc, run.engine, compare_mode=True)
        category_result: CategoryFilterResult = filtered["category"]
        budget_result: FilterResult = filtered["budget"]
        normalizer = filtered["normalizer"]
        error = run.error or filtered["error"]
        data = filtered["final"]
        debug_files = [
            *(run.debug_files or []),
            normalizer.debug_path,
            category_result.debug_path,
            budget_result.debug_path,
        ]

        comparison.append({
            **_engine_run_payload(run),
            "candidate_count": category_result.candidate_count,
            "laptop_candidates": category_result.candidate_count,
            "rejected_accessories": category_result.rejected_accessory_count,
            "budget_valid_count": len(budget_result.kept),
            "valid_after_budget": len(budget_result.kept),
            "ai_valid_count": len(filtered["ai_valid"]),
            "valid_after_ai": len(filtered["ai_valid"]),
            "data": data,
            "products": data,
            "error": "" if data else error,
            "normalizer_debug_path": normalizer.debug_path,
            "category_debug_path": category_result.debug_path,
            "budget_debug_path": budget_result.debug_path,
            "category_reasons": category_result.reasons,
            "budget_reasons": budget_result.reasons,
            "debug_files": [path for path in debug_files if path],
        })

    selected = max(
        comparison,
        key=lambda item: (item["valid_after_ai"], item["valid_after_budget"], item["laptop_candidates"], item["raw_products_found"]),
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
    log(
        f"[{search_id}]",
        f"Starting '{req.query}' target={req.target_count} engine_mode={req.engine_mode}",
        "INFO",
    )
    eta_calc = ETACalculator()

    selection = await run_scraper_engines(search_id, req.query, raw_target, eta_calc, req.engine_mode, req.budget, req.tolerance)
    if req.engine_mode == "compare" and selection.runs:
        await _finish_compare(search_id, req, selection, eta_calc)
        return

    if not selection.ok or not selection.products:
        fail_progress(search_id, selection.error or "Tidak ada produk ditemukan di halaman.")
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
        search_id,
        req,
        selection.products,
        eta_calc,
        selection.selected_engine or "selected",
    )
    category_result: CategoryFilterResult = filtered["category"]
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
        "category_info": {
            "candidates": category_result.candidate_count,
            "rejected_accessories": category_result.rejected_accessory_count,
            "debug_path": category_result.debug_path,
        },
        "count": len(filtered["final"]),
        "requested_count": req.target_count,
        "data": filtered["final"],
        "budget_info": _budget_info(budget_result),
    }

    complete_progress(search_id)
    log(f"[{search_id}]", f"Job complete. Returned {len(filtered['final'])} products.", "OK")
