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
import time
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from src.ai.ai_filter import is_valid_product_candidate
from src.ai.feedback_store import feedback_summary_counts, reset_learning
from src.ai.learning import save_feedback
from src.ai.memory_store import FEEDBACK_FILE as LEGACY_FEEDBACK_FILE, read_jsonl
from src.ai.model_registry import get_orchestrator_status
from src.ai.relevance import filter_relevance
from src.ai.reset import reset_ai_memory
from src.scraper.budget_filter import FilterResult, filter_by_budget
from src.scraper.dedupe import deduplicate_products
from src.scraper.engine_selector import EngineRunResult, EngineSelectionResult, run_engine, run_scraper_engines
from src.scraper.normalizer import normalize_image_url, normalize_products_with_report, pick_product_image
from src.server.lifecycle import register_task, unregister_task
from src.server.progress import complete_progress, fail_progress, get_progress, init_progress, update_progress
from src.server.schemas import FeedbackRequest, ProgressResponse, SearchRequest
from src.config import OVERFETCH_MULTIPLIER, RESULT_STORE_MAX_ITEMS, RESULT_STORE_TTL_SECONDS, STRICT_BUDGET_MODE
from src.utils.currency import format_rupiah, parse_rupiah
from src.utils.debug import safe_save_debug, save_json_debug
from src.utils.eta import ETACalculator
from src.utils.logger import log


router = APIRouter()
_results_store: dict[str, dict[str, Any]] = {}


