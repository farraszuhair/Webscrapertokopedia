"""
Automatic AI Orchestrator for borderline product relevance checks.
"""
from __future__ import annotations

import json
from typing import Any

from src.ai.json_repair import repair_json_or_fallback
from src.ai.model_registry import get_orchestrator_status, get_installed_model_name
from src.ai.ollama_client import chat_raw_async
from src.config import AI_CHAT_NUM_CTX, LLM_ACCEPT_THRESHOLD, RULE_ACCEPT_THRESHOLD, RULE_REJECT_THRESHOLD, RULE_REVIEW_THRESHOLD
from src.utils.logger import log


def should_call_llm(rule_score: float, obvious_junk: bool) -> bool:
    if rule_score >= RULE_ACCEPT_THRESHOLD:
        return False
    if obvious_junk and rule_score < RULE_REJECT_THRESHOLD:
        return False
    if rule_score >= RULE_REVIEW_THRESHOLD:
        return True
    return False


def estimate_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)


def clamp_text(text: str, max_chars: int) -> str:
    return (text or "")[:max_chars]


def _feedback_title(item: dict[str, Any]) -> str:
    return str(item.get("title") or item.get("product_title") or "")


def _feedback_reason(item: dict[str, Any]) -> str:
    reason = item.get("reason")
    if reason:
        return str(reason)
    reasons = item.get("reasons")
    if isinstance(reasons, list):
        return ", ".join(str(reason) for reason in reasons if reason)
    return str(item.get("note") or "")


def build_compact_feedback_memory(
    feedback_context: dict[str, Any],
    *,
    positive_limit: int = 2,
    negative_limit: int = 2,
    pattern_limit: int = 3,
) -> str:
    lines: list[str] = []

    for item in (feedback_context.get("positive_examples") or [])[:positive_limit]:
        title = clamp_text(_feedback_title(item), 80)
        if title:
            lines.append(f"+ {title}")

    for item in (feedback_context.get("negative_examples") or [])[:negative_limit]:
        title = clamp_text(_feedback_title(item), 80)
        reason = clamp_text(_feedback_reason(item), 40)
        if title:
            lines.append(f"- {title} | {reason}")

    for pattern in (feedback_context.get("learned_patterns") or [])[:pattern_limit]:
        p = clamp_text(str(pattern.get("pattern") or ""), 40)
        scope = pattern.get("scope", "")
        weight = pattern.get("weight", 0)
        if p:
            lines.append(f"pattern {p} scope={scope} weight={weight}")

    return "\n".join(lines) or "none"


def _product_audit_id(product: dict[str, Any], index: int) -> str:
    audit_id = str(product.get("_audit_id") or product.get("id") or f"p{index + 1}")
    product["_audit_id"] = audit_id
    return audit_id


def _product_constraints(product: dict[str, Any]) -> dict[str, Any]:
    ctx = product.get("_rule_context") or {}
    constraints = ctx.get("product_constraints") or product.get("product_constraints") or {}
    if isinstance(constraints, dict) and constraints:
        return constraints
    from src.ai.feedback_store import extract_query_constraints

    return extract_query_constraints(str(product.get("title") or product.get("name") or ""))


def _compact_product_payload(products: list[dict[str, Any]], title_chars: int) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for index, product in enumerate(products):
        ctx = product.get("_rule_context") or {}
        payload.append({
            "id": _product_audit_id(product, index),
            "title": clamp_text(str(product.get("title") or product.get("name") or ""), title_chars),
            "price": product.get("price_value") or product.get("priceNumber") or product.get("price") or 0,
            "score": product.get("combined_score") or ctx.get("combined_score") or product.get("rule_score") or 0,
            "constraints": _product_constraints(product),
        })
    return payload


def _render_batch_prompt(
    *,
    query: str,
    query_intent: str,
    query_constraints: dict[str, Any],
    feedback_memory: str,
    compact_products: list[dict[str, Any]],
) -> str:
    query_constraints_json = json.dumps(query_constraints, ensure_ascii=True, default=str, separators=(",", ":"))
    compact_products_json = json.dumps(compact_products, ensure_ascii=True, default=str, separators=(",", ":"))
    return f"""Query: {clamp_text(query, 160)}
Intent: {query_intent}
Query constraints: {query_constraints_json}

Feedback memory:
{feedback_memory}

Products:
{compact_products_json}

Rules:
- Use feedback only when scope matches query.
- Negative feedback is not global unless scope=global.
- Spec mismatch matters: if query wants RTX 5060 and product has RTX 4060, reject for this query.
- If query wants RTX 4060 and product has RTX 4060, do not reject because of RTX 5060 feedback.
- For laptop gaming, accept real gaming laptops.
- Reject accessory-only or non-product pages.
- Return JSON only.

Return exactly:
{{"items":[{{"id":"p1","accepted":true,"confidence":0.0,"reason":"short"}}]}}

No markdown.
No explanation.
"""


