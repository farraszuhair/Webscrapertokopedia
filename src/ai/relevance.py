"""
relevance.py - Qwen-based relevance filtering.

Pipeline: raw normalized products -> Qwen semantic filter -> keep relevant ones.

Key behaviors:
1. Run Ollama health check ONCE before batching.
   If Ollama is down, skip all Qwen calls and use fallback immediately.
   This prevents 120s * N product timeouts when Ollama is known dead.

2. If Qwen returns HTTP 500 or timeout on first product, mark qwen_status="failed"
   and switch ALL remaining products to fallback. No hanging on 500.

3. filter_relevance() returns (products, qwen_status) where qwen_status is:
   "ok"         - Qwen responded correctly
   "failed"     - Qwen gave 500/timeout/invalid JSON
   "disabled"   - use_ai=False
   "unavailable"- Ollama not running

4. Caller (routes.py) puts qwen_status in compare card so UI shows:
   "Qwen gagal, hasil raw/budget tetap ditampilkan."

NO hardcoded category filter. Qwen IS the semantic filter.
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Tuple

from src.ai.learning import get_recent_examples, get_recent_feedback
from src.ai.qwen_client import ask_qwen, check_ollama_health
from src.utils.logger import log


RELEVANCE_THRESHOLD = 0.55  # keep product if Qwen confidence >= this
FALLBACK_SCORE = 0.5        # used when Qwen is offline (fail-open default)

# How many consecutive Qwen failures before giving up and switching to fallback
MAX_CONSECUTIVE_FAILURES = 2


def _build_qwen_prompt(
    query: str,
    product: dict[str, Any],
    examples: list,
    feedback: list,
) -> str:
    """
    Build Qwen prompt with few-shot examples from user feedback.
    Keeps prompt small to avoid context-window OOM (which causes HTTP 500).
    """
    title = product.get("title", "")
    price = product.get("price_raw", "")

    # Few-shot: last 3 examples max (keep prompt small for 14B context limit)
    few_shot = ""
    if examples:
        few_shot = "\nUser feedback examples (apply these rules):\n"
        for ex in examples[-3:]:
            few_shot += (
                f'- "{ex.get("title", "")}" -> {ex.get("label", "unknown")}'
                f' | categories={ex.get("categories", [])}'
                f' | reason={ex.get("reason", "")}\n'
            )

    # Recent corrections context (last 2 only)
    feedback_ctx = ""
    if feedback:
        feedback_ctx = "\nRecent corrections:\n"
        for fb in feedback[-2:]:
            feedback_ctx += (
                f'- "{fb.get("product_title", "")}" was marked "{fb.get("correction", "")}"'
                f' | note={fb.get("note", "")}\n'
            )

    prompt = f"""You are an e-commerce product relevance validator for Tokopedia.

User searched: "{query}"
Product: "{title}"
Price: "{price}"
{few_shot}{feedback_ctx}
Is this product relevant to the search?

Rules:
- Accept gaming laptops of any brand (ROG, Legion, ASUS, MSI, Acer, HP Omen, Lenovo, etc.)
- Reject accessories (mouse, keyboard, charger, cooler, RAM, SSD, headset, bag) unless specifically searched for
- A product with GPU model (RTX, GTX) and "laptop" in title is almost certainly relevant for "laptop gaming"

