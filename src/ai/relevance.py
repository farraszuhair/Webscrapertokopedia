"""
relevance.py - Qwen-based relevance filtering.

Pipeline: raw products -> Qwen semantic filter -> keep relevant ones.

NO hardcoded category keyword filter before Qwen.
Qwen IS the semantic filter.
User feedback teaches Qwen via few-shot examples in the prompt.

Fallback: if Qwen fails, use simple title-word scoring (never crash).

Qwen output schema:
{
  "relevant": true,
  "confidence": 0.86,
  "categories": ["gaming_laptop"],
  "reason": "ASUS TUF Gaming is a gaming laptop."
}
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List

from src.ai.learning import get_recent_examples, get_recent_feedback
from src.ai.qwen_client import ask_qwen
from src.utils.logger import log


RELEVANCE_THRESHOLD = 0.55  # accept product if confidence >= this
FALLBACK_SCORE = 0.5        # used when Qwen is offline


def _build_qwen_prompt(query: str, product: dict[str, Any], examples: list, feedback: list) -> str:
    """
    Build the Qwen prompt with few-shot examples from user feedback.
    Examples teach Qwen what the user considers relevant for this specific query.
    """
    title = product.get("title", "")
    price = product.get("price_raw", "")

    # Few-shot section from user feedback (teaches Qwen from past corrections)
    few_shot = ""
    if examples:
        few_shot = "\nExamples from user feedback (learn from these):\n"
        for ex in examples[-5:]:  # last 5 examples
            label = ex.get("label", "unknown")
            few_shot += (
                f"- Title: \"{ex.get('title', '')}\" -> label: {label}"
                f" (categories: {ex.get('categories', [])})"
                f" reason: {ex.get('reason', '')}\n"
            )

    # Additional feedback context
    feedback_ctx = ""
    if feedback:
        feedback_ctx = "\nRecent user corrections:\n"
        for fb in feedback[-3:]:
            feedback_ctx += (
                f"- \"{fb.get('product_title', '')}\" was marked '{fb.get('correction', '')}'"
                f" because: {fb.get('note', '')}\n"
            )

    prompt = f"""You are an e-commerce product relevance validator for Tokopedia (Indonesian marketplace).

User searched for: "{query}"
Product Title: "{title}"
Product Price: "{price}"
{few_shot}{feedback_ctx}
Task: Is this product relevant to the user's search?

Rules:
- For broad queries like "laptop gaming", accept gaming laptops of any brand (ROG, Legion, ASUS, MSI, Acer, Lenovo, HP Omen, etc.)
- Reject accessories (mouse, charger, cooler, RAM, SSD, bag, sleeve) unless specifically searched for
- A product with GPU (RTX, GTX) and "laptop" in title is almost certainly relevant for "laptop gaming"
- Use context from user feedback examples above to learn what this user wants

