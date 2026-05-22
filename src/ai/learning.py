"""
learning.py - Save and retrieve user feedback for Qwen learning.

Feedback payload from frontend:
{
  "query": "laptop gaming",
  "product": {...},
  "ai_decision": {...},
  "correction": "should_exclude",
  "categories": ["mouse", "not_laptop", "should_exclude"],
  "note": "This is a mouse, not a laptop."
}

Saved to:
  data/ai_memory/feedback.jsonl     - all feedback
  data/ai_memory/examples.jsonl     - examples used for Qwen prompts
  data/ai_memory/category_rules.json - evolving category rules

Reset via POST /api/ai/reset (clears these files, not the Ollama model).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import FEEDBACK_FILE as PRODUCT_FEEDBACK_FILE
import src.ai.memory_store as memory_store
from src.ai.memory_store import (
    CATEGORY_RULES_FILE,
    EXAMPLES_FILE,
    FEEDBACK_FILE,
    append_jsonl,
    ensure_memory_dir,
    load_category_rules,
    read_jsonl,
    save_category_rules,
)
from src.utils.logger import log


def save_feedback(
    query: str,
    product_id: str | None = None,
    product_title: str | None = None,
    user_action: str | None = None,
    selected_reasons: list[str] | None = None,
    custom_reason: str | None = None,
    corrected_label: str | None = None,
    ai_label: str | None = None,
    ai_confidence: float | None = None,
    product: dict[str, Any] | None = None,
    ai_decision: dict[str, Any] | None = None,
    correction: str | None = None,
    categories: list[str] | None = None,
    note: str | None = None,
    query_intent: str | None = None,
    feedback_type: str | None = None,
    rule_score: float | None = None,
    sort_mode: str | None = None,
) -> None:
    """
    Save full feedback record to feedback.jsonl and examples.jsonl.
    Also update category_rules.json when user teaches AI about a category.
    """
    memory_store.ensure_memory_dir()

    selected_reasons = selected_reasons if selected_reasons is not None else (categories or [])
    custom_reason = custom_reason if custom_reason is not None else (note or "")
    user_action = user_action or correction or ""
    product = product or {}
    product_title = product_title or str(product.get("title") or "")
    product_id = product_id or str(product.get("id") or product.get("url") or product_title or "unknown")
    ai_decision = ai_decision or {}
    ai_label = ai_label or ("relevan" if ai_decision.get("relevant", True) else "tidak_relevan")
    ai_confidence = ai_confidence if ai_confidence is not None else float(ai_decision.get("confidence") or 0)
    corrected_label = corrected_label or _label_from_correction(user_action, selected_reasons)
    feedback_type = feedback_type or ("positive" if corrected_label in {"relevant", "relevan"} else "negative")
    product_category = str(product.get("product_category") or product.get("category") or "")
    if not product_category:
        try:
            from src.ai.relevance import detect_product_category

            product_category = detect_product_category(product_title)
        except Exception:
            product_category = "unknown"

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "query_intent": query_intent,
        "product_id": product_id,
        "product_title": product_title,
        "product": {
            "title": product_title,
            "price": product.get("price_value") or product.get("price") or 0,
            "store": product.get("shop_name") or product.get("shop") or "",
            "url": product.get("url") or product.get("product_url") or "",
            "image": product.get("image") or product.get("image_url") or "",
        },
        "product_category": product_category,
        "feedback_type": feedback_type,
        "reasons": selected_reasons,
        "note": custom_reason,
        "rule_score": rule_score or 0.0,
        "sort_mode": sort_mode or "terbaik",
        "ai_label": ai_label,
        "ai_confidence": ai_confidence,
        "user_action": user_action,
        "selected_reasons": selected_reasons,
        "custom_reason": custom_reason,
        "corrected_label": corrected_label,
        # Backward-compatible fields used by older learning tests/debug files.
        "correction": user_action,
        "categories": selected_reasons,
        "note": custom_reason,
    }

    memory_store.append_jsonl(memory_store.FEEDBACK_FILE, record)
    _append_product_feedback_json(record)

    # Save to examples.jsonl so Qwen prompts can reference these as few-shot examples
    example = {
        "query": query,
        "title": record["product_title"],
        "label": corrected_label,
        "categories": selected_reasons,
        "reason": custom_reason or user_action,
    }
    memory_store.append_jsonl(memory_store.EXAMPLES_FILE, example)

    # Update category_rules.json for systematic patterns
    _update_category_rules(query, product_title, user_action, selected_reasons)

    log("AI_LEARN", f"Saved feedback '{user_action}' categories={selected_reasons} for: {product_title[:60]}", "OK")


def _append_product_feedback_json(record: dict[str, Any]) -> None:
    """Maintain the requested JSON feedback file alongside legacy JSONL memory."""
    PRODUCT_FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(PRODUCT_FEEDBACK_FILE.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            existing = []
    except Exception:
        existing = []
    existing.append(record)
    PRODUCT_FEEDBACK_FILE.write_text(
        json.dumps(existing[-2000:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _label_from_correction(correction: str, categories: list[str]) -> str:
    """Normalize correction to a simple label for examples."""
    if correction in ("should_include", "benar", "relevan"):
        return "relevant"
    if correction in ("should_exclude", "salah", "tidak_relevan"):
        return "not_relevant"
    return correction


def _update_category_rules(
    query: str,
    product_title: str,
    user_action: str,
    categories: list[str],
) -> None:
    """Add a category rule when user explicitly teaches the AI."""
    rules_data = memory_store.load_category_rules()
    rules = rules_data.get("rules", [])

    for cat in (categories or []):
        rule = {
            "query": query,
            "category": cat,
            "correction": user_action,
            "title_example": product_title[:80],
            "action": "exclude" if user_action in ("should_exclude", "salah", "tidak_relevan") else "include",
        }
        rules.append(rule)

    rules_data["rules"] = rules[-500:]  # keep last 500 rules
    memory_store.save_category_rules(rules_data)


def get_recent_feedback(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Get recent feedback for a specific query to inject as few-shot examples into Qwen prompts."""
    all_feedback = memory_store.read_jsonl(memory_store.FEEDBACK_FILE)
    q_lower = query.lower()
    relevant = [r for r in all_feedback if r.get("query", "").lower() == q_lower]
    return relevant[-limit:]


def get_recent_examples(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Get confirmed examples for few-shot prompting."""
    all_examples = memory_store.read_jsonl(memory_store.EXAMPLES_FILE)
    q_lower = query.lower()
    relevant = [e for e in all_examples if e.get("query", "").lower() == q_lower]
    return relevant[-limit:]
