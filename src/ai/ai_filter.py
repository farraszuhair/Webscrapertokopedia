"""
Rules-first, intent-aware AI filter.

The core performance rule is simple: deterministic relevance handles obvious
products, and the local LLM only sees borderline cases.
"""
from __future__ import annotations

import contextlib
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable
import asyncio

from src.ai.ai_orchestrator import classify_borderline_product
from src.ai.model_registry import get_orchestrator_status
from src.config import (
    AI_BATCH_SIZE,
    AI_CLASSIFIER_MAX_PRODUCTS,
    AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK,
    FALLBACK_EXPANSION_THRESHOLD,
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


def _as_number(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


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
    product["confidence"] = round(confidence, 3)
    product["rule_score"] = round(rule_score, 3)
    product["ai_confidence"] = round(confidence, 3)
    product["ai_model_confidence"] = round(confidence, 3)
    product["ai_confidence_label"] = _confidence_label(confidence)
    product["ai_decision"] = bool(accepted)
    product["ai_label"] = "relevan" if accepted else "tidak_relevan"
    product["ai_reason"] = reason
    product["reason"] = reason
    product["ai_explanation"] = reason
    product["ai_source"] = source
    product["decision_source"] = source
    product["ai_categories"] = [product_category, category_match, query_intent]
    product["query_intent"] = query_intent
    product["product_category"] = product_category
    product["category_match"] = category_match
    return product


def combine_rule_and_semantic_score(rule_score: float, semantic_score: float | None) -> float:
    if semantic_score is None:
        return rule_score
    return round(max(rule_score, rule_score * 0.70 + semantic_score * 0.30), 3)


def _product_key(product: dict[str, Any]) -> str:
    return str(product.get("id") or product.get("url") or product.get("product_url") or product.get("title") or "")


def _decision_priority(product: dict[str, Any]) -> int:
    priority = {
        "ai_orchestrator": 0,
        "rule_accept": 1,
        "fallback_expansion": 2,
        "fallback_after_ai_reject": 3,
        "fallback_ai_timeout": 4,
        "fallback_ai_circuit_open": 5,
        "fallback_not_classified_cpu_limit": 6,
    }
    return priority.get(str(product.get("decision_source") or product.get("ai_source") or ""), 9)


def _rank_final_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        products,
        key=lambda product: (
            -_as_number(product.get("confidence", product.get("relevance_score", product.get("ai_confidence", 0)))),
            _decision_priority(product),
            -_as_number(product.get("rating")),
            -_as_number(product.get("sold_count")),
            _price_sort_value(product),
        ),
    )


def _price_sort_value(product: dict[str, Any]) -> float:
    price = _as_number(product.get("price_value", product.get("price")), 0.0)
    return price if price > 0 else float("inf")


def _sort_fallback_candidates(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        products,
        key=lambda product: (
            -_as_number(product.get("confidence", product.get("relevance_score", product.get("ai_confidence", 0)))),
            -_as_number(product.get("rule_score", (product.get("_rule_context") or {}).get("rule_score"))),
            -_as_number(product.get("semantic_score", (product.get("_rule_context") or {}).get("semantic_score"))),
            -_as_number(product.get("rating")),
            -_as_number(product.get("sold_count")),
            _price_sort_value(product),
        ),
    )


def _sort_borderline_candidates(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        products,
        key=lambda product: (
            -_as_number(product.get("rule_score", (product.get("_rule_context") or {}).get("rule_score"))),
            -_as_number(product.get("semantic_score", (product.get("_rule_context") or {}).get("semantic_score"))),
            -_as_number(product.get("rating")),
            -_as_number(product.get("sold_count")),
            _price_sort_value(product),
        ),
    )


async def _run_with_ai_heartbeat(
    *,
    coro: Awaitable[dict[str, Any]],
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
        return await coro

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
        return await coro
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
) -> IntentFilterResult:
    from src.ai.relevance import (
        compute_rule_score,
        detect_product_category,
        detect_query_intent,
        is_obvious_junk_for_intent,
        is_obvious_match_for_intent,
    )

    query_intent = detect_query_intent(query)
    orchestrator_status = get_orchestrator_status()
    selected_model = orchestrator_status.get("classifier")
    classifier_installed = bool(selected_model)
    target_count = int(products[0].get("_requested_target", 50) or 50) if products else 50
    target_display = min(target_count, len(products or []))
    
    log(
        "AI_ORCH",
        (
            f"ai_orchestrator_enabled={use_ai} "
            f"supported_models={orchestrator_status.get('supported', [])} "
            f"missing_models={orchestrator_status.get('missing', [])} "
            f"selected_classifier={selected_model or 'rules_only'} "
            f"semantic_enabled={bool(orchestrator_status.get('capabilities', {}).get('semantic'))} "
            f"json_repair_enabled={bool(orchestrator_status.get('capabilities', {}).get('json_repair'))}"
        ),
        "INFO",
    )
    
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    borderline: list[dict[str, Any]] = []
    fallback_candidates: list[dict[str, Any]] = []
    rule_accepted = 0
    rule_rejected = 0
    semantic_checked = 0
    classifier_checked = 0
    ai_accepted = 0
    ai_rejected = 0
    ai_fallback = 0
    ai_calls_attempted = 0
    ai_calls_succeeded = 0
    ai_timeouts = 0
    ai_failure_count = 0
    ai_circuit_open = False
    ai_circuit_reason: str | None = None

    query_embedding = None
    semantic_enabled = bool(orchestrator_status.get("capabilities", {}).get("semantic"))
    if semantic_enabled:
        try:
            from src.ai.ollama_client import get_embedding_async
            query_embedding = await get_embedding_async(query)
        except Exception:
            query_embedding = None
            semantic_enabled = False

    for product in list(products or []):
        product_category = detect_product_category(product)
        rule_score = compute_rule_score(query, product, query_intent)
        semantic_score = None
        
        if (
            semantic_enabled
            and query_embedding
            and str(product.get("title") or "").strip()
        ):
            try:
                from src.ai.ollama_client import cosine_similarity, get_embedding_async
                title_embedding = await get_embedding_async(str(product.get("title") or ""))
                semantic_score = cosine_similarity(query_embedding, title_embedding)
                if semantic_score is not None:
                    semantic_checked += 1
                    product["semantic_score"] = round(semantic_score, 3)
                    rule_score = combine_rule_and_semantic_score(rule_score, semantic_score)
            except Exception:
                semantic_score = None

        obvious_junk = is_obvious_junk_for_intent(query, product, query_intent)
                
        product["_rule_context"] = {
            "query_intent": query_intent,
            "product_category": product_category,
            "rule_score": rule_score,
            "semantic_score": semantic_score,
            "obvious_junk": obvious_junk,
        }

        obvious_match = is_obvious_match_for_intent(query, product, query_intent)
        if obvious_match or (rule_score >= RULE_ACCEPT_THRESHOLD and not obvious_junk):
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

        if use_ai and classifier_installed and rule_score >= RULE_REVIEW_THRESHOLD:
            borderline.append(product)
            continue

        if _is_safe_fallback_candidate(product, rule_score, obvious_junk):
            product["rule_score"] = round(rule_score, 3)
            product["decision_source"] = "fallback_candidate"
            fallback_candidates.append(product)
            continue

        rejected.append(_mark_product(
            product,
            accepted=False,
            confidence=rule_score,
            reason=f"Rejected by low rule score ({rule_score:.2f})",
            source="rule_low_score",
            query_intent=query_intent,
            product_category=product_category,
            rule_score=rule_score,
            category_match="low_score",
        ))

    def apply_fallback_expansion() -> int:
        expanded = 0
        if len(accepted) >= target_display:
            return 0
        seen_ids = {_product_key(p) for p in accepted}

        unique_candidates: list[dict[str, Any]] = []
        candidate_keys = set()
        for p in fallback_candidates:
            key = _product_key(p)
            if key in seen_ids or key in candidate_keys:
                continue
            candidate_keys.add(key)
            unique_candidates.append(p)

        unique_candidates = _sort_fallback_candidates(unique_candidates)

        for product in unique_candidates:
            if len(accepted) >= target_display:
                break
            ctx = product.get("_rule_context") or {}
            score = float(ctx.get("rule_score") or product.get("rule_score") or FALLBACK_EXPANSION_THRESHOLD)
            semantic = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
            existing_confidence = _as_number(product.get("confidence", product.get("relevance_score", product.get("ai_confidence", 0))), 0.0)
            if is_obvious_junk_for_intent(query, product, query_intent):
                continue
            product_category = str(ctx.get("product_category") or detect_product_category(product))
            source = str(product.get("decision_source") or "fallback_expansion")
            marked = _mark_product(
                product,
                accepted=True,
                confidence=max(existing_confidence, score, semantic, 0.35),
                reason=str(product.get("reason") or product.get("ai_reason") or "Included by fallback expansion to approach requested count"),
                source=source,
                query_intent=query_intent,
                product_category=product_category,
                rule_score=score,
                category_match="fallback_expansion",
            )
            accepted.append(marked)
            seen_ids.add(_product_key(product))
            expanded += 1
        
        return expanded

    def _ai_skip_reason(checked: int) -> str | None:
        if ai_circuit_open:
            return ai_circuit_reason or "AI classifier circuit breaker opened after repeated timeouts"
        if checked:
            return None
        if not use_ai:
            return "AI disabled"
        if not classifier_installed:
            return "No supported classifier installed"
        if not products:
            return "Candidate pool empty"
        if not borderline:
            return "No borderline candidates"
        return "Classifier path not reached"

    def _warning_text(fallback_expanded: int) -> str:
        warnings: list[str] = []
        budget_valid = int(products[0].get("_budget_valid", len(products)) or 0) if products else 0
        if budget_valid and budget_valid < target_count:
            warnings.append(f"Diminta {target_count}, tetapi hanya {budget_valid} kandidat sesuai budget.")
        if ai_timeouts > 0:
            warnings.append(f"AI lokal timeout pada {ai_timeouts} produk, beberapa hasil diisi dari fallback aman.")
        if fallback_expanded:
            warnings.append(f"{fallback_expanded} produk fallback ditambahkan agar hasil mendekati target.")
        return " ".join(dict.fromkeys(warnings))

    def _build_meta(
        *,
        status: str,
        checked: int,
        accepted_by_classifier: int,
        rejected_by_classifier: int,
        fallback_by_classifier: int,
        fallback_expanded: int,
        warning: str,
    ) -> dict[str, Any]:
        displayed = min(len(accepted), target_display)
        return {
            "requested": target_count,
            "requested_count": target_count,
            "scraped_raw": products[0].get("_scraped_raw", 0) if products else 0,
            "raw_scraped": products[0].get("_scraped_raw", 0) if products else 0,
            "raw_scraped_count": products[0].get("_scraped_raw", 0) if products else 0,
            "after_dedupe": products[0].get("_after_dedupe", 0) if products else 0,
            "deduped_count": products[0].get("_after_dedupe", 0) if products else 0,
            "budget_valid": products[0].get("_budget_valid", 0) if products else 0,
            "budget_valid_count": products[0].get("_budget_valid", 0) if products else 0,
            "candidate_pool": len(products),
            "ai_input_count": len(products),
            "query_intent": query_intent,
            "selected_model": selected_model if use_ai else None,
            "ai_status": status,
            "ai_orchestrator": orchestrator_status,
            "borderline_candidates": len(borderline),
            "borderline_count": len(borderline),
            "rule_accepted": rule_accepted,
            "rule_accepted_count": rule_accepted,
            "rule_rejected": rule_rejected,
            "rule_rejected_count": rule_rejected,
            "semantic_checked_count": semantic_checked,
            "semantic_checked": semantic_checked,
            "classifier_checked": checked,
            "ai_checked": checked,
            "llm_checked_count": checked,
            "classifier_limit": AI_CLASSIFIER_MAX_PRODUCTS,
            "ai_calls_attempted": ai_calls_attempted,
            "ai_calls_succeeded": ai_calls_succeeded,
            "ai_timeouts": ai_timeouts,
            "ai_circuit_open": ai_circuit_open,
            "ai_accepted": accepted_by_classifier,
            "ai_accepted_count": accepted_by_classifier,
            "ai_rejected": rejected_by_classifier,
            "ai_fallback": fallback_by_classifier,
            "fallback_added": fallback_expanded,
            "fallback_expansion_count": fallback_expanded,
            "displayed": displayed,
            "displayed_count": displayed,
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "fallback_used": fallback_by_classifier > 0,
            "warning": warning,
            "thresholds": {
                "rule_accept": RULE_ACCEPT_THRESHOLD,
                "rule_review": RULE_REVIEW_THRESHOLD,
                "rule_reject": RULE_REJECT_THRESHOLD,
                "fallback_expansion": FALLBACK_EXPANSION_THRESHOLD,
                "llm_accept": LLM_ACCEPT_THRESHOLD,
            },
            "ai_skip_reason": _ai_skip_reason(checked),
        }

    if not borderline:
        fallback_expanded = apply_fallback_expansion()
        warning = _warning_text(fallback_expanded)
        status = "disabled" if not use_ai else ("unavailable" if not classifier_installed else "ok")
        log(
            "AI",
            (
                f"raw={len(products)} target_display={target_display} intent={query_intent} "
                f"classifier_installed={classifier_installed} selected_classifier={selected_model or 'none'} "
                f"classifier_limit={AI_CLASSIFIER_MAX_PRODUCTS} "
                f"rule_accept={rule_accepted} rule_reject={rule_rejected} semantic_checked={semantic_checked} "
                f"borderline_candidates=0 classifier_checked=0 ai_calls_attempted=0 "
                f"ai_timeouts=0 ai_circuit_open=false "
                f"fallback_candidates={len(fallback_candidates)} fallback_added={fallback_expanded} final_displayed={len(accepted)} "
                f"ai_skip_reason={_ai_skip_reason(0)}"
            ),
            "OK",
        )
        meta = _build_meta(
            status=status,
            checked=0,
            accepted_by_classifier=0,
            rejected_by_classifier=0,
            fallback_by_classifier=0,
            fallback_expanded=fallback_expanded,
            warning=warning,
        )
        return IntentFilterResult(_rank_final_products(accepted)[:target_display], status, meta)

    borderline = _sort_borderline_candidates(borderline)
    to_classify = borderline[:AI_CLASSIFIER_MAX_PRODUCTS]
    not_classified = borderline[AI_CLASSIFIER_MAX_PRODUCTS:]
    for product in not_classified:
        ctx = product.get("_rule_context", {})
        rule_score = float(ctx.get("rule_score") or product.get("rule_score") or 0.0)
        obvious_junk = bool(ctx.get("obvious_junk"))
        if _is_safe_fallback_candidate(product, rule_score, obvious_junk):
            product["rule_score"] = round(rule_score, 3)
            product["decision_source"] = "fallback_not_classified_cpu_limit"
            product["reason"] = "Classifier limit reached, included as fallback candidate"
            fallback_candidates.append(product)

    batches = _chunks(to_classify, AI_BATCH_SIZE)
    completed_batch_durations: list[float] = []
    log(
        "AI_ORCH",
        (
            f"borderline_candidates={len(borderline)} classifier_limit={AI_CLASSIFIER_MAX_PRODUCTS} "
            f"classifier_selected={len(to_classify)} skipped_by_limit={len(not_classified)} batches={len(batches)}"
        ),
        "INFO",
    )

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
            semantic_score = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
            obvious_junk = bool(ctx.get("obvious_junk"))

            if ai_circuit_open:
                if _is_safe_fallback_candidate(product, rule_score, obvious_junk):
                    product["rule_score"] = round(rule_score, 3)
                    product["confidence"] = round(max(rule_score, semantic_score, 0.35), 3)
                    product["decision_source"] = "fallback_ai_circuit_open"
                    product["reason"] = "AI circuit breaker opened, included as fallback candidate"
                    fallback_candidates.append(product)
                continue
            
            classifier_checked += 1
            ai_calls_attempted += 1
            response = await _run_with_ai_heartbeat(
                coro=classify_borderline_product(
                    query,
                    query_intent,
                    product,
                    rule_score,
                    status=orchestrator_status,
                    ai_enabled=use_ai,
                ),
                search_id=search_id,
                batch_current=batch_index,
                batch_total=len(batches),
                batch_started_at_monotonic=batch_started,
                batch_started_at_epoch_ms=batch_epoch_ms,
                completed_batch_durations=completed_batch_durations,
                found=len(products),
                valid_count=len(accepted),
            )
            
            if response.get("_chat_ok"):
                ai_calls_succeeded += 1
            fallback_used = bool(response.get("_fallback_used"))
            timed_out = bool(response.get("_timeout"))
            failed = fallback_used or not bool(response.get("_chat_ok"))
            if fallback_used:
                ai_fallback += 1
            if timed_out:
                ai_timeouts += 1
            if failed:
                ai_failure_count += 1
                if ai_failure_count >= AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK and not ai_circuit_open:
                    ai_circuit_open = True
                    ai_circuit_reason = "AI classifier circuit breaker opened after repeated timeouts"
                    log(
                        "AI_ORCH",
                        f"circuit_open failures={ai_failure_count} reason={'timeout' if timed_out else 'classifier_error'}",
                        "WARN",
                    )

            ai_confidence = _as_float(response.get("confidence"), 0.5)
            if fallback_used:
                if _is_safe_fallback_candidate(product, rule_score, obvious_junk):
                    product["rule_score"] = round(rule_score, 3)
                    product["semantic_score"] = round(semantic_score, 3) if semantic_score else product.get("semantic_score")
                    product["confidence"] = round(max(rule_score, semantic_score, 0.35), 3)
                    product["decision_source"] = "fallback_ai_timeout" if timed_out else "ai_fallback"
                    product["reason"] = "AI timeout, included as fallback candidate" if timed_out else str(response.get("reason") or "Classifier unavailable, included as fallback candidate")
                    fallback_candidates.append(product)
                else:
                    rejected.append(_mark_product(
                        product,
                        accepted=False,
                        confidence=rule_score,
                        reason="AI fallback skipped because product is obvious junk",
                        source="ai_fallback_reject",
                        query_intent=query_intent,
                        product_category=product_category,
                        rule_score=rule_score,
                        category_match="fallback_reject",
                    ))
                continue

            llm_accepts = bool(response.get("accepted", True)) and (
                ai_confidence >= LLM_ACCEPT_THRESHOLD
            )
            
            confidence = max(rule_score, ai_confidence if llm_accepts else min(ai_confidence, rule_score))
            marked = _mark_product(
                product,
                accepted=llm_accepts,
                confidence=confidence,
                reason=str(response.get("reason") or "AI classified product"),
                source=str(response.get("decision_source") or ("ai_fallback" if fallback_used else "ai_classifier")),
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match=str(response.get("category_match") or "ai"),
            )
            if llm_accepts:
                ai_accepted += 1
                accepted.append(marked)
            else:
                ai_rejected += 1
                marked["decision_source"] = "ai_reject"
                marked["ai_source"] = "ai_reject"
                if _is_safe_fallback_candidate(marked, rule_score, obvious_junk):
                    marked["decision_source"] = "fallback_after_ai_reject"
                    marked["rule_score"] = round(rule_score, 3)
                    fallback_candidates.append(marked)
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

    fallback_expanded = apply_fallback_expansion()

    if ai_circuit_open:
        status = "partial"
    elif ai_fallback and ai_fallback == classifier_checked:
        status = "unavailable"
    elif ai_fallback:
        status = "partial"
    else:
        status = "ok"

    warning = _warning_text(fallback_expanded)
    if borderline and classifier_checked == 0:
        log("AI_ORCH", "AI classifier integration failure: borderline products exist but /api/chat was not called", "ERROR")

    meta = _build_meta(
        status=status,
        checked=classifier_checked,
        accepted_by_classifier=ai_accepted,
        rejected_by_classifier=ai_rejected,
        fallback_by_classifier=ai_fallback,
        fallback_expanded=fallback_expanded,
        warning=warning,
    )
    meta["batch_count"] = len(batches)
    
    log(
        "AI",
        (
            f"raw={len(products)} target_display={target_display} intent={query_intent} "
            f"classifier_installed={classifier_installed} selected_classifier={selected_model or 'none'} "
            f"classifier_limit={AI_CLASSIFIER_MAX_PRODUCTS} "
            f"rule_accept={rule_accepted} rule_reject={rule_rejected} semantic_checked={semantic_checked} "
            f"borderline_candidates={len(borderline)} classifier_checked={classifier_checked} "
            f"ai_calls_attempted={ai_calls_attempted} ai_calls_succeeded={ai_calls_succeeded} "
            f"ai_timeouts={ai_timeouts} ai_circuit_open={str(ai_circuit_open).lower()} "
            f"ai_accepted={ai_accepted} ai_rejected={ai_rejected} ai_fallback={ai_fallback} "
            f"fallback_candidates={len(fallback_candidates)} fallback_added={fallback_expanded} final_displayed={len(accepted)}"
        ),
        "OK",
    )
    return IntentFilterResult(_rank_final_products(accepted)[:target_display], status, meta)


def _is_safe_fallback_candidate(product: dict[str, Any], rule_score: float, obvious_junk: bool) -> bool:
    if obvious_junk or rule_score < FALLBACK_EXPANSION_THRESHOLD:
        return False
    title = str(product.get("title") or "").strip()
    if not title:
        return False
    price = product.get("price_value", product.get("price"))
    try:
        return int(price or 0) > 0
    except (TypeError, ValueError):
        return False