Respond in strict JSON only (no text outside JSON):
{{
  "relevant": true or false,
  "confidence": 0.0 to 1.0,
  "categories": ["one or more from: gaming_laptop, office_laptop, laptop_accessory, mouse, keyboard, charger, cooling_pad, headset, ram, ssd, monitor, not_laptop, other"],
  "reason": "short explanation in English"
}}"""
    return prompt


def _fallback_score(query: str, product: dict[str, Any]) -> dict[str, Any]:
    """
    Simple fallback when Qwen is offline.
    Uses word overlap + known positive signals.
    Never rejects anything unless it's an obvious accessory.
    """
    title = product.get("title", "").lower()
    query_words = set(query.lower().split())
    title_words = set(re.findall(r'\w+', title))

    # Strong positive signals for laptops
    laptop_signals = {"laptop", "notebook", "rog", "legion", "nitro", "predator", "msi", "omen",
                      "alienware", "rtx", "gtx", "geforce", "ryzen", "intel"}
    # Strong negative signals (obvious accessories, not laptops)
    accessory_signals = {"mouse", "mice", "mousepad", "keyboard", "charger", "adaptor",
                         "cooling", "headset", "earphone", "webcam", "sleeve", "tas"}

    accessory_hits = accessory_signals & title_words
    laptop_hits = laptop_signals & title_words
    query_overlap = query_words & title_words

    if accessory_hits and not laptop_hits:
        return {
            "relevant": False,
            "confidence": 0.1,
            "categories": ["laptop_accessory"],
            "reason": f"Fallback: accessory keywords detected ({', '.join(accessory_hits)}), no laptop signals",
        }

    if laptop_hits or query_overlap:
        confidence = min(0.9, 0.5 + len(laptop_hits) * 0.1 + len(query_overlap) * 0.05)
        return {
            "relevant": True,
            "confidence": confidence,
            "categories": ["gaming_laptop" if "gaming" in query.lower() else "other"],
            "reason": f"Fallback: matched {laptop_hits | query_overlap}",
        }

    # No strong signal either way - keep it (fail open)
    return {
        "relevant": True,
        "confidence": FALLBACK_SCORE,
        "categories": ["other"],
        "reason": "Fallback: no strong signal, accepted by default",
    }


async def _validate_product(
    query: str,
    product: dict[str, Any],
    use_ai: bool,
    examples: list,
    feedback: list,
) -> dict[str, Any]:
    """Ask Qwen about one product. Falls back to scoring if Qwen fails."""
    if not use_ai:
        decision = _fallback_score(query, product)
        decision["source"] = "fallback_ai_disabled"
        return decision

    prompt = _build_qwen_prompt(query, product, examples, feedback)
    ai_response = await ask_qwen(prompt)

    if ai_response and isinstance(ai_response, dict) and "relevant" in ai_response:
        ai_response["source"] = "qwen"
        # Normalize categories to list
        cats = ai_response.get("categories")
        if isinstance(cats, str):
            ai_response["categories"] = [cats]
        elif not isinstance(cats, list):
            ai_response["categories"] = []
        return ai_response

    # Qwen failed - use fallback
    decision = _fallback_score(query, product)
    decision["source"] = "fallback_qwen_failed"
    return decision


async def filter_relevance(
    query: str,
    products: List[Dict[str, Any]],
    use_ai: bool = True,
    search_id: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Filter products by Qwen relevance.

    For each product:
    1. Ask Qwen (or fallback if Qwen is down).
    2. Keep if relevant=True AND confidence >= threshold.
    3. Attach ai_decision, ai_reason, relevance_score to each product.

    Products are passed in ALREADY normalized. No category filter before this.
    """
    examples = get_recent_examples(query)
    feedback = get_recent_feedback(query)

    log("AI", f"filter_relevance: {len(products)} products, use_ai={use_ai}, examples={len(examples)}, feedback={len(feedback)}", "INFO")

    valid: list[dict[str, Any]] = []
    qwen_debug: list[dict[str, Any]] = []

    for product in products:
        decision = await _validate_product(query, product, use_ai, examples, feedback)

        # Attach decision to product for frontend display
        product["relevance_score"] = float(decision.get("confidence", 0.5))
        product["ai_decision"] = decision.get("relevant", True)
        product["ai_reason"] = decision.get("reason", "")
        product["ai_categories"] = decision.get("categories", [])
        product["ai_source"] = decision.get("source", "unknown")

        qwen_debug.append({
            "title": product.get("title", ""),
            "decision": decision,
            "kept": decision.get("relevant", True) and product["relevance_score"] >= RELEVANCE_THRESHOLD,
        })

        if decision.get("relevant", True) and product["relevance_score"] >= RELEVANCE_THRESHOLD:
            valid.append(product)
        else:
            log("AI", f"[REJECT] {product.get('title', '')[:50]} confidence={product['relevance_score']:.2f} reason={product['ai_reason'][:80]}", "INFO")

    # Save Qwen filter debug
    if search_id:
        from src.utils.debug import save_json_debug
        save_json_debug(search_id, "qwen_filter_debug.json", {
            "query": query,
            "total_input": len(products),
            "total_kept": len(valid),
            "threshold": RELEVANCE_THRESHOLD,
            "use_ai": use_ai,
            "examples_used": len(examples),
            "feedback_used": len(feedback),
            "decisions": qwen_debug,
        })

    log("AI", f"filter_relevance: {len(products)} in, {len(valid)} kept", "OK")
    return valid