Respond ONLY in strict JSON (no text outside JSON):
{{"relevant": true, "confidence": 0.9, "categories": ["gaming_laptop"], "reason": "short reason"}}"""
    return prompt


def _fallback_score(query: str, product: dict[str, Any]) -> dict[str, Any]:
    """
    Offline fallback when Qwen is unavailable.
    Fail-open: keep product unless it's obviously an accessory.
    """
    title = product.get("title", "").lower()
    title_words = set(re.findall(r'\w+', title))
    query_words = set(query.lower().split())

    laptop_signals = {
        "laptop", "notebook", "rog", "legion", "nitro", "predator",
        "msi", "omen", "alienware", "rtx", "gtx", "geforce", "ryzen", "intel",
    }
    accessory_signals = {
        "mouse", "mice", "mousepad", "keyboard", "charger", "adaptor",
        "cooling", "headset", "earphone", "webcam", "sleeve", "tas",
    }

    accessory_hits = accessory_signals & title_words
    laptop_hits = laptop_signals & title_words
    query_overlap = query_words & title_words

    if accessory_hits and not laptop_hits:
        return {
            "relevant": False,
            "confidence": 0.1,
            "categories": ["laptop_accessory"],
            "reason": f"Fallback: accessory signals detected ({', '.join(accessory_hits)})",
        }

    if laptop_hits or query_overlap:
        confidence = min(0.9, 0.5 + len(laptop_hits) * 0.1 + len(query_overlap) * 0.05)
        return {
            "relevant": True,
            "confidence": confidence,
            "categories": ["gaming_laptop" if "gaming" in query.lower() else "other"],
            "reason": f"Fallback: matched signals {laptop_hits | query_overlap}",
        }

    return {
        "relevant": True,
        "confidence": FALLBACK_SCORE,
        "categories": ["other"],
        "reason": "Fallback: no strong signal, kept by default (fail-open)",
    }


async def filter_relevance(
    query: str,
    products: List[Dict[str, Any]],
    use_ai: bool = True,
    search_id: str | None = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Filter products by Qwen relevance.

    Returns:
        (filtered_products, qwen_status)

    qwen_status values:
        "ok"          - Qwen responded to at least one product
        "failed"      - Qwen consistently failed (500/timeout), fallback used
        "disabled"    - use_ai=False, fallback used intentionally
        "unavailable" - Ollama not running, fallback used

    IMPORTANT: This always returns products even when Qwen fails.
    Caller must NOT block on qwen_status.
    """
    if not products:
        return [], "ok"

    if not use_ai:
        # AI disabled: use fallback scoring, return all above threshold
        log("AI", f"AI disabled - applying fallback for {len(products)} products", "INFO")
        result = _apply_fallback_all(query, products, "fallback_ai_disabled")
        return result, "disabled"

    # ── Health check ────────────────────────────────────────────────────────
    # One quick probe before sending potentially 50+ Qwen requests.
    # If Ollama is down, skip the 120s * N timeouts immediately.
    ollama_alive = await check_ollama_health()
    if not ollama_alive:
        log("AI", "Ollama not reachable - using fallback for all products", "WARN")
        result = _apply_fallback_all(query, products, "fallback_ollama_unavailable")
        _save_qwen_filter_debug(search_id, query, products, result, "unavailable", 0, 0)
        return result, "unavailable"

    # ── Per-product Qwen calls ───────────────────────────────────────────────
    examples = get_recent_examples(query)
    feedback_items = get_recent_feedback(query)
    log("AI", f"Qwen filter: {len(products)} products, examples={len(examples)}, feedback={len(feedback_items)}", "INFO")

    valid: list[dict[str, Any]] = []
    qwen_debug: list[dict[str, Any]] = []
    consecutive_failures = 0
    qwen_ok_count = 0
    qwen_fail_count = 0
    switched_to_fallback = False

    for product in products:
        decision: dict[str, Any]

        if switched_to_fallback:
            # Qwen gave too many consecutive failures - stop trying, use fallback for rest
            decision = _fallback_score(query, product)
            decision["source"] = "fallback_qwen_consecutive_fail"
        else:
            prompt = _build_qwen_prompt(query, product, examples, feedback_items)
            ai_response = await ask_qwen(prompt, search_id)

            if ai_response and isinstance(ai_response, dict) and "relevant" in ai_response:
                # Qwen responded correctly
                decision = ai_response
                decision["source"] = "qwen"
                cats = decision.get("categories")
                if isinstance(cats, str):
                    decision["categories"] = [cats]
                elif not isinstance(cats, list):
                    decision["categories"] = []
                consecutive_failures = 0
                qwen_ok_count += 1
            else:
                # Qwen failed (500, timeout, bad JSON)
                qwen_fail_count += 1
                consecutive_failures += 1
                decision = _fallback_score(query, product)
                decision["source"] = "fallback_qwen_failed"

                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    log("AI", f"Qwen failed {consecutive_failures} times in a row. Switching all remaining to fallback.", "WARN")
                    switched_to_fallback = True

        # Attach decision metadata to product
        product["relevance_score"] = float(decision.get("confidence", FALLBACK_SCORE))
        product["ai_decision"] = decision.get("relevant", True)
        product["ai_reason"] = decision.get("reason", "")
        product["ai_categories"] = decision.get("categories", [])
        product["ai_source"] = decision.get("source", "unknown")

        kept = decision.get("relevant", True) and product["relevance_score"] >= RELEVANCE_THRESHOLD
        qwen_debug.append({
            "title": product.get("title", "")[:80],
            "decision": decision,
            "kept": kept,
        })

        if kept:
            valid.append(product)
        else:
            log("AI", f"[REJECT] {product.get('title', '')[:50]} score={product['relevance_score']:.2f}", "INFO")

    # Determine overall qwen_status
    if qwen_ok_count > 0 and qwen_fail_count == 0:
        qwen_status = "ok"
    elif qwen_ok_count > 0 and qwen_fail_count > 0:
        qwen_status = "partial"  # some worked, some failed
    else:
        qwen_status = "failed"  # everything failed, all fallback

    _save_qwen_filter_debug(search_id, query, products, valid, qwen_status, qwen_ok_count, qwen_fail_count, qwen_debug)
    log("AI", f"filter_relevance: {len(products)} in, {len(valid)} kept, qwen_status={qwen_status}", "OK")
    return valid, qwen_status


def _apply_fallback_all(
    query: str,
    products: list[dict[str, Any]],
    source: str,
) -> list[dict[str, Any]]:
    """Apply fallback scoring to all products. Returns products above threshold."""
    valid = []
    for product in products:
        decision = _fallback_score(query, product)
        decision["source"] = source
        product["relevance_score"] = float(decision["confidence"])
        product["ai_decision"] = decision["relevant"]
        product["ai_reason"] = decision["reason"]
        product["ai_categories"] = decision.get("categories", [])
        product["ai_source"] = source
        if decision["relevant"] and decision["confidence"] >= RELEVANCE_THRESHOLD:
            valid.append(product)
    return valid


def _save_qwen_filter_debug(
    search_id: str | None,
    query: str,
    products: list,
    valid: list,
    qwen_status: str,
    ok_count: int,
    fail_count: int,
    decisions: list | None = None,
) -> None:
    if not search_id:
        return
    try:
        from src.utils.debug import save_json_debug
        save_json_debug(search_id, "qwen_filter_debug.json", {
            "query": query,
            "total_input": len(products),
            "total_kept": len(valid),
            "threshold": RELEVANCE_THRESHOLD,
            "qwen_status": qwen_status,
            "qwen_ok_count": ok_count,
            "qwen_fail_count": fail_count,
            "decisions": decisions or [],
        })
    except Exception:
        pass