def _utc_timestamp(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def cleanup_results_store() -> None:
    """Bound the in-memory result cache by TTL and item count."""
    now = time.time()
    ttl = max(0, int(RESULT_STORE_TTL_SECONDS))
    expired_ids = [
        search_id
        for search_id, payload in _results_store.items()
        if now - float(payload.get("created_at_epoch", 0) or 0) >= ttl
    ]

    for search_id in expired_ids:
        _results_store.pop(search_id, None)

    max_items = max(1, int(RESULT_STORE_MAX_ITEMS))
    overflow = len(_results_store) - max_items
    if overflow <= 0:
        return

    oldest_ids = sorted(
        _results_store,
        key=lambda search_id: float(_results_store[search_id].get("created_at_epoch", 0) or 0),
    )[:overflow]
    for search_id in oldest_ids:
        _results_store.pop(search_id, None)


def save_result(search_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    cleanup_results_store()
    created_at_epoch = time.time()
    stored_payload = dict(payload)
    stored_payload.setdefault("search_id", search_id)
    stored_payload["created_at"] = _utc_timestamp(created_at_epoch)
    stored_payload["created_at_epoch"] = created_at_epoch
    stored_payload["expires_at"] = _utc_timestamp(created_at_epoch + max(0, int(RESULT_STORE_TTL_SECONDS)))
    _results_store[search_id] = stored_payload
    cleanup_results_store()
    return stored_payload


def get_result(search_id: str) -> dict[str, Any] | None:
    cleanup_results_store()
    return _results_store.get(search_id)


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
    return get_orchestrator_status(force_refresh=True)


@router.get("/api/result/{search_id}")
async def fetch_result(search_id: str):
    result = get_result(search_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found or not ready")
    return result


@router.get("/api/image-proxy")
async def image_proxy(url: str = Query(..., min_length=8)):
    image_url = normalize_image_url(url)
    if not image_url:
        raise HTTPException(status_code=400, detail="Invalid image URL")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Referer": "https://www.tokopedia.com/",
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(image_url, headers=headers)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Image proxy timeout") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Image proxy failed") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Image host returned {response.status_code}")

    media_type = response.headers.get("content-type", "image/jpeg").split(";", 1)[0].strip().lower()
    if not media_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="URL did not return an image")

    return Response(
        content=response.content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.post("/api/feedback")
async def handle_feedback(req: FeedbackRequest):
    """Save user feedback from Benar/Salah result-card actions."""
    try:
        product = req.normalized_product()
        reasons = req.normalized_reasons()
        feedback_type = req.normalized_feedback_type()
        user_action = req.normalized_user_action()
        corrected_label = req.normalized_corrected_label()
        note = req.normalized_note()
        result = save_feedback(
            query=req.query,
            product_id=req.normalized_product_id(),
            product_title=req.normalized_product_title(),
            user_action=user_action,
            selected_reasons=reasons,
            custom_reason=note,
            corrected_label=corrected_label,
            ai_label=req.ai_label,
            ai_confidence=req.ai_confidence,
            product=product,
            query_intent=req.query_intent,
            feedback_type=feedback_type,
            rule_score=req.rule_score,
            semantic_score=req.semantic_score,
            combined_score=req.combined_score,
            learned_adjustment=req.learned_adjustment,
            sort_mode=req.sort_mode,
            decision_source=str(getattr(req, "decision_source", "") or product.get("decision_source") or product.get("ai_source") or ""),
            learning_scope_hint=req.learning_scope_hint,
            model_used=req.model_used,
            ai_reason=req.ai_reason,
        )
        if req.search_id:
            save_json_debug(req.search_id, "feedback_saved.json", req.model_dump())
        return {
            "ok": True,
            "success": True,
            "message": "Feedback saved",
            "learning_updated": bool(result.get("learning_updated")),
        }
    except Exception as exc:
        log("API", f"Feedback save error: {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/feedback/summary")
async def feedback_summary():
    records = read_jsonl(LEGACY_FEEDBACK_FILE, limit=500)
    positives = sum(1 for item in records if item.get("feedback_type") == "positive" or item.get("user_action") == "benar")
    negatives = sum(1 for item in records if item.get("feedback_type") == "negative" or item.get("user_action") == "salah")
    sqlite_counts = feedback_summary_counts()
    return {
        "ok": True,
        "total": len(records),
        "positive": positives,
        "negative": negatives,
        **sqlite_counts,
    }


@router.post("/api/ai/reset")
async def handle_ai_reset():
    """Clear AI learning files. Does NOT touch the Ollama model."""
    if reset_ai_memory():
        return {"success": True, "message": "AI memory reset. Ollama model untouched."}
    raise HTTPException(status_code=500, detail="Failed to reset AI memory.")


@router.post("/api/learning/reset")
async def handle_learning_reset(payload: dict[str, Any]):
    """Reset scoped SQLite learning memory."""
    try:
        scope = str(payload.get("scope") or "all")
        result = reset_learning(
            scope=scope,
            query=payload.get("query"),
            constraint_key=payload.get("constraint_key"),
        )
        return {"ok": True, "success": True, "message": "Learning memory reset", **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        log("API", f"Learning reset error: {exc}", "ERROR")
        raise HTTPException(status_code=500, detail=str(exc))


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


def _candidate_pool_snapshot(
    raw_products: list[dict[str, Any]],
    req: SearchRequest,
    engine_name: str = "selected",
) -> dict[str, Any]:
    normalizer = normalize_products_with_report(raw_products, engine_name)
    deduped = deduplicate_products(normalizer.output)
    product_candidates = [product for product in deduped if is_valid_product_candidate(product)]
    invalid_non_product_removed = len(deduped) - len(product_candidates)
    budget_result = filter_by_budget(product_candidates, req.budget, req.tolerance)
    candidates = [product for product in budget_result.kept if is_valid_product_candidate(product)]
    return {
        "scraped_raw": len(raw_products),
        "after_dedupe": len(deduped),
        "valid_product_candidates": len(product_candidates),
        "invalid_non_product_removed": invalid_non_product_removed,
        "budget_valid": len(candidates),
        "candidate_pool_count": len(candidates),
        "budget_enabled": budget_result.budget_value is not None,
    }


async def _overfetch_raw_products(
    search_id: str,
    req: SearchRequest,
    raw_products: list[dict[str, Any]],
    engine_name: str,
    raw_target: int,
    eta_calc: ETACalculator,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    desired = int(req.target_count)
    max_raw = max(desired * 10, 500)
    max_scroll_rounds = 12
    attempts = 0
    products = list(raw_products or [])
    snapshot = _candidate_pool_snapshot(products, req, engine_name)
    initial_valid_pool = int(snapshot["candidate_pool_count"])
    can_load_more = engine_name in {"puppeteer", "rollback"} and len(products) < max_raw
    stop_reason = "target_met" if initial_valid_pool >= desired else "not_started"

    if initial_valid_pool < desired:
        log(
            "PIPELINE",
            (
                f"overfetch_start requested={desired} "
                f"budget_valid={initial_valid_pool} raw={len(products)}"
            ),
            "INFO",
        )

    while (
        int(snapshot["candidate_pool_count"]) < desired
        and len(products) < max_raw
        and can_load_more
        and attempts < max_scroll_rounds
    ):
        attempts += 1
        next_target = min(max_raw, max(raw_target, len(products) + desired, desired * 4))
        log(
            "PIPELINE",
            (
                f"overfetch requested={desired} valid_pool={snapshot['candidate_pool_count']} "
                f"loading_more=true attempt={attempts} next_raw_target={next_target}"
            ),
            "INFO",
        )
        update_progress(
            search_id,
            active_engine=engine_name,
            stage="overfetching",
            message="Mencari produk tambahan untuk memenuhi target valid...",
            found=len(products),
            valid=int(snapshot["candidate_pool_count"]),
            elapsed_seconds=eta_calc.get_elapsed(),
        )

        run = await run_engine(search_id, engine_name, req.query, next_target, eta_calc)
        if not run.ok or not run.products:
            can_load_more = False
            stop_reason = "load_more_exhausted"
            break

        previous_after_dedupe = int(snapshot["after_dedupe"])
        previous_valid_pool = int(snapshot["candidate_pool_count"])
        products.extend(run.products)
        snapshot = _candidate_pool_snapshot(products, req, engine_name)
        log(
            "PIPELINE",
            f"overfetch_round={attempts} raw={len(products)} budget_valid={snapshot['candidate_pool_count']}",
            "INFO",
        )
        if (
            int(snapshot["after_dedupe"]) <= previous_after_dedupe
            and int(snapshot["candidate_pool_count"]) <= previous_valid_pool
        ):
            can_load_more = False
            stop_reason = "no_new_valid_products"
            break

    final_valid_pool = int(snapshot["candidate_pool_count"])
    target_display = min(desired, final_valid_pool)
    if final_valid_pool >= desired:
        stop_reason = "target_met"
    elif len(products) >= max_raw:
        stop_reason = "raw_limit_reached"
    elif attempts >= max_scroll_rounds:
        stop_reason = "max_scroll_rounds_reached"
    elif not can_load_more and stop_reason == "not_started":
        stop_reason = "load_more_unavailable"
    log(
        "PIPELINE",
        (
            f"overfetch_done requested={desired} budget_valid={final_valid_pool} "
            f"reason={stop_reason} target_display={target_display} attempts={attempts} "
            f"loading_more={str(can_load_more).lower()}"
        ),
        "INFO",
    )
    return products, {
        "overfetch_attempted": attempts > 0,
        "overfetch_attempts": attempts,
        "overfetch_rounds": attempts,
        "overfetch_initial_valid_pool": initial_valid_pool,
        "overfetch_final_valid_pool": final_valid_pool,
        "overfetch_max_raw": max_raw,
        "overfetch_exhausted": final_valid_pool < desired,
        "overfetch_stop_reason": stop_reason,
        "raw_after_overfetch": len(products),
    }


def _public_product_payload(product: dict[str, Any]) -> dict[str, Any]:
    """Expose the required demo product shape while keeping legacy aliases."""
    payload = dict(product or {})
    image_url = pick_product_image(payload)
    price_number = parse_rupiah(payload.get("price_value"))
    if price_number is None:
        price_number = parse_rupiah(payload.get("priceNumber"))
    if price_number is None:
        price_number = parse_rupiah(payload.get("price_raw") or payload.get("price_text") or payload.get("price"))
    price_number = int(price_number or 0)

    price_text = str(payload.get("price_raw") or payload.get("price_text") or "").strip()
    if not price_text and price_number > 0:
        price_text = format_rupiah(price_number)

    store_name = str(payload.get("storeName") or payload.get("shop_name") or payload.get("shop") or payload.get("store") or "").strip()
    confidence_value = payload.get("confidenceScore")
    if confidence_value in (None, ""):
        confidence_value = payload.get("confidence", payload.get("relevance_score", payload.get("ai_confidence", 0)))
    try:
        confidence_score = max(0.0, min(1.0, float(confidence_value or 0)))
    except (TypeError, ValueError):
        confidence_score = 0.0

    relevance_reason = str(
        payload.get("relevanceReason")
        or payload.get("ai_reason")
        or payload.get("reason")
        or payload.get("ai_explanation")
        or payload.get("category_reason")
        or ""
    ).strip()

    payload.update({
        "id": str(payload.get("id") or payload.get("url") or payload.get("product_url") or payload.get("title") or ""),
        "title": str(payload.get("title") or ""),
        "price": price_text,
        "priceNumber": price_number,
        "price_value": price_number,
        "price_raw": price_text,
        "price_text": price_text,
        "image_url": image_url,
        "image": image_url or "",
        "has_image": bool(image_url),
        "storeName": store_name,
        "shop_name": store_name,
        "rating": payload.get("rating") or 0,
        "soldCount": int(_num(payload.get("soldCount", payload.get("sold_count")), 0)),
        "sold_count": int(_num(payload.get("sold_count", payload.get("soldCount")), 0)),
        "url": str(payload.get("url") or payload.get("product_url") or ""),
        "source": str(payload.get("source") or payload.get("source_engine") or "tokopedia"),
        "confidenceScore": round(confidence_score, 3),
        "relevanceReason": relevance_reason,
        "outside_budget": bool(payload.get("outside_budget", False)),
        "budget_badge": str(payload.get("budget_badge") or ""),
        "target_first_fallback": bool(payload.get("target_first_fallback", False)),
    })
    return payload


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
    image_url = pick_product_image(product)
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
        "image_url": image_url,
        "image": image_url or "",
        "has_image": bool(image_url),
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
        return f"Diminta {requested_count}, tetapi hanya {displayed_count} produk bisa ditampilkan dari {candidate_count} kandidat valid."
    return f"Diminta {requested_count}, tetapi hanya {displayed_count} produk bisa ditampilkan."


def _build_result_warning(
    *,
    requested: int,
    candidate_pool_count: int,
    fallback_added: int,
    ai_skip_reason: str | None,
    displayed: int,
    target_display: int,
    overfetch_stop_reason: str | None = None,
    strict_budget_mode: bool = True,
) -> str:
    warnings: list[str] = []
    if candidate_pool_count < requested:
        if strict_budget_mode:
            warnings.append(
                f"Diminta {requested}, tetapi hanya {candidate_pool_count} produk sesuai budget setelah overfetch."
            )
        else:
            warnings.append(f"Diminta {requested}, tetapi hanya {candidate_pool_count} kandidat tersedia.")
    if overfetch_stop_reason and candidate_pool_count < requested:
        warnings.append(f"Overfetch berhenti: {overfetch_stop_reason}.")
    if fallback_added > 0:
        warnings.append(f"{fallback_added} produk fallback ditambahkan agar hasil mendekati target.")
    if ai_skip_reason:
        warnings.append(f"AI classifier: {ai_skip_reason}.")
    if displayed < target_display:
        warnings.append(
            f"Ditampilkan {displayed} dari target aman {target_display}. Cek log pipeline untuk alasan produk dibuang."
        )
    return " ".join(dict.fromkeys(warnings))


def _budget_distance(product: dict[str, Any], min_price: int | None, max_price: int | None) -> int:
    price = parse_rupiah(product.get("price_value"))
    if price is None:
        price = parse_rupiah(product.get("price_raw") or product.get("price_text") or product.get("price"))
    price = int(price or 0)
    if min_price is not None and price < min_price:
        return min_price - price
    if max_price is not None and price > max_price:
        return price - max_price
    return 0


def _target_first_budget_fallbacks(
    budget_result: FilterResult,
    needed: int,
) -> list[dict[str, Any]]:
    if needed <= 0 or budget_result.budget_value is None:
        return []
    candidates = [
        dict(product)
        for product in budget_result.rejected
        if is_valid_product_candidate(product)
        and product.get("reject_reason") in {"below_budget_range", "above_budget_range"}
    ]
    candidates.sort(
        key=lambda product: (
            _budget_distance(product, budget_result.min_price, budget_result.max_price),
            parse_rupiah(product.get("price_value")) or 10**18,
        )
    )
    selected = candidates[:needed]
    for product in selected:
        product["outside_budget"] = True
        product["budget_badge"] = "Di luar budget"
        product["target_first_fallback"] = True
        product["budget_distance"] = _budget_distance(product, budget_result.min_price, budget_result.max_price)
    return selected


async def _filter_pipeline(
    search_id: str,
    req: SearchRequest,
    raw_products: list[dict[str, Any]],
    eta_calc: ETACalculator,
    engine_name: str = "selected",
    overfetch_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Full filter pipeline: normalize -> dedupe -> budget -> intent-aware AI -> sort.
    Returns dict with all intermediate counts and AI orchestrator status.
    """
    engine = engine_name or "selected"
    normalizer = normalize_products_with_report(raw_products, engine, search_id)
    normalized = normalizer.output
    deduped = deduplicate_products(normalized)
    product_candidates = [product for product in deduped if is_valid_product_candidate(product)]
    invalid_non_product_removed = len(deduped) - len(product_candidates)
    image_total = len(normalized)
    missing_rate = (normalizer.images_missing_count / image_total) if image_total else 0.0
    log(
        "IMAGE",
        (
            f"total={image_total} image_found={normalizer.images_extracted_count} "
            f"image_missing={normalizer.images_missing_count} engine={engine} "
            f"missing_rate={missing_rate:.2%}"
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
        message=f"Deduped {len(normalized)} raw products into {len(product_candidates)} valid products",
        found=len(normalized),
        valid=len(product_candidates),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    update_progress(
        search_id,
        stage="budget_filtering",
        percent=68,
        message="Filtering budget..." if req.budget else "Budget kosong: skip budget filter",
        found=len(product_candidates),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    budget_result = filter_by_budget(product_candidates, req.budget, req.tolerance)
    strict_budget_mode = bool(STRICT_BUDGET_MODE)
    target_first_mode = bool(getattr(req, "target_first_mode", False))
    budget_valid_count = len([product for product in budget_result.kept if is_valid_product_candidate(product)])
    candidates = [product for product in budget_result.kept if is_valid_product_candidate(product)]
    target_first_added = 0
    if target_first_mode and budget_valid_count < req.target_count:
        target_first_fill = _target_first_budget_fallbacks(
            budget_result,
            req.target_count - budget_valid_count,
        )
        target_first_added = len(target_first_fill)
        candidates.extend(target_first_fill)
    budget_enabled = budget_result.budget_value is not None
    orchestrator_status = get_orchestrator_status()

    log(
        "BUDGET",
        (
            f"enabled={str(budget_enabled).lower()} raw={len(raw_products)} "
            f"deduped={len(deduped)} product_candidates={len(product_candidates)} "
            f"invalid_non_product_removed={invalid_non_product_removed} budget_valid={budget_valid_count} "
            f"candidate_pool={len(candidates)} target_first_added={target_first_added} "
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

    overfetch_meta = overfetch_meta or {}
    for candidate in candidates:
        candidate["_requested_target"] = req.target_count
        candidate["_scraped_raw"] = len(raw_products)
        candidate["_after_dedupe"] = len(deduped)
        candidate["_valid_product_candidates"] = len(product_candidates)
        candidate["_invalid_non_product_removed"] = invalid_non_product_removed
        candidate["_budget_valid"] = budget_valid_count
        candidate["_candidate_pool"] = len(candidates)
        candidate["_overfetch_attempted"] = bool(overfetch_meta.get("overfetch_attempted", False))
        candidate["_overfetch_attempts"] = int(overfetch_meta.get("overfetch_attempts", 0) or 0)
        candidate["_overfetch_rounds"] = int(overfetch_meta.get("overfetch_rounds", overfetch_meta.get("overfetch_attempts", 0)) or 0)
        candidate["_overfetch_initial_valid_pool"] = int(overfetch_meta.get("overfetch_initial_valid_pool", len(candidates)) or 0)
        candidate["_overfetch_final_valid_pool"] = int(overfetch_meta.get("overfetch_final_valid_pool", len(candidates)) or 0)
        candidate["_overfetch_max_raw"] = int(overfetch_meta.get("overfetch_max_raw", 0) or 0)
        candidate["_overfetch_exhausted"] = bool(overfetch_meta.get("overfetch_exhausted", False))
        candidate["_overfetch_stop_reason"] = str(overfetch_meta.get("overfetch_stop_reason") or "")
        candidate["_raw_after_overfetch"] = int(overfetch_meta.get("raw_after_overfetch", len(raw_products)) or 0)
        candidate["_strict_budget_mode"] = strict_budget_mode
        candidate["_target_first_mode"] = target_first_mode
        candidate["_target_first_added"] = target_first_added

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
    ranked = _sort_products(list(ai_valid), req.sort_mode)
    final = ranked[:target_display]
    public_final = [_public_product_payload(product) for product in final]
    public_image_found = sum(1 for product in public_final if product.get("has_image"))
    log(
        "IMAGE",
        f"total={len(public_final)} image_found={public_image_found} image_missing={len(public_final) - public_image_found}",
        "INFO",
    )
    fallback_added = int(ai_meta.get("fallback_added", ai_meta.get("fallback_expansion_count", 0)) or 0)
    ai_timeouts = int(ai_meta.get("ai_timeouts", 0) or 0)
    ai_skip_reason = ai_meta.get("ai_skip_reason")
    final_warning = str(ai_meta.get("warning") or "").strip() or _build_result_warning(
        requested=req.target_count,
        candidate_pool_count=len(candidates),
        fallback_added=fallback_added,
        ai_skip_reason=str(ai_skip_reason) if ai_skip_reason else None,
        displayed=len(public_final),
        target_display=target_display,
        overfetch_stop_reason=str(overfetch_meta.get("overfetch_stop_reason") or "") or None,
        strict_budget_mode=strict_budget_mode,
    )
    limited = final_warning or None

    update_progress(
        search_id,
        stage="recommendation_building",
        percent=93,
        message="Membangun rekomendasi cepat...",
        found=len(deduped),
        valid=len(public_final),
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    recommendations = _build_recommendations(req.query, public_final)
    has_enough = len(public_final) >= target_display
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
        "valid_product_candidates": len(product_candidates),
        "invalid_non_product_removed": invalid_non_product_removed,
        "budget_valid": budget_valid_count,
        "budget_valid_count": budget_valid_count,
        "candidate_pool": len(candidates),
        "candidate_pool_count": len(candidates),
        "ai_input_count": len(candidates),
        "target_display": target_display,
        "image_found": public_image_found,
        "image_missing": len(public_final) - public_image_found,
        "normalizer_image_found": normalizer.images_extracted_count,
        "normalizer_image_missing": normalizer.images_missing_count,
        "overfetch_attempted": bool(overfetch_meta.get("overfetch_attempted", False)),
        "overfetch_attempts": int(overfetch_meta.get("overfetch_attempts", 0) or 0),
        "overfetch_rounds": int(overfetch_meta.get("overfetch_rounds", overfetch_meta.get("overfetch_attempts", 0)) or 0),
        "overfetch_initial_valid_pool": int(overfetch_meta.get("overfetch_initial_valid_pool", len(candidates)) or 0),
        "overfetch_final_valid_pool": int(overfetch_meta.get("overfetch_final_valid_pool", len(candidates)) or 0),
        "overfetch_max_raw": int(overfetch_meta.get("overfetch_max_raw", 0) or 0),
        "overfetch_exhausted": bool(overfetch_meta.get("overfetch_exhausted", False)),
        "overfetch_stop_reason": str(overfetch_meta.get("overfetch_stop_reason") or ""),
        "raw_after_overfetch": int(overfetch_meta.get("raw_after_overfetch", len(raw_products)) or 0),
        "strict_budget_mode": strict_budget_mode,
        "target_first_mode": target_first_mode,
        "target_first_added": target_first_added,
        "query_constraints": ai_meta.get("query_constraints", {}),
        "feedback_examples_loaded": ai_meta.get("feedback_examples_loaded", 0),
        "learned_patterns_loaded": ai_meta.get("learned_patterns_loaded", 0),
        "query_scoped_patterns": ai_meta.get("query_scoped_patterns", 0),
        "constraint_scoped_patterns": ai_meta.get("constraint_scoped_patterns", 0),
        "intent_scoped_patterns": ai_meta.get("intent_scoped_patterns", 0),
        "global_patterns": ai_meta.get("global_patterns", 0),
        "constraint_mismatch_products": ai_meta.get("constraint_mismatch_products", 0),
        "learning_adjusted_products": ai_meta.get("learning_adjusted_products", 0),
        "learned_positive_matches": ai_meta.get("learned_positive_matches", 0),
        "learned_negative_matches": ai_meta.get("learned_negative_matches", 0),
        "rule_accepted": ai_meta.get("rule_accepted", ai_meta.get("rule_accepted_count", 0)),
        "rule_rejected": ai_meta.get("rule_rejected", ai_meta.get("rule_rejected_count", 0)),
        "borderline_candidates": ai_meta.get("borderline_candidates", 0),
        "semantic_checked": semantic_checked,
        "semantic_checked_count": semantic_checked,
        "classifier_checked": classifier_checked,
        "ai_checked": classifier_checked,
        "ai_calls_attempted": ai_meta.get("ai_calls_attempted", 0),
        "ai_calls_succeeded": ai_meta.get("ai_calls_succeeded", 0),
        "ai_timeouts": ai_timeouts,
        "ai_failures": ai_meta.get("ai_failures", 0),
        "ai_batch_size": ai_meta.get("ai_batch_size"),
        "prompt_tokens_estimated": ai_meta.get("prompt_tokens_estimated", 0),
        "prompt_truncated_by_app": ai_meta.get("prompt_truncated_by_app", False),
        "ctx": ai_meta.get("ctx"),
        "ai_circuit_open": bool(ai_meta.get("ai_circuit_open", False)),
        "classifier_limit": ai_meta.get("classifier_limit"),
        "ai_accepted": ai_meta.get("ai_accepted", ai_meta.get("ai_accepted_count", 0)),
        "ai_accepted_count": ai_meta.get("ai_accepted", ai_meta.get("ai_accepted_count", 0)),
        "ai_confirmed": ai_meta.get("ai_confirmed", 0),
        "ai_rescued": ai_meta.get("ai_rescued", 0),
        "ai_rejected": ai_meta.get("ai_rejected", 0),
        "ai_fallback": ai_meta.get("ai_fallback", 0),
        "fallback_candidates": ai_meta.get("fallback_candidates", 0),
        "fallback_candidates_count": ai_meta.get("fallback_candidates_count", ai_meta.get("fallback_candidates", 0)),
        "weak_fallback_candidates": ai_meta.get("weak_fallback_candidates", 0),
        "weak_fallback_candidates_count": ai_meta.get("weak_fallback_candidates_count", ai_meta.get("weak_fallback_candidates", 0)),
        "fallback_rejected_as_junk": ai_meta.get("fallback_rejected_as_junk", 0),
        "fallback_added": fallback_added,
        "accepted_before_fallback": ai_meta.get("accepted_before_fallback", 0),
        "rejected_as_obvious_junk": ai_meta.get("rejected_as_obvious_junk", 0),
        "rejected_as_obvious_junk_count": ai_meta.get("rejected_as_obvious_junk_count", ai_meta.get("rejected_as_obvious_junk", 0)),
        "rejected_as_obvious_junk_count_before_rescue": ai_meta.get("rejected_as_obvious_junk_count_before_rescue", 0),
        "rescued_false_obvious_junk": ai_meta.get("rescued_false_obvious_junk", 0),
        "rejected_reasons_histogram": ai_meta.get("rejected_reasons_histogram", {}),
        "pipeline_debug_path": ai_meta.get("pipeline_debug_path"),
        "why_remaining_products_were_not_displayed": ai_meta.get("why_remaining_products_were_not_displayed"),
        "displayed_count": len(public_final),
        "displayed": len(public_final),
        "has_enough_results": has_enough,
        "limited_reason": limited,
        "ai_skip_reason": ai_skip_reason,
        "ai_status": ai_status,
        "ai_warning": final_warning,
        "ai_orchestrator": ai_meta.get("ai_orchestrator", orchestrator_status),
        "ai_model": ai_meta.get("selected_model"),
        "selected_classifier": ai_meta.get("selected_classifier", ai_meta.get("selected_model")),
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
            f"valid_product_candidates={len(product_candidates)} "
            f"invalid_non_product_removed={invalid_non_product_removed} "
            f"budget_valid={budget_valid_count} candidate_pool={len(candidates)} target_display={target_display} "
            f"semantic_checked={semantic_checked} classifier_checked={classifier_checked} "
            f"ai_calls_attempted={metadata['ai_calls_attempted']} ai_calls_succeeded={metadata['ai_calls_succeeded']} "
            f"ai_timeouts={metadata['ai_timeouts']} ai_failures={metadata['ai_failures']} "
            f"prompt_tokens_estimated={metadata['prompt_tokens_estimated']} ctx={metadata['ctx']} "
            f"ai_circuit_open={str(metadata['ai_circuit_open']).lower()} "
            f"ai_accepted={metadata['ai_accepted']} ai_rejected={metadata['ai_rejected']} ai_fallback={metadata['ai_fallback']} "
            f"accepted_before_fallback={metadata['accepted_before_fallback']} "
            f"fallback_candidates={metadata['fallback_candidates']} weak_fallback_candidates={metadata['weak_fallback_candidates']} "
            f"fallback_added={fallback_added} displayed={len(public_final)} "
            f"ai_skip_reason={metadata['ai_skip_reason']} "
            f"has_enough={str(has_enough).lower()}"
            + (f' reason="{limited}"' if limited else "")
        ),
        "INFO",
    )

    if len(candidates) >= req.target_count and len(public_final) < req.target_count:
        log(
            "PIPELINE",
            (
                f"target_not_met target={target_display} displayed={len(public_final)} "
                f"accepted_count_before_fallback={metadata['accepted_before_fallback']} "
                f"fallback_candidates_count={metadata['fallback_candidates_count']} "
                f"weak_fallback_candidates_count={metadata['weak_fallback_candidates_count']} "
                f"fallback_added={fallback_added} "
                f"rejected_as_obvious_junk_count={metadata['rejected_as_obvious_junk_count']} "
                f"rejected_reasons_histogram={metadata['rejected_reasons_histogram']} "
                f"reason={metadata.get('why_remaining_products_were_not_displayed')}"
            ),
            "ERROR",
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
    elif not public_final:
        error = "Tidak ada produk setelah filter final."

    return {
        "raw_products": raw_products,
        "normalizer": normalizer,
        "deduped": deduped,
        "budget": budget_result,
        "ai_valid": ai_valid,
        "ranked": ranked,
        "final": public_final,
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

        raw_for_filter, overfetch_meta = await _overfetch_raw_products(
            search_id,
            req,
            run.products,
            run.engine,
            run.raw_products_found,
            eta_calc,
        )
        filtered = await _filter_pipeline(
            search_id,
            req,
            raw_for_filter,
            eta_calc,
            run.engine,
            overfetch_meta=overfetch_meta,
        )
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

    save_result(search_id, {
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
    })
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

    raw_for_filter, overfetch_meta = await _overfetch_raw_products(
        search_id,
        req,
        selection.products,
        selection.selected_engine or "selected",
        raw_target,
        eta_calc,
    )

    filtered = await _filter_pipeline(
        search_id, req, raw_for_filter, eta_calc,
        selection.selected_engine or "selected",
        overfetch_meta=overfetch_meta,
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

    save_result(search_id, {
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
    })

    complete_progress(search_id)
    log(
        f"[{search_id}]",
        f"Done. raw={len(selection.products)} ai={len(filtered['ai_valid'])} "
        f"returned={len(filtered['final'])} ai_status={filtered['ai_status']}",
        "OK",
    )
