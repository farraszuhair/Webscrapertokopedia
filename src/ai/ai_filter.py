"""
Rules-first, intent-aware AI filter.

The core performance rule is simple: deterministic relevance handles obvious
products, and the local LLM only sees borderline cases.
"""
from __future__ import annotations

import asyncio
import contextlib
import math
import time
from dataclasses import dataclass, field
from typing import Any

from src.ai.model_router import get_ai_model
from src.ai.ollama_client import chat_json_async
from src.config import (
    AI_BATCH_SIZE,
    LLM_ACCEPT_THRESHOLD,
    RULE_ACCEPT_THRESHOLD,
    RULE_REJECT_THRESHOLD,
    RULE_REVIEW_THRESHOLD,
)
from src.utils.logger import log


@dataclass
class IntentFilterResult:
    products: list[dict[str, Any]]
    status: str
    meta: dict[str, Any] = field(default_factory=dict)

    def __iter__(self):
        yield self.products
        yield self.status


def _chunks(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [items[i : i + size] for i in range(0, len(items), max(1, size))]


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, parsed))


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.85:
        return "High"
    if confidence >= 0.70:
        return "Medium"
    return "Low"


def _mark_product(
    product: dict[str, Any],
    *,
    accepted: bool,
    confidence: float,
    reason: str,
    source: str,
    query_intent: str,
    product_category: str,
    rule_score: float,
    category_match: str,
) -> dict[str, Any]:
    confidence = max(0.0, min(0.98, float(confidence)))
    product["relevance_score"] = round(confidence, 3)
    product["rule_score"] = round(rule_score, 3)
    product["ai_confidence"] = round(confidence, 3)
    product["ai_model_confidence"] = round(confidence, 3)
    product["ai_confidence_label"] = _confidence_label(confidence)
    product["ai_decision"] = bool(accepted)
    product["ai_label"] = "relevan" if accepted else "tidak_relevan"
    product["ai_reason"] = reason
    product["ai_explanation"] = reason
    product["ai_source"] = source
    product["ai_categories"] = [product_category, category_match, query_intent]
    product["query_intent"] = query_intent
    product["product_category"] = product_category
    product["category_match"] = category_match
    return product


def _build_prompt(query: str, query_intent: str, product: dict[str, Any]) -> str:
    return f"""You are an intent-aware product relevance classifier for marketplace search.

User query:
{query}

Detected query intent:
{query_intent}

Product:
title: {product.get("title", "")}
price: {product.get("price_raw") or product.get("price_text") or product.get("price", "")}
store: {product.get("shop_name") or product.get("shop") or ""}
rating: {product.get("rating") or product.get("rating_text") or ""}
sold: {product.get("sold_count") or product.get("sold") or product.get("sold_text") or ""}

Rules:
- First understand what the user is actually searching for.
- If user searches for a main product, reject accessories and spare parts.
- If user searches for an accessory, accept matching accessories.
- If user searches for a spare part, accept matching spare parts.
- Do not globally reject accessories.
- Reject only when product category does not match query intent.
- Accept semantic matches even if exact words are different.
- For "laptop gaming", accept ASUS ROG, Lenovo Legion, Acer Nitro, MSI, HP Victus, ASUS TUF, RTX/GTX laptops.
- For "casing iphone 13", accept case, casing, softcase, hardcase, MagSafe case for iPhone 13.
- Return JSON only.

JSON format:
{{
  "accepted": true,
  "confidence": 0.0,
  "reason": "...",
  "category_match": "..."
}}
"""


