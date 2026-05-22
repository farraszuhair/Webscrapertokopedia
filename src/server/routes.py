"""
routes.py - FastAPI routes for the Tokopedia scraper pipeline.

Pipeline per spec:
  preflight -> scrape raw -> normalize -> budget filter -> AI orchestrator -> result -> feedback

The active AI path is model-orchestrated: rules handle obvious products, the
best installed small classifier checks borderline products, and rule fallback
keeps searches useful when Ollama has no supported model installed.
"""
from __future__ import annotations

import asyncio
import os
import traceback
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from src.ai.learning import save_feedback
from src.ai.memory_store import FEEDBACK_FILE as LEGACY_FEEDBACK_FILE, read_jsonl
from src.ai.model_registry import get_orchestrator_status
from src.ai.relevance import RELEVANCE_THRESHOLD, filter_relevance
from src.ai.reset import reset_ai_memory
from src.scraper.budget_filter import FilterResult, filter_by_budget
from src.scraper.dedupe import deduplicate_products
from src.scraper.engine_selector import EngineRunResult, EngineSelectionResult, run_scraper_engines
from src.scraper.normalizer import normalize_products_with_report
from src.server.lifecycle import register_task, unregister_task
from src.server.progress import complete_progress, fail_progress, get_progress, init_progress, update_progress
from src.server.schemas import FeedbackRequest, ProgressResponse, SearchRequest
from src.config import OVERFETCH_MULTIPLIER
from src.utils.currency import format_rupiah
from src.utils.debug import safe_save_debug, save_json_debug
from src.utils.eta import ETACalculator
from src.utils.logger import log


router = APIRouter()
_results_store: dict[str, dict[str, Any]] = {}


def _product_cache_key(product: dict[str, Any]) -> str:
    url = str(product.get("url") or product.get("product_url") or "").strip().lower()
    if url:
        return f"url:{url.split('?')[0]}"
    title = str(product.get("title") or "").strip().lower()
    price = str(product.get("price_value") or product.get("price_raw") or "").strip().lower()
    return f"title:{title}|price:{price}"


def _is_ai_valid(product: dict[str, Any]) -> bool:
    try:
        confidence = float(product.get("relevance_score", product.get("ai_confidence", 0)) or 0)
    except (TypeError, ValueError):
        confidence = 0.0
    return bool(product.get("ai_decision", True)) and confidence >= RELEVANCE_THRESHOLD


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
    overfetch_multiplier = max(1, int(OVERFETCH_MULTIPLIER))
    max_raw_candidates = max(target_count, int(os.getenv("MAX_RAW_CANDIDATES", "300")))
    raw_target = min(max_raw_candidates, max(100, target_count * overfetch_multiplier))
    req.target_count = target_count
    init_progress(search_id, target_count, raw_target, req.engine_mode)
    progress = get_progress(search_id) or {}
    task = asyncio.create_task(run_scrape_job_wrapper(search_id, req, raw_target))
    register_task(search_id, task)
    task.add_done_callback(lambda t: cleanup_task(search_id, t))
    return {
        "success": True,
        "search_id": search_id,
        "requested_count": target_count,
        "raw_target": raw_target,
        "started_at_epoch_ms": progress.get("started_at_epoch_ms"),
    }


