"""
reset.py - Reset AI learning files only.

POST /api/ai/reset clears:
  data/ai_memory/feedback.jsonl
  data/ai_memory/examples.jsonl
  data/ai_memory/category_rules.json

Does NOT touch Ollama or the qwen2.5:14b model.
"""
from __future__ import annotations

import json

from src.ai.memory_store import (
    CATEGORY_RULES_FILE,
    EXAMPLES_FILE,
    FEEDBACK_FILE,
    ensure_memory_dir,
)
from src.utils.logger import log


def reset_ai_memory() -> bool:
    """
    Clear all AI learning files. Returns True on success.
    Ollama model is NOT touched.
    """
    try:
        ensure_memory_dir()

        # Clear JSONL files
        FEEDBACK_FILE.write_text("", encoding="utf-8")
        EXAMPLES_FILE.write_text("", encoding="utf-8")

        # Reset category rules to empty
        CATEGORY_RULES_FILE.write_text(
            json.dumps({"version": 1, "rules": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        log("AI_RESET", "AI memory cleared: feedback.jsonl, examples.jsonl, category_rules.json", "OK")
        return True

    except Exception as exc:
        log("AI_RESET", f"Reset failed: {exc}", "ERROR")
        return False