async def _chat_with_progress_heartbeat(
    *,
    prompt: str,
    model: str,
    search_id: str | None,
    batch_current: int,
    batch_total: int,
    batch_started_at_monotonic: float,
    batch_started_at_epoch_ms: int,
    completed_batch_durations: list[float],
    found: int,
    valid_count: int,
) -> dict[str, Any]:
    if not search_id:
        return await chat_json_async(prompt, model=model)

    from src.server.progress import update_ai_eta_progress

    stop_event = asyncio.Event()

    async def heartbeat() -> None:
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                update_ai_eta_progress(
                    search_id=search_id,
                    batch_current=batch_current,
                    batch_total=batch_total,
                    batch_started_at_monotonic=batch_started_at_monotonic,
                    batch_started_at_epoch_ms=batch_started_at_epoch_ms,
                    completed_ai_batch_durations=completed_batch_durations,
                    message=f"AI filtering batch {batch_current}/{batch_total}",
                    found=found,
                    valid=valid_count,
                )

    task = asyncio.create_task(heartbeat())
    try:
        return await chat_json_async(prompt, model=model)
    finally:
        stop_event.set()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def filter_products(
    query: str,
    products: list[dict[str, Any]],
    *,
    use_ai: bool = True,
    search_id: str | None = None,
    ai_mode: str = "balanced",
) -> IntentFilterResult:
    from src.ai.relevance import (
        compute_rule_score,
        detect_product_category,
        detect_query_intent,
        is_obvious_junk_for_intent,
        should_call_llm,
    )

    query_intent = detect_query_intent(query)
    selected_model = get_ai_model(ai_mode)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    borderline: list[dict[str, Any]] = []
    rule_accepted = 0
    rule_rejected = 0

    for product in list(products or []):
        product_category = detect_product_category(product)
        rule_score = compute_rule_score(query, product, query_intent)
        obvious_junk = is_obvious_junk_for_intent(query, product, query_intent)
        product["_rule_context"] = {
            "query_intent": query_intent,
            "product_category": product_category,
            "rule_score": rule_score,
            "obvious_junk": obvious_junk,
        }

        if rule_score >= RULE_ACCEPT_THRESHOLD and not obvious_junk:
            rule_accepted += 1
            accepted.append(_mark_product(
                product,
                accepted=True,
                confidence=rule_score,
                reason=f"Accepted by intent rule ({query_intent} -> {product_category})",
                source="rule_accept",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="rule_match",
            ))
            continue

        if obvious_junk and rule_score < RULE_REJECT_THRESHOLD:
            rule_rejected += 1
            rejected.append(_mark_product(
                product,
                accepted=False,
                confidence=rule_score,
                reason=f"Rejected by intent rule ({product_category} does not match {query_intent})",
                source="rule_reject",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="intent_mismatch",
            ))
            continue

        if use_ai and should_call_llm(rule_score, obvious_junk):
            borderline.append(product)
            continue

        accepted_by_rule_review = rule_score >= RULE_REVIEW_THRESHOLD and not obvious_junk
        target = accepted if accepted_by_rule_review else rejected
        target.append(_mark_product(
            product,
            accepted=accepted_by_rule_review,
            confidence=rule_score,
            reason=(
                "Kept by rule review because AI is disabled"
                if accepted_by_rule_review else
                f"Rejected by low rule score ({rule_score:.2f})"
            ),
            source="rule_review" if accepted_by_rule_review else "rule_low_score",
            query_intent=query_intent,
            product_category=product_category,
            rule_score=rule_score,
            category_match="rule_review" if accepted_by_rule_review else "low_score",
        ))

    if not use_ai or not borderline:
        status = "disabled" if not use_ai else "ok"
        return IntentFilterResult(accepted, status, {
            "query_intent": query_intent,
            "selected_model": None if not use_ai else selected_model,
            "borderline_count": len(borderline),
            "rule_accepted_count": rule_accepted,
            "rule_rejected_count": rule_rejected,
            "llm_checked_count": 0,
            "qwen_accepted_count": 0,
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
        })

    batches = _chunks(borderline, AI_BATCH_SIZE)
    completed_batch_durations: list[float] = []
    llm_checked = 0
    llm_accepted = 0
    llm_failures = 0

    for batch_index, batch in enumerate(batches, 1):
        batch_started = time.perf_counter()
        batch_epoch_ms = int(time.time() * 1000)
        if search_id:
            from src.server.progress import update_ai_eta_progress

            update_ai_eta_progress(
                search_id=search_id,
                batch_current=batch_index,
                batch_total=len(batches),
                batch_started_at_monotonic=batch_started,
                batch_started_at_epoch_ms=batch_epoch_ms,
                completed_ai_batch_durations=completed_batch_durations,
                message=f"AI filtering batch {batch_index}/{len(batches)}",
                found=len(products),
                valid=len(accepted),
            )

        for product in batch:
            ctx = product.get("_rule_context", {})
            product_category = str(ctx.get("product_category") or "unknown")
            rule_score = float(ctx.get("rule_score") or 0.0)
            obvious_junk = bool(ctx.get("obvious_junk"))
            prompt = _build_prompt(query, query_intent, product)
            response = await _chat_with_progress_heartbeat(
                prompt=prompt,
                model=selected_model,
                search_id=search_id,
                batch_current=batch_index,
                batch_total=len(batches),
                batch_started_at_monotonic=batch_started,
                batch_started_at_epoch_ms=batch_epoch_ms,
                completed_batch_durations=completed_batch_durations,
                found=len(products),
                valid_count=len(accepted),
            )
            llm_checked += 1
            fallback_used = bool(response.get("_fallback_used"))
            if fallback_used:
                llm_failures += 1
            ai_confidence = _as_float(response.get("confidence"), 0.5)
            llm_accepts = bool(response.get("accepted", True)) and (
                fallback_used or ai_confidence >= LLM_ACCEPT_THRESHOLD
            ) and not (fallback_used and obvious_junk)
            confidence = max(rule_score, ai_confidence if llm_accepts else min(ai_confidence, rule_score))
            marked = _mark_product(
                product,
                accepted=llm_accepts,
                confidence=confidence,
                reason=str(response.get("reason") or "AI classified product"),
                source="ai_fallback" if fallback_used else "ai_borderline",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match=str(response.get("category_match") or "ai"),
            )
            if llm_accepts:
                llm_accepted += 1
                accepted.append(marked)
            else:
                rejected.append(marked)

        completed_batch_durations.append(time.perf_counter() - batch_started)
        if search_id:
            from src.server.progress import update_ai_eta_progress

            update_ai_eta_progress(
                search_id=search_id,
                batch_current=batch_index,
                batch_total=len(batches),
                batch_started_at_monotonic=batch_started,
                batch_started_at_epoch_ms=batch_epoch_ms,
                completed_ai_batch_durations=completed_batch_durations,
                message=f"AI filtering batch {batch_index}/{len(batches)} done",
                found=len(products),
                valid=len(accepted),
                batch_done=True,
            )

    if not accepted:
        rescue = [
            p for p in rejected
            if float(p.get("rule_score") or 0) >= RULE_REVIEW_THRESHOLD
            and p.get("category_match") != "intent_mismatch"
        ]
        accepted.extend(sorted(rescue, key=lambda p: float(p.get("rule_score") or 0), reverse=True)[:10])

    if llm_failures and llm_failures == llm_checked:
        status = "unavailable"
    elif llm_failures:
        status = "partial"
    else:
        status = "ok"

    warning = ""
    if llm_failures:
        warning = "AI model failed for some borderline products; fallback kept usable candidates."

    meta = {
        "query_intent": query_intent,
        "selected_model": selected_model,
        "borderline_count": len(borderline),
        "batch_count": len(batches),
        "rule_accepted_count": rule_accepted,
        "rule_rejected_count": rule_rejected,
        "llm_checked_count": llm_checked,
        "llm_accepted_count": llm_accepted,
        "qwen_accepted_count": llm_accepted,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "fallback_used": llm_failures > 0,
        "warning": warning,
        "thresholds": {
            "rule_accept": RULE_ACCEPT_THRESHOLD,
            "rule_review": RULE_REVIEW_THRESHOLD,
            "rule_reject": RULE_REJECT_THRESHOLD,
            "llm_accept": LLM_ACCEPT_THRESHOLD,
        },
    }
    log("AI", f"intent={query_intent} rule={rule_accepted} llm={llm_checked} accepted={len(accepted)}", "OK")
    return IntentFilterResult(accepted, status, meta)