def build_batch_classifier_prompt(
    query: str,
    query_intent: str,
    query_constraints: dict[str, Any],
    feedback_context: dict[str, Any],
    products: list[dict[str, Any]],
) -> dict[str, Any]:
    feedback_memory = build_compact_feedback_memory(feedback_context)
    compact_products = _compact_product_payload(products[:3], title_chars=160)
    prompt = _render_batch_prompt(
        query=query,
        query_intent=query_intent,
        query_constraints=query_constraints,
        feedback_memory=feedback_memory,
        compact_products=compact_products,
    )
    token_estimate = estimate_tokens(prompt)
    truncated_by_app = False

    if token_estimate > 3000:
        truncated_by_app = True
        feedback_memory = build_compact_feedback_memory(
            feedback_context,
            positive_limit=1,
            negative_limit=1,
            pattern_limit=1,
        )
        compact_products = _compact_product_payload(products[:3], title_chars=120)
        prompt = _render_batch_prompt(
            query=query,
            query_intent=query_intent,
            query_constraints=query_constraints,
            feedback_memory=feedback_memory,
            compact_products=compact_products,
        )
        token_estimate = estimate_tokens(prompt)

    if token_estimate > 3000:
        truncated_by_app = True
        compact_products = _compact_product_payload(products[:3], title_chars=80)
        prompt = _render_batch_prompt(
            query=query,
            query_intent=query_intent,
            query_constraints=query_constraints,
            feedback_memory="none",
            compact_products=compact_products,
        )
        token_estimate = estimate_tokens(prompt)

    if token_estimate > 3000:
        truncated_by_app = True
        compact_products = _compact_product_payload(products[:1], title_chars=80)
        prompt = _render_batch_prompt(
            query=query,
            query_intent=query_intent,
            query_constraints=query_constraints,
            feedback_memory="none",
            compact_products=compact_products,
        )
        token_estimate = estimate_tokens(prompt)

    return {
        "prompt": prompt,
        "prompt_tokens_estimated": token_estimate,
        "truncated_by_app": truncated_by_app,
        "compact_products": compact_products,
    }


def build_classifier_prompt(query: str, query_intent: str, product: dict[str, Any]) -> str:
    from src.ai.feedback_store import extract_query_constraints, load_feedback_context

    query_constraints = extract_query_constraints(query)
    feedback_context = load_feedback_context(query, query_intent, query_constraints, limit=4)
    return build_batch_classifier_prompt(
        query,
        query_intent,
        query_constraints,
        feedback_context,
        [product],
    )["prompt"]


