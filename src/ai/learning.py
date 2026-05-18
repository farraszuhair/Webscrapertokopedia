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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    product: dict[str, Any],
    ai_decision: dict[str, Any],
    correction: str,
    categories: list[str],
    note: str = "",
) -> None:
    """
    Save full feedback record to feedback.jsonl and examples.jsonl.
    Also update category_rules.json when user teaches AI about a category.
    """
    ensure_memory_dir()

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "product_title": product.get("title", ""),
        "product_url": product.get("url", ""),
        "product_price": product.get("price_raw", ""),
        "ai_was_relevant": (ai_decision or {}).get("relevant"),
        "ai_confidence": (ai_decision or {}).get("confidence"),
        "ai_reason": (ai_decision or {}).get("reason", ""),
        "correction": correction,
        "categories": categories or [],
        "note": note,
    }

    append_jsonl(FEEDBACK_FILE, record)

    # Save to examples.jsonl so Qwen prompts can reference these as few-shot examples
    example = {
        "query": query,
        "title": record["product_title"],
        "price": record["product_price"],
        "label": _label_from_correction(correction, categories),
        "categories": categories,
        "reason": note or correction,
    }
    append_jsonl(EXAMPLES_FILE, example)

    # Update category_rules.json for systematic patterns
    _update_category_rules(query, product, correction, categories)

    log("AI_LEARN", f"Saved feedback '{correction}' categories={categories} for: {record['product_title'][:60]}", "OK")


def _label_from_correction(correction: str, categories: list[str]) -> str:
    """Normalize correction to a simple label for examples."""
    if correction in ("should_include", "benar", "relevan"):
        return "relevant"
    if correction in ("should_exclude", "salah", "tidak_relevan"):
        return "not_relevant"
    return correction


def _update_category_rules(
    query: str,
    product: dict[str, Any],
    correction: str,
    categories: list[str],
) -> None:
    """Add a category rule when user explicitly teaches the AI."""
    rules_data = load_category_rules()
    rules = rules_data.get("rules", [])

    for cat in (categories or []):
        rule = {
            "query": query,
            "category": cat,
            "correction": correction,
            "title_example": product.get("title", "")[:80],
            "action": "exclude" if correction in ("should_exclude", "salah", "tidak_relevan") else "include",
        }
        rules.append(rule)

    rules_data["rules"] = rules[-500:]  # keep last 500 rules
    save_category_rules(rules_data)


def get_recent_feedback(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Get recent feedback for a specific query to inject as few-shot examples into Qwen prompts."""
    all_feedback = read_jsonl(FEEDBACK_FILE)
    q_lower = query.lower()
    relevant = [r for r in all_feedback if r.get("query", "").lower() == q_lower]
    return relevant[-limit:]


def get_recent_examples(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Get confirmed examples for few-shot prompting."""
    all_examples = read_jsonl(EXAMPLES_FILE)
    q_lower = query.lower()
    relevant = [e for e in all_examples if e.get("query", "").lower() == q_lower]
    return relevant[-limit:]
