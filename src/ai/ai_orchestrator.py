"""
Automatic AI Orchestrator for borderline product relevance checks.
"""
from __future__ import annotations

from typing import Any

from src.ai.json_repair import repair_json_or_fallback
from src.ai.model_registry import get_orchestrator_status, get_installed_model_name
from src.ai.ollama_client import chat_raw_async
from src.config import LLM_ACCEPT_THRESHOLD, RULE_ACCEPT_THRESHOLD, RULE_REJECT_THRESHOLD, RULE_REVIEW_THRESHOLD
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
- If user searches for a main product, reject accessories and spare parts.
- If user searches for an accessory, accept matching accessories.
- If user searches for a spare part, accept matching spare parts.
- Do not globally reject accessories.
- Reject only when product category does not match query intent.
- Accept semantic matches even if exact words are different.
- For "laptop gaming", accept ASUS ROG, Lenovo Legion, Acer Nitro, MSI, HP Victus, ASUS TUF, RTX/GTX laptops.
- For "casing iphone 13", accept case, casing, softcase, hardcase, MagSafe case for iPhone 13.
- Return JSON only.
- No markdown.

JSON format:
{{
  "accepted": true,
  "confidence": 0.0,
  "reason": "...",
  "category_match": "..."
}}
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

    resolved_classifier = get_installed_model_name(str(classifier))
    prompt = build_classifier_prompt(query, query_intent, product)
    result = await chat_raw_async(prompt, model=resolved_classifier, use_json_format=True)
    
    if not result.get("ok"):
        supported = set(status.get("supported") or [])
        fallback_model = "llama3.2:3b"
        resolved_fallback = get_installed_model_name(fallback_model)
        if classifier != fallback_model and fallback_model in supported:
            log("AI_ORCH", f"classifier_fallback primary={resolved_classifier} fallback={resolved_fallback}", "WARN")
            resolved_classifier = resolved_fallback
            result = await chat_raw_async(prompt, model=resolved_fallback, use_json_format=True)

    parsed = result.get("parsed")
    if not parsed:
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
    parsed["_llm_accept_threshold"] = LLM_ACCEPT_THRESHOLD
    return parsed
