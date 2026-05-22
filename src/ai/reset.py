"""
reset.py - Reset AI learning files only.

POST /api/ai/reset clears:
  data/ai_memory/feedback.jsonl
  data/ai_memory/examples.jsonl
  data/ai_memory/category_rules.json

Does NOT touch Ollama or any local model.
"""
from __future__ import annotations

import json

import src.ai.memory_store as memory_store
from src.config import FEEDBACK_FILE as PRODUCT_FEEDBACK_FILE
from src.utils.logger import log


def reset_ai_memory() -> bool:
    """
    Clear all AI learning files. Returns True on success.
    Ollama model is NOT touched.
    """
    try:
        memory_store.ensure_memory_dir()

        # Clear JSONL files
        memory_store.FEEDBACK_FILE.write_text("", encoding="utf-8")
        memory_store.EXAMPLES_FILE.write_text("", encoding="utf-8")
        PRODUCT_FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        PRODUCT_FEEDBACK_FILE.write_text("[]", encoding="utf-8")

        # Reset category rules to empty
        memory_store.CATEGORY_RULES_FILE.write_text(
            json.dumps({"version": 1, "rules": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        log("AI_RESET", "AI memory cleared: feedback.jsonl, product_feedback.json, examples.jsonl, category_rules.json", "OK")
        return True

    except Exception as exc:
        log("AI_RESET", f"Reset failed: {exc}", "ERROR")
        return False