@router.get("/api/progress/{search_id}", response_model=ProgressResponse)
async def fetch_progress(search_id: str):
    progress = get_progress(search_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Search ID not found")
    return progress


@router.get("/api/ai/status")
async def ai_status():
    """Return installed supported Ollama models and active orchestrator capabilities."""
    return get_orchestrator_status()


@router.get("/api/result/{search_id}")
async def fetch_result(search_id: str):
    result = _results_store.get(search_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found or not ready")
    return result


@router.post("/api/feedback")
async def handle_feedback(req: FeedbackRequest):
    """Save user feedback from Benar/Salah result-card actions."""
    try:
        product = req.product or {"id": req.product_id, "title": req.product_title}
        reasons = req.reasons or req.selected_reasons or []
        feedback_type = req.feedback_type or ("positive" if req.user_action == "benar" else "negative")
        user_action = req.user_action or ("benar" if feedback_type == "positive" else "salah")
        corrected_label = req.corrected_label or ("relevan" if feedback_type == "positive" else "tidak_relevan")
        save_feedback(
            query=req.query,
            product_id=req.product_id or str(product.get("id") or product.get("url") or "unknown"),
            product_title=req.product_title or str(product.get("title") or ""),
            user_action=user_action,
            selected_reasons=reasons,
            custom_reason=req.note or req.custom_reason,
            corrected_label=corrected_label,
            ai_label=req.ai_label,
            ai_confidence=req.ai_confidence,
            product=product,
            query_intent=req.query_intent,
            feedback_type=feedback_type,
            rule_score=req.rule_score,
            sort_mode=req.sort_mode,
            decision_source=str(getattr(req, "decision_source", "") or product.get("decision_source") or product.get("ai_source") or ""),
        )
        if req.search_id:
            save_json_debug(req.search_id, "feedback_saved.json", req.model_dump())
        return {"ok": True, "success": True, "message": "Feedback saved"}
    except Exception as exc:
        log("API", f"Feedback save error: {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/feedback/summary")
async def feedback_summary():
    records = read_jsonl(LEGACY_FEEDBACK_FILE, limit=500)
    positives = sum(1 for item in records if item.get("feedback_type") == "positive" or item.get("user_action") == "benar")
    negatives = sum(1 for item in records if item.get("feedback_type") == "negative" or item.get("user_action") == "salah")
    return {
        "ok": True,
        "total": len(records),
        "positive": positives,
        "negative": negatives,
    }


@router.post("/api/ai/reset")
async def handle_ai_reset():
    """Clear AI learning files. Does NOT touch the Ollama model."""
    if reset_ai_memory():
        return {"success": True, "message": "AI memory reset. Ollama model untouched."}
    raise HTTPException(status_code=500, detail="Failed to reset AI memory.")


@router.get("/api/preflight/{engine}")
async def run_preflight_check(engine: str, query: str = "laptop gaming"):
    """
    Run preflight check for the given engine.
    Returns opened_real_page + error_type before starting a full scrape.
    Useful for diagnosing ERR_HTTP2_PROTOCOL_ERROR without wasting time.
    """
    from src.scraper.preflight import run_preflight
    search_id = f"preflight_{uuid.uuid4().hex[:8]}"
    return await run_preflight(search_id, engine, query)


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


def _sort_products(products: list[dict[str, Any]], sort_mode: str = "terbaik") -> list[dict[str, Any]]:
    mode = sort_mode if sort_mode in {"terbaik", "termurah", "most_trusted"} else "terbaik"
    if mode == "termurah":
        return sorted(
            products,
            key=lambda p: (
                p.get("price_value") if p.get("price_value") is not None else 10**18,
                -float(p.get("relevance_score") or p.get("ai_confidence") or 0),
            ),
        )
    if mode == "most_trusted":
        return sorted(
            products,
            key=lambda p: (
                -score_trusted_product(p),
                -float(p.get("relevance_score") or p.get("ai_confidence") or 0),
                p.get("price_value") if p.get("price_value") is not None else 10**18,
            ),
        )
    return sorted(
        products,
        key=lambda p: (
            -float(p.get("relevance_score") or p.get("ai_confidence") or 0),
            -score_best_product(p),
            p.get("price_value") if p.get("price_value") is not None else 10**18,
        ),
    )


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def normalize_score(value: Any, min_value: float, max_value: float) -> float:
    parsed = _num(value, min_value)
    if max_value <= min_value:
        return 0.0
    return max(0.0, min(1.0, (parsed - min_value) / (max_value - min_value)))


def _sold_score(product: dict[str, Any]) -> float:
    sold = _num(product.get("sold_count"), 0.0)
    return normalize_score(min(sold, 1000.0), 0.0, 1000.0)


def _rating_score(product: dict[str, Any]) -> float:
    rating = _num(product.get("rating"), 0.0)
    if rating <= 0:
        return 0.0
    return max(0.0, min(1.0, rating / 5.0))


def _shop_score(product: dict[str, Any]) -> float:
    text = " ".join(
        str(product.get(key) or "")
        for key in ("shop_name", "shop", "shop_badge", "title")
    ).lower()
    if any(token in text for token in ("official", "mall", "power merchant", "pro")):
        return 1.0
    return 0.5 if (product.get("shop_name") or product.get("shop")) else 0.0


def _ai_confidence(product: dict[str, Any]) -> float:
    return max(0.0, min(1.0, _num(product.get("ai_confidence", product.get("relevance_score")), 0.0)))


def _price_sanity_score(product: dict[str, Any]) -> float:
    price = product.get("price_value")
    if isinstance(price, int) and price > 0:
        return 1.0
    return 0.0 if product.get("price_parse_failed") else 0.35


def _data_completeness_score(product: dict[str, Any]) -> float:
    keys = ("title", "price_raw", "url", "image", "shop", "location", "rating", "sold")
    return sum(1 for key in keys if product.get(key)) / len(keys)


def score_trusted_product(product: dict[str, Any]) -> float:
    return (
        _rating_score(product) * 0.35
        + _sold_score(product) * 0.30
        + _shop_score(product) * 0.15
        + _ai_confidence(product) * 0.20
    )


def score_best_product(product: dict[str, Any]) -> float:
    return (
        _ai_confidence(product) * 0.35
        + _rating_score(product) * 0.20
        + _sold_score(product) * 0.20
        + _price_sanity_score(product) * 0.10
        + _data_completeness_score(product) * 0.15
    )


def is_accessory_like(product: dict[str, Any], query: str) -> bool:
    query_lower = query.lower()
    title = str(product.get("title") or "").lower()
    accessory_terms = {
        "mouse", "keyboard", "charger", "adaptor", "adapter", "cooling",
        "cooler", "stand", "headset", "earphone", "webcam", "sleeve",
        "tas", "bag", "ram", "ssd", "sticker", "sparepart", "spare parts",
        "baterai", "battery",
    }
    query_asks_accessory = any(term in query_lower for term in accessory_terms)
    return not query_asks_accessory and any(term in title for term in accessory_terms)


def _recommendation_payload(product: dict[str, Any] | None, reason: str) -> dict[str, Any] | None:
    if not product:
        return None
    return {
        "id": product.get("id", ""),
        "title": product.get("title", ""),
        "price": product.get("price_raw") or product.get("price_text") or "",
        "price_value": product.get("price_value"),
        "rating": product.get("rating"),
        "sold_count": product.get("sold_count"),
        "sold": product.get("sold") or product.get("sold_text") or "",
        "shop_name": product.get("shop_name") or product.get("shop") or "",
        "shop_location": product.get("shop_location") or product.get("location") or "",
        "image": product.get("image") or product.get("image_url") or "",
        "url": product.get("url") or product.get("product_url") or "",
        "ai_confidence": product.get("ai_confidence", product.get("relevance_score", 0)),
        "reason": reason,
    }


def build_recommendations(products: list[dict[str, Any]], query: str) -> dict[str, Any]:
    relevant = [p for p in products if p.get("ai_decision", True)]
    if not relevant:
        relevant = list(products)

    main_products = [p for p in relevant if not is_accessory_like(p, query)] or relevant
    priced = [
        p for p in main_products
        if isinstance(p.get("price_value"), int) and p.get("price_value") > 0
    ]

    trusted = max(main_products, key=score_trusted_product, default=None)
    cheapest = min(priced, key=lambda p: p.get("price_value", 10**18), default=None)
    best = max(main_products, key=score_best_product, default=None)

    return {
        "cheapest": _recommendation_payload(
            cheapest,
            "Harga paling rendah dari produk yang lolos filter.",
        ),
        "trusted": _recommendation_payload(
            trusted,
            "Dipilih karena rating, penjualan, dan skor kepercayaan paling kuat.",
        ),
        "best": _recommendation_payload(
            best,
            "Skor keseluruhan terbaik dari relevansi, rating, penjualan, dan kelengkapan data.",
        ),
    }


def _build_recommendations(query: str, products: list[dict[str, Any]]) -> dict[str, Any]:
    return build_recommendations(products, query)


def _limited_reason(requested_count: int, displayed_count: int, candidate_count: int | None = None) -> str | None:
    if displayed_count >= requested_count:
        return None
    if candidate_count is not None:
        return f"Diminta {requested_count}, tetapi hanya {displayed_count} produk aman yang bisa ditampilkan dari {candidate_count} kandidat valid."
    return f"Diminta {requested_count}, tetapi hanya {displayed_count} produk aman yang bisa ditampilkan."


def _build_result_warning(
    *,
    requested: int,
    displayed: int,
    candidate_pool_count: int,
    budget_enabled: bool,
    budget_valid_count: int,
    fallback_added: int,
) -> str:
    warnings: list[str] = []
    target_display = min(requested, candidate_pool_count)
    if budget_enabled and budget_valid_count < requested:
        warnings.append(f"Diminta {requested}, tetapi hanya {budget_valid_count} kandidat sesuai budget.")
    elif candidate_pool_count < requested:
        warnings.append(f"Diminta {requested}, tetapi hanya {candidate_pool_count} kandidat valid.")
    if displayed < target_display:
        warnings.append(f"Ditampilkan {displayed} produk aman dari {candidate_pool_count} kandidat valid.")
    if fallback_added > 0:
        warnings.append(f"{fallback_added} produk confidence rendah ditambahkan agar hasil mendekati target.")
    return " ".join(dict.fromkeys(warnings))


async def _filter_pipeline(
    search_id: str,
    req: SearchRequest,
    raw_products: list[dict[str, Any]],
    eta_calc: ETACalculator,
    engine_name: str = "selected",
) -> dict[str, Any]:
    """
    Full filter pipeline: normalize -> dedupe -> budget -> intent-aware AI -> sort.
    Returns dict with all intermediate counts and AI orchestrator status.
    """
    engine = engine_name or "selected"
    normalizer = normalize_products_with_report(raw_products, engine, search_id)
    normalized = normalizer.output
    deduped = deduplicate_products(normalized)
    image_total = len(normalized)
    missing_rate = (normalizer.images_missing_count / image_total) if image_total else 0.0
    log(
        "IMAGES",
        (
            f"engine={engine} images_extracted_count={normalizer.images_extracted_count} "
            f"images_missing_count={normalizer.images_missing_count} missing_rate={missing_rate:.2%}"
        ),
        "INFO",
    )
    if image_total and missing_rate > 0.70:
        save_json_debug(
            search_id,
            f"image_missing_debug_{engine}.json",
            {
                "engine": engine,
                "images_extracted_count": normalizer.images_extracted_count,
                "images_missing_count": normalizer.images_missing_count,
                "missing_rate": round(missing_rate, 4),
                "samples": normalized[:20],
            },
        )

    update_progress(
        search_id,
        stage="deduplicating",
        percent=65,
        message=f"Deduped {len(normalized)} raw products into {len(deduped)} candidates",
        found=len(normalized),
        valid=len(deduped),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    update_progress(
        search_id,
        stage="budget_filtering",
        percent=68,
        message="Filtering budget..." if req.budget else "Budget kosong: skip budget filter",
        found=len(deduped),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    budget_result = filter_by_budget(deduped, req.budget, req.tolerance)
    candidates = budget_result.kept
    budget_enabled = budget_result.budget_value is not None
    orchestrator_status = get_orchestrator_status()

    log(
        "BUDGET",
        (
            f"enabled={str(budget_enabled).lower()} raw={len(raw_products)} "
            f"deduped={len(deduped)} valid={len(candidates)} "
            f"min={budget_result.min_price} max={budget_result.max_price} "
            f"rejected={len(budget_result.rejected)}"
        ),
        "INFO",
    )

    if budget_result.budget_value is not None:
        from src.utils.debug import save_budget_filter_debug
        budget_result.debug_path = save_budget_filter_debug(search_id, budget_result.debug_payload(), engine)

    update_progress(
        search_id,
        stage="ai_filtering",
        percent=70,
        message="Filtering relevansi dengan AI Orchestrator..." if req.use_ai else "AI nonaktif: rule scoring...",
        found=len(deduped),
        valid=len(candidates),
        elapsed_seconds=eta_calc.get_elapsed(),
        ai_orchestrator={
            "enabled": bool(req.use_ai),
            "classifier": orchestrator_status.get("classifier"),
            "semantic_enabled": bool(orchestrator_status.get("capabilities", {}).get("semantic")),
            "json_repair_enabled": bool(orchestrator_status.get("capabilities", {}).get("json_repair")),
        },
    )

    for candidate in candidates:
        candidate["_requested_target"] = req.target_count
        candidate["_scraped_raw"] = len(raw_products)
        candidate["_after_dedupe"] = len(deduped)
        candidate["_budget_valid"] = len(candidates)
        candidate["_candidate_pool"] = len(candidates)

    ai_result = await filter_relevance(req.query, candidates, req.use_ai, search_id)
    ai_valid, ai_status = ai_result
    ai_meta = getattr(ai_result, "meta", {}) or {}

    update_progress(
        search_id,
        stage="ranking",
        percent=88,
        message="Ranking hasil...",
        found=len(deduped),
        valid=len(ai_valid),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    target_display = min(req.target_count, len(candidates))
    ranked = list(ai_valid)
    final = ranked[:target_display]
    fallback_added = int(ai_meta.get("fallback_added", ai_meta.get("fallback_expansion_count", 0)) or 0)
    final_warning = _build_result_warning(
        requested=req.target_count,
        displayed=len(final),
        candidate_pool_count=len(candidates),
        budget_enabled=budget_enabled,
        budget_valid_count=len(candidates),
        fallback_added=fallback_added,
    )
    limited = final_warning or None

    update_progress(
        search_id,
        stage="recommendation_building",
        percent=93,
        message="Membangun rekomendasi cepat...",
        found=len(deduped),
        valid=len(final),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    recommendations = _build_recommendations(req.query, final)
    has_enough = len(final) >= target_display
    classifier_checked = ai_meta.get("classifier_checked", ai_meta.get("ai_checked", ai_meta.get("llm_checked_count", 0)))
    semantic_checked = ai_meta.get("semantic_checked", ai_meta.get("semantic_checked_count", 0))
    metadata = {
        "requested": req.target_count,
        "requested_count": req.target_count,
        "scraped_raw": len(raw_products),
        "raw_scraped_count": len(raw_products),
        "raw_scraped": len(raw_products),
        "after_dedupe": len(deduped),
        "deduped_count": len(deduped),
        "budget_valid": len(candidates),
        "budget_valid_count": len(candidates),
        "candidate_pool": len(candidates),
        "ai_input_count": len(candidates),
        "rule_accepted": ai_meta.get("rule_accepted", ai_meta.get("rule_accepted_count", 0)),
        "rule_rejected": ai_meta.get("rule_rejected", ai_meta.get("rule_rejected_count", 0)),
        "borderline_candidates": ai_meta.get("borderline_candidates", 0),
        "semantic_checked": semantic_checked,
        "semantic_checked_count": semantic_checked,
        "classifier_checked": classifier_checked,
        "ai_checked": classifier_checked,
        "ai_calls_attempted": ai_meta.get("ai_calls_attempted", 0),
        "ai_calls_succeeded": ai_meta.get("ai_calls_succeeded", 0),
        "ai_accepted": ai_meta.get("ai_accepted", ai_meta.get("ai_accepted_count", 0)),
        "ai_accepted_count": ai_meta.get("ai_accepted", ai_meta.get("ai_accepted_count", 0)),
        "ai_rejected": ai_meta.get("ai_rejected", 0),
        "ai_fallback": ai_meta.get("ai_fallback", 0),
        "fallback_added": fallback_added,
        "displayed_count": len(final),
        "displayed": len(final),
        "has_enough_results": has_enough,
        "limited_reason": limited,
        "ai_skip_reason": ai_meta.get("ai_skip_reason"),
        "ai_status": ai_status,
        "ai_warning": final_warning,
        "ai_orchestrator": ai_meta.get("ai_orchestrator", orchestrator_status),
        "ai_model": ai_meta.get("selected_model"),
        "query_intent": ai_meta.get("query_intent"),
        "sort_mode": req.sort_mode,
        "rule_accepted_count": ai_meta.get("rule_accepted_count", 0),
        "rule_rejected_count": ai_meta.get("rule_rejected_count", 0),
        "llm_checked_count": classifier_checked,
        "fallback_expansion_count": fallback_added,
    }

    log(
        "COUNT",
        (
            f"requested={req.target_count} raw_target={get_progress(search_id).get('raw_target') if get_progress(search_id) else '?'} "
            f"raw_scraped={len(raw_products)} deduped={len(deduped)} "
            f"budget_valid={len(candidates)} candidate_pool={len(candidates)} target_display={target_display} "
            f"semantic_checked={semantic_checked} classifier_checked={classifier_checked} "
            f"ai_calls_attempted={metadata['ai_calls_attempted']} ai_calls_succeeded={metadata['ai_calls_succeeded']} "
            f"ai_accepted={metadata['ai_accepted']} ai_rejected={metadata['ai_rejected']} ai_fallback={metadata['ai_fallback']} "
            f"fallback_added={fallback_added} displayed={len(final)} "
            f"ai_skip_reason={metadata['ai_skip_reason']} "
            f"has_enough={str(has_enough).lower()}"
            + (f' reason="{limited}"' if limited else "")
        ),
        "INFO",
    )

    error = ""
    ai_warning = final_warning

    if ai_status == "unavailable" and not ai_warning:
        ai_warning = "AI unavailable for borderline products; deterministic relevance fallback was used."
    elif ai_status == "failed":
        ai_warning = ai_warning or "AI filtering failed. Products were displayed with explicit fallback."
    metadata["ai_warning"] = ai_warning

    if not candidates and budget_result.budget_value is not None:
        error = (
            f"0 produk lolos budget {format_rupiah(budget_result.min_price)} - "
            f"{format_rupiah(budget_result.max_price)}. Coba naikkan budget/tolerance."
        )
    elif not ai_valid:
        if ai_status in ("failed", "unavailable"):
            error = f"0 produk tersisa setelah fallback filter. {ai_warning}"
        else:
            error = "Semua produk ditolak filter relevansi. Disable AI atau tambah feedback."
    elif not final:
        error = "Tidak ada produk setelah filter final."

    return {
        "raw_products": raw_products,
        "normalizer": normalizer,
        "deduped": deduped,
        "budget": budget_result,
        "ai_valid": ai_valid,
        "ranked": ranked,
        "final": final,
        "ai_status": ai_status,
        "ai_warning": ai_warning,
        "ai_meta": ai_meta,
        "metadata": metadata,
        "recommendations": recommendations,
        "error": error,
    }


def _engine_run_payload(run: EngineRunResult) -> dict[str, Any]:
    """
    Serialize one engine run to the API response.
    raw_products_found is before any filter so callers can verify raw != 0.
    """
    count = run.raw_products_found
    return {
        "engine": run.engine,
        "ok": run.ok,
        "opened_real_page": run.opened_real_page,
        "error_type": run.error_type,
        "raw_count": count,
        "raw_scraped": count,
        "raw_products_found": count,    # ← kept for backward compat with test_engine_reports
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
    """
    Compare mode: run filter pipeline for BOTH engines independently.
    No silent fallback between engines.
    Both results are returned regardless of AI classifier status.
    """
    comparison: list[dict[str, Any]] = []

    for run in selection.runs:
        base_payload = _engine_run_payload(run)

        if not run.ok or not run.products:
            # Engine itself failed (Chrome error page / zero raw)
            comparison.append({
                **base_payload,
                "budget_count": 0,
                "budget_valid_count": 0,
                "ai_count": 0,
                "ai_valid_count": 0,
                "ai_accepted_count": 0,
                "ai_status": "skipped",
                "result_metadata": {
                    "requested_count": req.target_count,
                    "raw_scraped_count": run.raw_products_found,
                    "raw_scraped": run.raw_products_found,
                    "deduped_count": 0,
                    "budget_valid_count": 0,
                    "ai_input_count": 0,
                    "ai_accepted_count": 0,
                    "displayed_count": 0,
                    "has_enough_results": False,
                    "limited_reason": _limited_reason(req.target_count, 0),
                },
                "recommendations": _build_recommendations(req.query, []),
                "data": [],
                "products": [],
                "budget_debug_path": None,
                "normalizer_debug_path": None,
            })
            continue

        update_progress(
            search_id,
            active_engine=run.engine,
            stage="compare_filtering",
            percent=75,
            message=f"Compare: filtering {run.engine} ({len(run.products)} raw)...",
            found=len(run.products),
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        filtered = await _filter_pipeline(search_id, req, run.products, eta_calc, run.engine)
        budget_result: FilterResult = filtered["budget"]
        normalizer = filtered["normalizer"]
        data = filtered["final"]

        comparison.append({
            **base_payload,
            "budget_count": len(budget_result.kept),
            "budget_valid_count": len(budget_result.kept),
            "ai_count": len(filtered["ai_valid"]),
            "ai_valid_count": len(filtered["ai_valid"]),
            "ai_accepted_count": filtered["metadata"].get("ai_accepted_count", 0),
            "ai_status": filtered["ai_status"],
            "ai_warning": filtered["ai_warning"],
            "result_metadata": filtered["metadata"],
            "recommendations": filtered["recommendations"],
            "data": data,
            "products": data,
            "error": filtered["error"] if not data else "",
            "normalizer_debug_path": normalizer.debug_path,
            "budget_debug_path": budget_result.debug_path,
        })

    # Best engine = most AI-valid, then budget-valid, then raw
    selected = max(
        comparison,
        key=lambda c: (c["ai_valid_count"], c["budget_valid_count"], c["raw_count"]),
        default=None,
    )
    selected_engine = selected["engine"] if selected else None
    final_data = (selected or {}).get("data", [])
    selected_metadata = (selected or {}).get("result_metadata") or {
        "requested_count": req.target_count,
        "raw_scraped_count": 0,
        "raw_scraped": 0,
        "deduped_count": 0,
        "budget_valid_count": 0,
        "ai_input_count": 0,
        "ai_accepted_count": 0,
        "displayed_count": len(final_data),
        "has_enough_results": len(final_data) >= req.target_count,
        "limited_reason": _limited_reason(req.target_count, len(final_data)),
    }

    _results_store[search_id] = {
        "success": True,
        "search_id": search_id,
        "query": req.query,
        "engine_mode": req.engine_mode,
        "sort_mode": req.sort_mode,
        "selected_engine": selected_engine,
        "count": len(final_data),
        "requested_count": req.target_count,
        "displayed_count": len(final_data),
        "limited_reason": selected_metadata.get("limited_reason"),
        "result_metadata": selected_metadata,
        "recommendations": (selected or {}).get("recommendations") or _build_recommendations(req.query, final_data),
        "ai_status": (selected or {}).get("ai_status", "skipped"),
        "ai_warning": (selected or {}).get("ai_warning", ""),
        "data": final_data,
        "engine_runs": comparison,     # ← also exposed as engine_runs for consistency
        "comparison": comparison,      # ← kept for frontend renderComparison()
        "budget_info": None,
    }
    complete_progress(search_id)


async def run_scrape_job(search_id: str, req: SearchRequest, raw_target: int) -> None:
    log(f"[{search_id}]", f"Starting '{req.query}' target={req.target_count} mode={req.engine_mode}", "INFO")
    log("COUNT", f"requested={req.target_count}", "INFO")
    log("COUNT", f"raw_target={raw_target}", "INFO")
    eta_calc = ETACalculator()

    selection = await run_scraper_engines(
        search_id, req.query, raw_target, eta_calc,
        req.engine_mode, req.budget, req.tolerance
    )

    if req.engine_mode in {"compare", "compare_both"} and selection.runs:
        await _finish_compare(search_id, req, selection, eta_calc)
        return

    if not selection.ok or not selection.products:
        error_msg = selection.error or "Tidak ada produk ditemukan."
        # Annotate error with preflight context if browser failed
        for run in selection.runs:
            if not run.opened_real_page and run.error_type:
                error_msg = (
                    f"Browser membuka Chrome error page: {run.error_type}. "
                    f"Bukan masalah selector. "
                    f"Lihat debug: data/debug/{search_id}/"
                )
                break
        fail_progress(search_id, error_msg)
        return

    update_progress(
        search_id,
        active_engine=selection.selected_engine or "unknown",
        stage="deduplicating",
        percent=58,
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
        percent=96,
        message="Menyiapkan hasil...",
        valid=len(filtered["final"]),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    engine_runs = []
    for run in selection.runs:
        payload = _engine_run_payload(run)
        if run.engine == (selection.selected_engine or ""):
            payload.update({
                "budget_count": len(budget_result.kept),
                "budget_valid_count": len(budget_result.kept),
                "ai_count": len(filtered["ai_valid"]),
                "ai_valid_count": len(filtered["ai_valid"]),
                "ai_accepted_count": filtered["metadata"].get("ai_accepted_count", 0),
                "ai_status": filtered["ai_status"],
                "ai_warning": filtered["ai_warning"],
                "result_metadata": filtered["metadata"],
                "recommendations": filtered["recommendations"],
                "products": filtered["final"],
                "data": filtered["final"],
            })
        engine_runs.append(payload)

    _results_store[search_id] = {
        "success": True,
        "search_id": search_id,
        "query": req.query,
        "engine_mode": req.engine_mode,
        "sort_mode": req.sort_mode,
        "selected_engine": selection.selected_engine,
        "fallback_message": selection.fallback_message,
        "engine_runs": engine_runs,
        "raw_count": len(selection.products),
        "deduped_count": len(filtered["deduped"]),
        "budget_count": len(budget_result.kept),
        "budget_valid_count": len(budget_result.kept),
        "ai_count": len(filtered["ai_valid"]),
        "ai_valid_count": len(filtered["ai_valid"]),
        "ai_accepted_count": filtered["metadata"].get("ai_accepted_count", 0),
        "ai_status": filtered["ai_status"],
        "ai_warning": filtered["ai_warning"],
        "count": len(filtered["final"]),
        "requested_count": req.target_count,
        "displayed_count": len(filtered["final"]),
        "limited_reason": filtered["metadata"].get("limited_reason"),
        "result_metadata": filtered["metadata"],
        "recommendations": filtered["recommendations"],
        "data": filtered["final"],
        "budget_info": _budget_info(budget_result),
    }

    complete_progress(search_id)
    log(
        f"[{search_id}]",
        f"Done. raw={len(selection.products)} ai={len(filtered['ai_valid'])} "
        f"returned={len(filtered['final'])} ai_status={filtered['ai_status']}",
        "OK",
    )
