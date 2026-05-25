"""
Rules-first, intent-aware AI filter.

The core performance rule is simple: deterministic relevance handles obvious
products, and the local LLM only sees borderline cases.
"""
from __future__ import annotations

import contextlib
import json
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable
import asyncio

from src.ai.ai_orchestrator import classify_borderline_product
from src.ai.model_registry import get_best_classifier_model, get_orchestrator_status
from src.config import (
    AI_BATCH_SIZE,
    AI_CHAT_TIMEOUT_SECONDS,
    AI_CLASSIFIER_MAX_PRODUCTS,
    AI_CPU_MODE,
    AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK,
    FALLBACK_EXPANSION_THRESHOLD,
    LLM_ACCEPT_THRESHOLD,
    RULE_ACCEPT_THRESHOLD,
    RULE_REJECT_THRESHOLD,
    RULE_REVIEW_THRESHOLD,
    WEAK_FALLBACK_THRESHOLD,
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
    combined_score: float | None = None,
) -> dict[str, Any]:
    confidence = max(0.0, min(0.98, float(confidence)))
    product["relevance_score"] = round(confidence, 3)
    product["confidence"] = round(confidence, 3)
    product["rule_score"] = round(rule_score, 3)
    product["combined_score"] = round(combined_score if combined_score is not None else confidence, 3)
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
    return round(max(rule_score, semantic_score * 0.85), 3)


def _product_key(product: dict[str, Any]) -> str:
    return str(product.get("id") or product.get("url") or product.get("product_url") or product.get("title") or "")


def _decision_priority(product: dict[str, Any]) -> int:
    priority = {
        "ai_orchestrator": 0,
        "rule_accept": 1,
        "fallback_expansion": 2,
        "fallback_after_ai_reject": 3,
        "fallback_after_ai_reject_positive_laptop": 3,
        "rescued_false_obvious_junk": 3,
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
            -_as_number(product.get("combined_score", (product.get("_rule_context") or {}).get("combined_score"))),
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
            -_as_number(product.get("combined_score", (product.get("_rule_context") or {}).get("combined_score"))),
            -_as_number(product.get("rule_score", (product.get("_rule_context") or {}).get("rule_score"))),
            -_as_number(product.get("semantic_score", (product.get("_rule_context") or {}).get("semantic_score"))),
            -_as_number(product.get("rating")),
            -_as_number(product.get("sold_count")),
            _price_sort_value(product),
        ),
    )


def _product_price_value(product: dict[str, Any]) -> int:
    price = product.get("price_value", product.get("price"))
    try:
        return int(price or 0)
    except (TypeError, ValueError):
        return 0


def _is_valid_product(product: dict[str, Any]) -> bool:
    title = str(product.get("title") or product.get("name") or "").strip()
    if len(title) < 3:
        return False
    identifier = str(product.get("id") or product.get("url") or product.get("product_url") or "").strip()
    if identifier:
        return True
    return _product_price_value(product) > 0


def _debug_sample(product: dict[str, Any]) -> dict[str, Any]:
    ctx = product.get("_rule_context") or {}
    return {
        "id": product.get("id"),
        "title": product.get("title"),
        "price_value": product.get("price_value", product.get("price")),
        "url": product.get("url") or product.get("product_url"),
        "decision_source": product.get("decision_source") or product.get("ai_source"),
        "reason": product.get("reason") or product.get("ai_reason"),
        "rule_score": product.get("rule_score", ctx.get("rule_score")),
        "semantic_score": product.get("semantic_score", ctx.get("semantic_score")),
        "base_combined_score": product.get("base_combined_score", ctx.get("base_combined_score")),
        "constraint_penalty": product.get("constraint_penalty", ctx.get("constraint_penalty")),
        "combined_score": product.get("combined_score", ctx.get("combined_score")),
        "query_constraints": product.get("query_constraints", ctx.get("query_constraints")),
        "product_constraints": product.get("product_constraints", ctx.get("product_constraints")),
        "constraint_mismatch_reasons": product.get(
            "constraint_mismatch_reasons",
            ctx.get("constraint_mismatch_reasons", []),
        ),
        "learned_adjustment": product.get("learned_adjustment", ctx.get("learned_adjustment", 0.0)),
        "learned_matches": product.get("learned_matches", ctx.get("learned_matches", [])),
    }