def _normalize_batch_items(parsed: dict[str, Any] | None, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(parsed, dict):
        return []
    raw_items = parsed.get("items")
    if raw_items is None and "accepted" in parsed:
        raw_items = [{
            "id": products[0].get("_audit_id", "p1") if products else "p1",
            "accepted": parsed.get("accepted"),
            "confidence": parsed.get("confidence"),
            "reason": parsed.get("reason"),
        }]
    if not isinstance(raw_items, list):
        return []

    valid_ids = {str(product.get("_audit_id")) for product in products}
    normalized: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id") or "")
        if item_id not in valid_ids:
            continue
        try:
            confidence = float(item.get("confidence", 0.50))
        except (TypeError, ValueError):
            confidence = 0.50
        accepted_raw = item.get("accepted", True)
        if isinstance(accepted_raw, str):
            accepted = accepted_raw.strip().lower() not in {"false", "0", "no", "tidak"}
        else:
            accepted = bool(accepted_raw)
        normalized.append({
            "id": item_id,
            "accepted": accepted,
            "confidence": max(0.0, min(0.98, confidence)),
            "reason": clamp_text(str(item.get("reason") or "AI audit decision"), 120),
            "category_match": str(item.get("category_match") or "ai"),
            "decision_source": "ai_orchestrator",
        })
    return normalized


async def classify_product_batch(
    query: str,
    query_intent: str,
    products: list[dict[str, Any]],
    *,
    status: dict[str, Any] | None = None,
    ai_enabled: bool = True,
    feedback_context: dict[str, Any] | None = None,
    query_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status = status or get_orchestrator_status()
    classifier = status.get("classifier")
    if not ai_enabled or not classifier or not products:
        return {
            "ok": False,
            "items": [],
            "_model": None,
            "_fallback_used": True,
            "_chat_ok": False,
            "_timeout": False,
            "_error": "AI disabled, classifier missing, or no products",
            "attempts": 0,
        }

    if query_constraints is None or feedback_context is None:
        from src.ai.feedback_store import extract_query_constraints, load_feedback_context

        query_constraints = query_constraints or extract_query_constraints(query)
        feedback_context = feedback_context or load_feedback_context(query, query_intent, query_constraints, limit=4)

    resolved_classifier = get_installed_model_name(str(classifier), status.get("installed") or None)
    prompt_data = build_batch_classifier_prompt(
        query,
        query_intent,
        query_constraints or {},
        feedback_context or {},
        products,
    )
    prompt = str(prompt_data["prompt"])
    prompt_tokens = int(prompt_data["prompt_tokens_estimated"])
    truncated_by_app = bool(prompt_data["truncated_by_app"])
    log(
        "AI_ORCH",
        f"prompt_tokens_estimated={prompt_tokens} ctx={AI_CHAT_NUM_CTX} truncated_by_app={str(truncated_by_app).lower()}",
        "INFO",
    )

    result = await chat_raw_async(
        prompt,
        model=resolved_classifier,
        use_json_format=True,
        prompt_tokens_estimated=prompt_tokens,
    )
    parsed = result.get("parsed")
    if result.get("ok") and not parsed:
        parsed = await repair_json_or_fallback(
            str(result.get("content") or ""),
            phi_available=bool(status.get("capabilities", {}).get("json_repair")),
        )

    items = _normalize_batch_items(parsed if isinstance(parsed, dict) else None, products) if result.get("ok") else []
    if not result.get("ok"):
        log("AI_ORCH", f"classifier_failed model={resolved_classifier} error={result.get('error')}", "WARN")

    return {
        "ok": bool(result.get("ok")),
        "items": items,
        "_model": resolved_classifier,
        "_fallback_used": not bool(result.get("ok")),
        "_chat_ok": bool(result.get("ok")),
        "_timeout": bool(result.get("timeout")),
        "_error": str(result.get("error") or ""),
        "attempts": int(result.get("attempts") or 0),
        "prompt_tokens_estimated": prompt_tokens,
        "truncated_by_app": truncated_by_app,
        "ctx": result.get("ctx", AI_CHAT_NUM_CTX),
        "status_code": result.get("status_code"),
    }


async def classify_borderline_product(
    query: str,
    query_intent: str,
    product: dict[str, Any],
    rule_score: float,
    status: dict[str, Any] | None = None,
    ai_enabled: bool = True,
) -> dict[str, Any]:
    status = status or get_orchestrator_status()
    classifier = status.get("classifier")

    if not ai_enabled or not classifier:
        # Rule-based fallback: if rule_score >= 0.58, accept; else reject.
        accepted = rule_score >= 0.58
        return {
            "accepted": accepted,
            "confidence": rule_score,
            "reason": "Included by rule fallback (AI disabled or classifier not installed)" if accepted else "Rejected by rule fallback (AI disabled or classifier not installed)",
            "category_match": "rules",
            "decision_source": "rule_fallback",
            "_model": None,
            "_fallback_used": True,
            "_llm_accept_threshold": LLM_ACCEPT_THRESHOLD,
        }

    result = await classify_product_batch(
        query,
        query_intent,
        [product],
        status=status,
        ai_enabled=ai_enabled,
    )
    resolved_classifier = str(result.get("_model") or classifier or "")
    parsed = (result.get("items") or [{}])[0] if result.get("items") else None
    if not result.get("ok"):
        parsed = {
            "accepted": True,
            "confidence": 0.50,
            "reason": "Classifier unavailable, accepted by safe fallback to avoid empty results",
            "category_match": "fallback",
            "decision_source": "ai_fallback",
        }
    elif not parsed:
        parsed = {}

    if not result.get("ok") and parsed.get("decision_source") == "ai_fallback":
        log("AI_ORCH", f"classifier_failed model={resolved_classifier} rule_score={rule_score}", "WARN")

    accepted = bool(parsed.get("accepted", True))
    try:
        confidence = float(parsed.get("confidence", 0.50))
    except (TypeError, ValueError):
        confidence = 0.50
    parsed["accepted"] = accepted
    parsed["confidence"] = max(0.0, min(0.98, confidence))
    parsed.setdefault("reason", "AI Orchestrator classified borderline product")
    parsed.setdefault("category_match", "ai")
    parsed.setdefault("decision_source", "ai_orchestrator" if result.get("ok") else "ai_fallback")
    parsed["_model"] = resolved_classifier
    parsed["_fallback_used"] = parsed.get("decision_source") == "ai_fallback"
    parsed["_chat_ok"] = bool(result.get("ok"))
    parsed["_timeout"] = bool(result.get("_timeout"))
    parsed["_error"] = str(result.get("_error") or "")
    parsed["_prompt_tokens_estimated"] = result.get("prompt_tokens_estimated")
    parsed["_truncated_by_app"] = result.get("truncated_by_app")
    parsed["_llm_accept_threshold"] = LLM_ACCEPT_THRESHOLD
    return parsed
