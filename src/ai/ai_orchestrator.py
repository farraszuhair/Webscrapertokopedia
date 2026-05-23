"""
Automatic AI Orchestrator for borderline product relevance checks.
"""
from __future__ import annotations

import json
from typing import Any

from src.ai.json_repair import repair_json_or_fallback
from src.ai.model_registry import get_orchestrator_status, get_installed_model_name
from src.ai.ollama_client import chat_raw_async
from src.config import AI_CPU_MODE, LLM_ACCEPT_THRESHOLD, RULE_ACCEPT_THRESHOLD, RULE_REJECT_THRESHOLD, RULE_REVIEW_THRESHOLD
from src.utils.logger import log


def should_call_llm(rule_score: float, obvious_junk: bool) -> bool:
    if rule_score >= RULE_ACCEPT_THRESHOLD:
        return False
    if obvious_junk and rule_score < RULE_REJECT_THRESHOLD:
        return False
    if rule_score >= RULE_REVIEW_THRESHOLD:
        return True
    return False


def build_classifier_prompt(query: str, query_intent: str, product: dict[str, Any]) -> str:
    from src.ai.feedback_store import extract_query_constraints, load_feedback_context

    query_constraints = extract_query_constraints(query)
    product_constraints = extract_query_constraints(str(product.get("title") or ""))
    feedback_memory = load_feedback_context(query, query_intent, query_constraints, limit=12)
    positive_examples = json.dumps(feedback_memory.get("positive_examples", []), ensure_ascii=True, default=str)
    negative_examples = json.dumps(feedback_memory.get("negative_examples", []), ensure_ascii=True, default=str)
    learned_patterns = json.dumps(feedback_memory.get("learned_patterns", []), ensure_ascii=True, default=str)
    product_constraints_json = json.dumps(product_constraints, ensure_ascii=True, default=str)
    query_constraints_json = json.dumps(query_constraints, ensure_ascii=True, default=str)
    return f"""Query: {query}
Intent: {query_intent}
Query constraints: {query_constraints_json}

User feedback memory:
Positive examples:
{positive_examples}

Negative examples:
{negative_examples}

Learned patterns:
{learned_patterns}

Product:
Title: {product.get("title", "")}
Price: {product.get("price_raw") or product.get("price_text") or product.get("price", "")}
Store: {product.get("shop_name") or product.get("shop") or ""}
Product constraints: {product_constraints_json}

Decision rules:
- Follow user feedback memory, but respect scope.
- Negative feedback from another query must not globally ban a product.
- If query wants RTX 5060 and product has RTX 4060, mark spec mismatch.
- If query wants RTX 4060 and product has RTX 4060, do not apply RTX 5060 negative feedback.
- If unsure, accepted can be true with lower confidence instead of hard rejecting.
- Main product query rejects accessories/spare parts.
- Accessory query accepts matching accessories.
- Sparepart query accepts matching spare parts.
- laptop gaming accepts ROG, Legion, Nitro, TUF, Victus, LOQ, RTX, GTX, MSI.
- casing iphone accepts case/casing/softcase/hardcase for that iPhone.

Return exactly:
{{"accepted":true,"confidence":0.0,"reason":"short","category_match":"main/accessory/sparepart/no","learned_match":""}}
No markdown.
"""


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

    resolved_classifier = get_installed_model_name(str(classifier), status.get("installed") or None)
    prompt = build_classifier_prompt(query, query_intent, product)
    result = await chat_raw_async(prompt, model=resolved_classifier, use_json_format=True)
    
    if not result.get("ok") and not AI_CPU_MODE:
        supported = set(status.get("supported") or [])
        fallback_model = "llama3.2:3b"
        resolved_fallback = get_installed_model_name(fallback_model, status.get("installed") or None)
        if classifier != fallback_model and fallback_model in supported:
            log("AI_ORCH", f"classifier_fallback primary={resolved_classifier} fallback={resolved_fallback}", "WARN")
            resolved_classifier = resolved_fallback
            result = await chat_raw_async(prompt, model=resolved_fallback, use_json_format=True)

    parsed = result.get("parsed")
    if not result.get("ok"):
        parsed = {
            "accepted": True,
            "confidence": 0.50,
            "reason": "Classifier unavailable, accepted by safe fallback to avoid empty results",
            "category_match": "fallback",
            "decision_source": "ai_fallback",
        }
    elif not parsed:
        parsed = await repair_json_or_fallback(
            str(result.get("content") or result.get("error") or ""),
            phi_available=bool(status.get("capabilities", {}).get("json_repair")),
        )

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
    parsed["_timeout"] = bool(result.get("timeout"))
    parsed["_error"] = str(result.get("error") or "")
    parsed["_llm_accept_threshold"] = LLM_ACCEPT_THRESHOLD
    return parsed