def _write_latest_pipeline_debug(payload: dict[str, Any]) -> None:
    try:
        output_dir = Path("debug") / "pipeline"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "latest_search_debug.json"
        output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2, default=str), encoding="utf-8")
    except Exception as exc:
        log("PIPELINE", f"failed_to_write_debug_json error={exc}", "WARN")


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
        apply_laptop_gaming_boost,
        compute_rule_score,
        detect_product_category,
        detect_query_intent,
        has_gaming_laptop_evidence,
        is_obvious_junk_for_intent,
        is_obvious_match_for_intent,
        is_laptop_gaming_query,
    )
    from src.ai.feedback_store import (
        compute_constraint_mismatch_penalty,
        compute_learned_adjustment,
        extract_query_constraints,
        load_feedback_context,
        load_learned_patterns,
    )

    query_intent = detect_query_intent(query)
    query_constraints = extract_query_constraints(query)
    learned_patterns = load_learned_patterns(query, query_intent, query_constraints, limit=200)
    feedback_context = load_feedback_context(query, query_intent, query_constraints, limit=12)
    feedback_examples_loaded = int(feedback_context.get("feedback_examples_loaded", 0) or 0)
    learned_patterns_loaded = len(learned_patterns)
    query_scoped_patterns = sum(1 for p in learned_patterns if p.get("scope") == "exact_query")
    constraint_scoped_patterns = sum(1 for p in learned_patterns if p.get("scope") == "query_constraint")
    intent_scoped_patterns = sum(1 for p in learned_patterns if p.get("scope") == "query_intent")
    global_patterns = sum(1 for p in learned_patterns if p.get("scope") == "global")
    orchestrator_status = get_orchestrator_status()
    installed_models = orchestrator_status.get("installed")
    selected_model = orchestrator_status.get("classifier") or get_best_classifier_model(
        installed_models if installed_models is not None else None
    )
    classifier_installed = bool(selected_model)
    target_count = int(products[0].get("_requested_target", 50) or 50) if products else 50
    target_display = min(target_count, len(products or []))
    
    log(
        "AI_ORCH",
        (
            f"ai_orchestrator_enabled={use_ai} "
            f"supported_models={orchestrator_status.get('supported', [])} "
            f"missing_models={orchestrator_status.get('missing', [])} "
            f"classifier={selected_model or 'rules_only'} "
            f"semantic_enabled={bool(orchestrator_status.get('capabilities', {}).get('semantic'))} "
            f"json_repair_enabled={bool(orchestrator_status.get('capabilities', {}).get('json_repair'))}"
        ),
        "INFO",
    )
    log("AI_ORCH", f"ai_enabled={bool(use_ai)}", "INFO")
    log("AI_ORCH", f"installed_models={orchestrator_status.get('installed', [])}", "INFO")
    log(
        "AI_ORCH",
        (
            f"selected_classifier={selected_model or 'none'} "
            f"cpu_mode={str(AI_CPU_MODE).lower()} "
            f"max_products={AI_CLASSIFIER_MAX_PRODUCTS} "
            f"timeout={AI_CHAT_TIMEOUT_SECONDS}"
        ),
        "INFO",
    )
    log(
        "AI_LEARN",
        (
            f"feedback_examples_loaded={feedback_examples_loaded} "
            f"learned_patterns_loaded={learned_patterns_loaded} "
            f"query_scoped_patterns={query_scoped_patterns} "
            f"constraint_scoped_patterns={constraint_scoped_patterns} "
            f"global_patterns={global_patterns}"
        ),
        "INFO",
    )
    
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    borderline: list[dict[str, Any]] = []
    fallback_candidates: list[dict[str, Any]] = []
    weak_fallback_candidates: list[dict[str, Any]] = []
    accepted_before_fallback = 0
    rule_accepted = 0
    rule_rejected = 0
    rejected_as_obvious_junk_count = 0
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
    ai_skip_reason_override: str | None = None
    fallback_rejected_as_junk = 0
    rejected_reasons_histogram: Counter[str] = Counter()
    rejected_as_obvious_junk_count_before_rescue = 0
    rescued_false_obvious_junk_count = 0
    constraint_mismatch_products = 0
    learning_adjusted_products = 0
    learned_positive_matches = 0
    learned_negative_matches = 0

    def record_rejection(reason: str, product: dict[str, Any]) -> None:
        rejected_reasons_histogram[reason] += 1
        product["reject_reason"] = reason

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
        product_constraints = extract_query_constraints(str(product.get("title") or product.get("name") or ""))
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
            except Exception:
                semantic_score = None

        combined_score = combine_rule_and_semantic_score(rule_score, semantic_score)
        combined_score = apply_laptop_gaming_boost(query, product, combined_score)
        base_combined_score = combined_score
        constraint_penalty, constraint_reasons = compute_constraint_mismatch_penalty(
            query_constraints,
            product_constraints,
        )
        learned_adjustment, learned_matches = compute_learned_adjustment(
            query,
            query_intent,
            query_constraints,
            product,
            learned_patterns,
        )
        if constraint_reasons:
            constraint_mismatch_products += 1
        if abs(learned_adjustment) > 0.0001:
            learning_adjusted_products += 1
        if any(float(match.get("weight", 0) or 0) > 0 for match in learned_matches):
            learned_positive_matches += 1
        if any(float(match.get("weight", 0) or 0) < 0 for match in learned_matches):
            learned_negative_matches += 1
        combined_score = round(max(0.0, min(1.0, combined_score + constraint_penalty + learned_adjustment)), 3)
        positive_laptop_evidence = is_laptop_gaming_query(query) and has_gaming_laptop_evidence(str(product.get("title") or ""))
        obvious_junk = is_obvious_junk_for_intent(query, product, query_intent)
        if positive_laptop_evidence:
            obvious_junk = False
                
        product["_rule_context"] = {
            "query_intent": query_intent,
            "product_category": product_category,
            "rule_score": rule_score,
            "semantic_score": semantic_score,
            "base_combined_score": base_combined_score,
            "constraint_penalty": constraint_penalty,
            "constraint_mismatch_reasons": constraint_reasons,
            "learned_adjustment": learned_adjustment,
            "learned_matches": learned_matches,
            "combined_score": combined_score,
            "obvious_junk": obvious_junk,
            "positive_laptop_evidence": positive_laptop_evidence,
            "query_constraints": query_constraints,
            "product_constraints": product_constraints,
        }
        product["rule_score"] = round(rule_score, 3)
        product["base_combined_score"] = round(base_combined_score, 3)
        product["constraint_penalty"] = round(constraint_penalty, 3)
        product["constraint_mismatch_reasons"] = constraint_reasons
        product["query_constraints"] = query_constraints
        product["product_constraints"] = product_constraints
        product["learned_adjustment"] = round(learned_adjustment, 3)
        product["learned_matches"] = learned_matches
        product["combined_score"] = round(combined_score, 3)

        obvious_match = is_obvious_match_for_intent(query, product, query_intent)
        if obvious_match or (combined_score >= RULE_ACCEPT_THRESHOLD and not obvious_junk):
            rule_accepted += 1
            accepted.append(_mark_product(
                product,
                accepted=True,
                confidence=combined_score,
                reason=f"Accepted by intent rule ({query_intent} -> {product_category})",
                source="rule_accept",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="rule_match",
                combined_score=combined_score,
            ))
            continue

        if obvious_junk and combined_score < RULE_REJECT_THRESHOLD:
            log("REJECT", f'reason=obvious_junk title="{str(product.get("title") or "")[:180]}" positive_laptop_evidence={str(positive_laptop_evidence).lower()}', "WARN")
            rule_rejected += 1
            rejected_as_obvious_junk_count += 1
            record_rejection("obvious_junk", product)
            rejected.append(_mark_product(
                product,
                accepted=False,
                confidence=combined_score,
                reason=f"Rejected by intent rule ({product_category} does not match {query_intent})",
                source="rule_reject",
                query_intent=query_intent,
                product_category=product_category,
                rule_score=rule_score,
                category_match="intent_mismatch",
                combined_score=combined_score,
            ))
            continue

        if combined_score >= RULE_REVIEW_THRESHOLD and not obvious_junk:
            product["decision_source"] = "borderline_candidate"
            product["confidence"] = round(max(combined_score, rule_score, semantic_score or 0.0), 3)
            borderline.append(product)
            continue

        if _is_valid_product(product) and not obvious_junk:
            product["rule_score"] = round(rule_score, 3)
            product["combined_score"] = round(combined_score, 3)
            product["confidence"] = round(max(combined_score, rule_score, semantic_score or 0.0), 3)
            if semantic_score is not None:
                product["semantic_score"] = round(semantic_score, 3)
            if combined_score >= FALLBACK_EXPANSION_THRESHOLD:
                product["decision_source"] = "fallback_candidate"
                fallback_candidates.append(product)
            else:
                product["decision_source"] = "weak_fallback_candidate"
                product["reason"] = "Weak fallback candidate; not obvious junk"
                weak_fallback_candidates.append(product)
            continue

        reject_reason = "obvious_junk" if obvious_junk else "invalid_product_data"
        if obvious_junk:
            log("REJECT", f'reason=obvious_junk title="{str(product.get("title") or "")[:180]}" positive_laptop_evidence={str(positive_laptop_evidence).lower()}', "WARN")
            rejected_as_obvious_junk_count += 1
        record_rejection(reject_reason, product)
        rejected.append(_mark_product(
            product,
            accepted=False,
            confidence=combined_score,
            reason=f"Rejected by {reject_reason.replace('_', ' ')}",
            source="rule_reject" if obvious_junk else "rule_invalid",
            query_intent=query_intent,
            product_category=product_category,
            rule_score=rule_score,
            category_match=reject_reason,
            combined_score=combined_score,
        ))

    rejected_as_obvious_junk_count_before_rescue = rejected_as_obvious_junk_count
    rescued_false_junk: list[dict[str, Any]] = []
    remaining_rejected: list[dict[str, Any]] = []
    for product in rejected:
        if (
            product.get("reject_reason") == "obvious_junk"
            and is_laptop_gaming_query(query)
            and has_gaming_laptop_evidence(str(product.get("title") or ""))
        ):
            product["decision_source"] = "rescued_false_obvious_junk"
            product["ai_source"] = "rescued_false_obvious_junk"
            product["reason"] = "Rescued because title has valid gaming laptop evidence"
            product["ai_reason"] = product["reason"]
            product["confidence"] = round(max(
                _as_number(product.get("combined_score"), 0.0),
                _as_number(product.get("semantic_score"), 0.0) * 0.85,
                0.55,
            ), 3)
            product["ai_confidence"] = product["confidence"]
            rescued_false_junk.append(product)
            continue
        remaining_rejected.append(product)
    if rescued_false_junk:
        rejected[:] = remaining_rejected
        fallback_candidates.extend(rescued_false_junk)
        rejected_as_obvious_junk_count = max(0, rejected_as_obvious_junk_count - len(rescued_false_junk))
        rejected_reasons_histogram["obvious_junk"] = max(
            0,
            rejected_reasons_histogram.get("obvious_junk", 0) - len(rescued_false_junk),
        )
    rescued_false_obvious_junk_count = len(rescued_false_junk)
    log("RELEVANCE", f"query={query} target_display={target_display}", "INFO")
    log("RELEVANCE", f"rejected_as_obvious_junk_before_rescue={rejected_as_obvious_junk_count_before_rescue}", "INFO")
    log("RELEVANCE", f"rescued_false_obvious_junk={rescued_false_obvious_junk_count}", "INFO")
    log("RELEVANCE", f"fallback_candidates_after_rescue={len(fallback_candidates)}", "INFO")

    def apply_fallback_expansion() -> int:
        nonlocal accepted_before_fallback, fallback_rejected_as_junk, rejected_as_obvious_junk_count
        expanded = 0
        accepted_before_fallback = len(accepted)
        if len(accepted) >= target_display:
            return 0
        seen_ids = {_product_key(p) for p in accepted}

        unique_candidates: list[dict[str, Any]] = []
        candidate_keys = set()
        for p in [*fallback_candidates, *weak_fallback_candidates]:
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
            score = _as_number(ctx.get("rule_score", product.get("rule_score")), 0.0)
            semantic = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
            existing_confidence = _as_number(product.get("confidence", product.get("relevance_score", product.get("ai_confidence", 0))), 0.0)
            positive_laptop_evidence = is_laptop_gaming_query(query) and has_gaming_laptop_evidence(str(product.get("title") or ""))
            if not positive_laptop_evidence and is_obvious_junk_for_intent(query, product, query_intent):
                fallback_rejected_as_junk += 1
                rejected_as_obvious_junk_count += 1
                record_rejection("obvious_junk", product)
                product_category = str(ctx.get("product_category") or detect_product_category(product))
                rejected.append(_mark_product(
                    product,
                    accepted=False,
                    confidence=max(score, semantic),
                    reason="Fallback rejected because product is obvious junk",
                    source="fallback_reject",
                    query_intent=query_intent,
                    product_category=product_category,
                    rule_score=score,
                    category_match="obvious_junk",
                    combined_score=_as_number(ctx.get("combined_score", product.get("combined_score")), score),
                ))
                continue
            if not _is_valid_product(product):
                record_rejection("invalid_product_data", product)
                product_category = str(ctx.get("product_category") or detect_product_category(product))
                rejected.append(_mark_product(
                    product,
                    accepted=False,
                    confidence=max(score, semantic),
                    reason="Fallback rejected because product data is invalid",
                    source="fallback_reject",
                    query_intent=query_intent,
                    product_category=product_category,
                    rule_score=score,
                    category_match="invalid_product_data",
                    combined_score=_as_number(ctx.get("combined_score", product.get("combined_score")), score),
                ))
                continue
            product_category = str(ctx.get("product_category") or detect_product_category(product))
            combined = _as_number(ctx.get("combined_score", product.get("combined_score")), score)
            source = str(product.get("decision_source") or "")
            if source in {"", "fallback_candidate", "weak_fallback_candidate", "borderline_candidate"}:
                source = "fallback_expansion"
            marked = _mark_product(
                product,
                accepted=True,
                confidence=max(existing_confidence, combined, score, semantic, 0.35),
                reason="Included by fallback expansion to satisfy requested count",
                source=source,
                query_intent=query_intent,
                product_category=product_category,
                rule_score=score,
                category_match="fallback_expansion",
                combined_score=combined,
            )
            accepted.append(marked)
            seen_ids.add(_product_key(product))
            expanded += 1

        if len(products) >= target_count and len(accepted) < target_display:
            log(
                "PIPELINE",
                (
                    f"target_not_met target={target_display} displayed={len(accepted)} "
                    f"accepted_count_before_fallback={accepted_before_fallback} "
                    f"fallback_candidates_count={len(fallback_candidates)} "
                    f"weak_fallback_candidates_count={len(weak_fallback_candidates)} "
                    f"fallback_added={expanded} "
                    f"rejected_as_obvious_junk_count={rejected_as_obvious_junk_count} "
                    f"rejected_reasons_histogram={dict(rejected_reasons_histogram)} "
                    f"reason=fallback_pool_exhausted"
                ),
                "ERROR",
            )
        return expanded

    def _ai_skip_reason(checked: int) -> str | None:
        if ai_skip_reason_override:
            return ai_skip_reason_override
        if ai_circuit_open:
            return ai_circuit_reason or "AI classifier circuit breaker opened for this search"
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
        if fallback_expanded:
            warnings.append(f"{fallback_expanded} produk fallback ditambahkan agar hasil mendekati target.")
        skip_reason = _ai_skip_reason(classifier_checked)
        if skip_reason:
            warnings.append(f"AI classifier: {skip_reason}.")
        displayed = min(len(accepted), target_display)
        if displayed < target_display:
            warnings.append(
                f"Ditampilkan {displayed} dari target aman {target_display}. Cek log pipeline untuk alasan produk dibuang."
            )
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
            "target_display": target_display,
            "query_intent": query_intent,
            "query_constraints": query_constraints,
            "feedback_examples_loaded": feedback_examples_loaded,
            "learned_patterns_loaded": learned_patterns_loaded,
            "query_scoped_patterns": query_scoped_patterns,
            "constraint_scoped_patterns": constraint_scoped_patterns,
            "intent_scoped_patterns": intent_scoped_patterns,
            "global_patterns": global_patterns,
            "constraint_mismatch_products": constraint_mismatch_products,
            "learning_adjusted_products": learning_adjusted_products,
            "learned_positive_matches": learned_positive_matches,
            "learned_negative_matches": learned_negative_matches,
            "selected_model": selected_model if use_ai else None,
            "ai_status": status,
            "ai_orchestrator": orchestrator_status,
            "borderline_candidates": len(borderline),
            "borderline_count": len(borderline),
            "rule_accepted": rule_accepted,
            "rule_accepted_count": rule_accepted,
            "rule_rejected": rule_rejected,
            "rule_rejected_count": rule_rejected,
            "rejected_as_obvious_junk": rejected_as_obvious_junk_count,
            "rejected_as_obvious_junk_count": rejected_as_obvious_junk_count,
            "rejected_as_obvious_junk_count_before_rescue": rejected_as_obvious_junk_count_before_rescue,
            "rescued_false_obvious_junk": rescued_false_obvious_junk_count,
            "fallback_candidates_count_after_rescue": len(fallback_candidates),
            "rejected_reasons_histogram": dict(rejected_reasons_histogram),
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
            "fallback_candidates": len(fallback_candidates),
            "fallback_candidates_count": len(fallback_candidates),
            "weak_fallback_candidates": len(weak_fallback_candidates),
            "weak_fallback_candidates_count": len(weak_fallback_candidates),
            "fallback_rejected_as_junk": fallback_rejected_as_junk,
            "fallback_added": fallback_expanded,
            "fallback_expansion_count": fallback_expanded,
            "displayed": displayed,
            "displayed_count": displayed,
            "accepted_before_fallback": accepted_before_fallback,
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "fallback_used": fallback_by_classifier > 0 or fallback_expanded > 0,
            "warning": warning,
            "thresholds": {
                "rule_accept": RULE_ACCEPT_THRESHOLD,
                "rule_review": RULE_REVIEW_THRESHOLD,
                "rule_reject": RULE_REJECT_THRESHOLD,
                "fallback_expansion": FALLBACK_EXPANSION_THRESHOLD,
                "weak_fallback": WEAK_FALLBACK_THRESHOLD,
                "llm_accept": LLM_ACCEPT_THRESHOLD,
            },
            "ai_skip_reason": _ai_skip_reason(checked),
        }

    def log_runtime_summary(*, fallback_expanded: int, final_displayed: int, checked: int) -> None:
        skip_reason = _ai_skip_reason(checked)
        log("AI_ORCH", f"semantic_checked={semantic_checked}", "INFO")
        log("AI_ORCH", f"classifier_installed={str(classifier_installed).lower()} classifier={selected_model or 'none'}", "INFO")
        log("AI_ORCH", f"borderline_candidates={len(borderline)}", "INFO")
        log("AI_ORCH", f"classifier_checked={checked}", "INFO")
        log("AI_ORCH", f"ai_calls_attempted={ai_calls_attempted}", "INFO")
        log("AI_ORCH", f"ai_calls_succeeded={ai_calls_succeeded}", "INFO")
        log("AI_ORCH", f"ai_skip_reason={skip_reason or 'none'}", "INFO")
        log("PIPELINE", f"requested={target_count} candidate_pool={len(products)} target_display={target_display}", "INFO")
        log("PIPELINE", f"accepted_before_fallback={accepted_before_fallback}", "INFO")
        log("PIPELINE", f"fallback_candidates={len(fallback_candidates)} weak_fallback_candidates={len(weak_fallback_candidates)}", "INFO")
        log("PIPELINE", f"fallback_added={fallback_expanded}", "INFO")
        log("PIPELINE", f"final_displayed={final_displayed}", "INFO")
        log("PIPELINE", f"accepted_before_fallback={accepted_before_fallback} fallback_added={fallback_expanded} final_displayed={final_displayed}", "INFO")
        log("PIPELINE", f"rejected_as_obvious_junk={rejected_as_obvious_junk_count}", "INFO")
        log(
            "PIPELINE",
            (
                f"requested={target_count} candidate_pool={len(products)} "
                f"rule_accepted={rule_accepted} rule_rejected={rule_rejected} "
                f"fallback_candidates={len(fallback_candidates)} weak_fallback_candidates={len(weak_fallback_candidates)} "
                f"fallback_added={fallback_expanded} "
                f"final_displayed={final_displayed} target_display={target_display}"
            ),
            "INFO",
        )

    def finalize_intent_result(
        *,
        status: str,
        checked: int,
        accepted_by_classifier: int,
        rejected_by_classifier: int,
        fallback_by_classifier: int,
        fallback_expanded: int,
        warning: str,
        extra_meta: dict[str, Any] | None = None,
    ) -> IntentFilterResult:
        final_products = _rank_final_products(accepted)[:target_display]
        meta = _build_meta(
            status=status,
            checked=checked,
            accepted_by_classifier=accepted_by_classifier,
            rejected_by_classifier=rejected_by_classifier,
            fallback_by_classifier=fallback_by_classifier,
            fallback_expanded=fallback_expanded,
            warning=warning,
        )
        if extra_meta:
            meta.update(extra_meta)
        meta["displayed"] = len(final_products)
        meta["displayed_count"] = len(final_products)

        final_histogram = Counter(
            str(product.get("decision_source") or product.get("ai_source") or "unknown")
            for product in final_products
        )
        if len(final_products) >= target_display:
            remaining_reason = "target met"
        else:
            remaining_reason = (
                f"fallback pool exhausted after excluding invalid/duplicate/obvious junk products; "
                f"missing={target_display - len(final_products)}"
            )
        debug_payload = {
            "query": query,
            "search_id": search_id,
            "requested": target_count,
            "candidate_pool_count": len(products),
            "target_display": target_display,
            "query_constraints": query_constraints,
            "feedback_examples_loaded": feedback_examples_loaded,
            "learned_patterns_loaded": learned_patterns_loaded,
            "query_scoped_patterns": query_scoped_patterns,
            "constraint_scoped_patterns": constraint_scoped_patterns,
            "intent_scoped_patterns": intent_scoped_patterns,
            "global_patterns": global_patterns,
            "constraint_mismatch_products": constraint_mismatch_products,
            "learning_adjusted_products": learning_adjusted_products,
            "learned_positive_matches": learned_positive_matches,
            "learned_negative_matches": learned_negative_matches,
            "accepted_before_fallback": accepted_before_fallback,
            "fallback_candidates_count": len(fallback_candidates),
            "weak_fallback_candidates_count": len(weak_fallback_candidates),
            "fallback_added": fallback_expanded,
            "final_displayed": len(final_products),
            "rejected_as_obvious_junk_count": rejected_as_obvious_junk_count,
            "rejected_as_obvious_junk_count_before_rescue": rejected_as_obvious_junk_count_before_rescue,
            "rescued_false_obvious_junk": rescued_false_obvious_junk_count,
            "fallback_candidates_count_after_rescue": len(fallback_candidates),
            "rejected_reasons_histogram": dict(rejected_reasons_histogram),
            "semantic_checked": semantic_checked,
            "classifier_checked": checked,
            "ai_checked": checked,
            "ai_calls_attempted": ai_calls_attempted,
            "ai_calls_succeeded": ai_calls_succeeded,
            "ai_accepted": accepted_by_classifier,
            "ai_rejected": rejected_by_classifier,
            "ai_skip_reason": meta.get("ai_skip_reason"),
            "decision_histogram": dict(final_histogram),
            "sample_rejected": [_debug_sample(product) for product in rejected[:10]],
            "sample_fallback": [_debug_sample(product) for product in [*fallback_candidates, *weak_fallback_candidates][:10]],
            "why_remaining_products_were_not_displayed": remaining_reason,
        }
        _write_latest_pipeline_debug(debug_payload)
        meta["pipeline_debug_path"] = "debug/pipeline/latest_search_debug.json"
        meta["decision_histogram"] = dict(final_histogram)
        meta["why_remaining_products_were_not_displayed"] = remaining_reason
        return IntentFilterResult(final_products, status, meta)

    if not borderline:
        fallback_expanded = apply_fallback_expansion()
        warning = _warning_text(fallback_expanded)
        status = "disabled" if not use_ai else ("unavailable" if not classifier_installed else "ok")
        final_displayed = min(len(accepted), target_display)
        log_runtime_summary(fallback_expanded=fallback_expanded, final_displayed=final_displayed, checked=0)
        log(
            "AI",
            (
                f"raw={len(products)} target_display={target_display} intent={query_intent} "
                f"classifier_installed={classifier_installed} selected_classifier={selected_model or 'none'} "
                f"classifier_limit={AI_CLASSIFIER_MAX_PRODUCTS} "
                f"rule_accept={rule_accepted} rule_reject={rule_rejected} semantic_checked={semantic_checked} "
                f"borderline_candidates=0 classifier_checked=0 ai_calls_attempted=0 "
                f"ai_timeouts=0 ai_circuit_open=false "
                f"fallback_candidates={len(fallback_candidates)} fallback_added={fallback_expanded} final_displayed={final_displayed} "
                f"ai_skip_reason={_ai_skip_reason(0)}"
            ),
            "OK",
        )
        return finalize_intent_result(
            status=status,
            checked=0,
            accepted_by_classifier=0,
            rejected_by_classifier=0,
            fallback_by_classifier=0,
            fallback_expanded=fallback_expanded,
            warning=warning,
        )

    if not use_ai or not classifier_installed:
        if not use_ai:
            ai_skip_reason_override = "AI disabled"
            status = "disabled"
        else:
            ai_skip_reason_override = "No supported classifier installed"
            status = "unavailable"

        for product in borderline:
            ctx = product.get("_rule_context", {})
            rule_score = float(ctx.get("rule_score") or product.get("rule_score") or 0.0)
            combined_score = _as_number(ctx.get("combined_score", product.get("combined_score")), rule_score)
            semantic_score = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
            product["rule_score"] = round(rule_score, 3)
            product["combined_score"] = round(combined_score, 3)
            if semantic_score:
                product["semantic_score"] = round(semantic_score, 3)
            product["confidence"] = round(max(combined_score, rule_score, semantic_score, 0.35), 3)
            product["decision_source"] = "fallback_classifier_skipped"
            product["reason"] = "Classifier skipped, included as fallback candidate"
            fallback_candidates.append(product)

        fallback_expanded = apply_fallback_expansion()
        warning = _warning_text(fallback_expanded)
        final_displayed = min(len(accepted), target_display)
        log_runtime_summary(fallback_expanded=fallback_expanded, final_displayed=final_displayed, checked=0)
        log(
            "AI",
            (
                f"raw={len(products)} target_display={target_display} intent={query_intent} "
                f"classifier_installed={classifier_installed} selected_classifier={selected_model or 'none'} "
                f"classifier_limit={AI_CLASSIFIER_MAX_PRODUCTS} "
                f"rule_accept={rule_accepted} rule_reject={rule_rejected} semantic_checked={semantic_checked} "
                f"borderline_candidates={len(borderline)} classifier_checked=0 ai_calls_attempted=0 "
                f"ai_timeouts=0 ai_circuit_open=false "
                f"fallback_candidates={len(fallback_candidates)} fallback_added={fallback_expanded} final_displayed={final_displayed} "
                f"ai_skip_reason={ai_skip_reason_override}"
            ),
            "OK",
        )
        return finalize_intent_result(
            status=status,
            checked=0,
            accepted_by_classifier=0,
            rejected_by_classifier=0,
            fallback_by_classifier=0,
            fallback_expanded=fallback_expanded,
            warning=warning,
        )

    borderline = _sort_borderline_candidates(borderline)
    to_classify = borderline[:AI_CLASSIFIER_MAX_PRODUCTS]
    not_classified = borderline[AI_CLASSIFIER_MAX_PRODUCTS:]
    for product in not_classified:
        ctx = product.get("_rule_context", {})
        rule_score = float(ctx.get("rule_score") or product.get("rule_score") or 0.0)
        combined_score = _as_number(ctx.get("combined_score", product.get("combined_score")), rule_score)
        semantic_score = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
        obvious_junk = bool(ctx.get("obvious_junk"))
        if is_laptop_gaming_query(query) and has_gaming_laptop_evidence(str(product.get("title") or "")):
            obvious_junk = False
        if _is_safe_fallback_candidate(product, rule_score, obvious_junk):
            product["rule_score"] = round(rule_score, 3)
            product["combined_score"] = round(combined_score, 3)
            product["confidence"] = round(max(combined_score, rule_score, semantic_score, 0.35), 3)
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
            combined_score = _as_number(ctx.get("combined_score", product.get("combined_score")), rule_score)
            semantic_score = _as_number(ctx.get("semantic_score", product.get("semantic_score")), 0.0)
            obvious_junk = bool(ctx.get("obvious_junk"))
            positive_laptop_evidence = is_laptop_gaming_query(query) and has_gaming_laptop_evidence(str(product.get("title") or ""))
            if positive_laptop_evidence:
                obvious_junk = False

            if ai_circuit_open:
                if _is_safe_fallback_candidate(product, rule_score, obvious_junk):
                    product["rule_score"] = round(rule_score, 3)
                    product["combined_score"] = round(combined_score, 3)
                    product["confidence"] = round(max(combined_score, rule_score, semantic_score, 0.35), 3)
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
                    combined_score,
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
                    ai_circuit_reason = "AI classifier circuit breaker opened for this search"
                    log(
                        "AI_ORCH",
                        f"circuit_open failures={ai_failure_count} reason={'timeout' if timed_out else 'classifier_error'}",
                        "WARN",
                    )

            ai_confidence = _as_float(response.get("confidence"), 0.5)
            if fallback_used:
                if _is_safe_fallback_candidate(product, rule_score, obvious_junk):
                    product["rule_score"] = round(rule_score, 3)
                    product["combined_score"] = round(combined_score, 3)
                    product["semantic_score"] = round(semantic_score, 3) if semantic_score else product.get("semantic_score")
                    product["confidence"] = round(max(combined_score, rule_score, semantic_score, 0.35), 3)
                    product["decision_source"] = "fallback_ai_timeout" if timed_out else "ai_fallback"
                    product["reason"] = "AI timeout, included as fallback candidate" if timed_out else str(response.get("reason") or "Classifier unavailable, included as fallback candidate")
                    fallback_candidates.append(product)
                else:
                    if obvious_junk:
                        record_rejection("obvious_junk", product)
                    else:
                        record_rejection("invalid_product_data", product)
                    rejected.append(_mark_product(
                        product,
                        accepted=False,
                        confidence=combined_score,
                        reason="AI fallback skipped because product is obvious junk",
                        source="ai_fallback_reject",
                        query_intent=query_intent,
                        product_category=product_category,
                        rule_score=rule_score,
                        category_match="fallback_reject",
                        combined_score=combined_score,
                    ))
                continue

            llm_accepts = bool(response.get("accepted", True)) and (
                ai_confidence >= LLM_ACCEPT_THRESHOLD
            )
            
            confidence = max(combined_score, rule_score, ai_confidence if llm_accepts else min(ai_confidence, combined_score))
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
                combined_score=combined_score,
            )
            if llm_accepts:
                ai_accepted += 1
                accepted.append(marked)
            else:
                ai_rejected += 1
                marked["decision_source"] = "ai_reject"
                marked["ai_source"] = "ai_reject"
                if positive_laptop_evidence and _is_valid_product(marked):
                    marked["decision_source"] = "fallback_after_ai_reject_positive_laptop"
                    marked["ai_source"] = "fallback_after_ai_reject_positive_laptop"
                    marked["reason"] = "AI rejected but product has valid gaming laptop evidence"
                    marked["ai_reason"] = marked["reason"]
                    marked["rule_score"] = round(rule_score, 3)
                    marked["combined_score"] = round(combined_score, 3)
                    fallback_candidates.append(marked)
                elif _is_safe_fallback_candidate(marked, rule_score, obvious_junk):
                    marked["decision_source"] = "fallback_after_ai_reject"
                    marked["rule_score"] = round(rule_score, 3)
                    marked["combined_score"] = round(combined_score, 3)
                    fallback_candidates.append(marked)
                else:
                    if obvious_junk:
                        record_rejection("obvious_junk", marked)
                    else:
                        record_rejection("invalid_product_data", marked)
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

    meta_result = finalize_intent_result(
        status=status,
        checked=classifier_checked,
        accepted_by_classifier=ai_accepted,
        rejected_by_classifier=ai_rejected,
        fallback_by_classifier=ai_fallback,
        fallback_expanded=fallback_expanded,
        warning=warning,
        extra_meta={"batch_count": len(batches)},
    )
    final_displayed = min(len(accepted), target_display)
    log_runtime_summary(
        fallback_expanded=fallback_expanded,
        final_displayed=final_displayed,
        checked=classifier_checked,
    )
    
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
            f"fallback_candidates={len(fallback_candidates)} fallback_added={fallback_expanded} final_displayed={final_displayed}"
        ),
        "OK",
    )
    return meta_result


def _is_safe_fallback_candidate(product: dict[str, Any], rule_score: float, obvious_junk: bool) -> bool:
    if obvious_junk:
        return False
    return _is_valid_product(product)
