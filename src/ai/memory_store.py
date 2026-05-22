"""
memory_store.py - AI memory file paths and raw I/O helpers.

Files:
  data/ai_memory/feedback.jsonl     - raw user feedback log
  data/ai_memory/examples.jsonl     - confirmed good/bad examples for prompt
  data/ai_memory/category_rules.json - user-taught category rules

These are read by relevance.py to build AI Orchestrator prompts.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMORY_DIR = Path("data/ai_memory")
FEEDBACK_FILE = MEMORY_DIR / "feedback.jsonl"
EXAMPLES_FILE = MEMORY_DIR / "examples.jsonl"
CATEGORY_RULES_FILE = MEMORY_DIR / "category_rules.json"


def ensure_memory_dir() -> None:
    """Create memory directory and blank files if they don't exist."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    for f in (FEEDBACK_FILE, EXAMPLES_FILE):
        if not f.exists():
            f.touch()
    if not CATEGORY_RULES_FILE.exists():
        CATEGORY_RULES_FILE.write_text(
            json.dumps({"version": 1, "rules": []}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Append one record to a JSONL file. Creates file if missing."""
    ensure_memory_dir()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path, limit: int = 0) -> list[dict[str, Any]]:
    """Read all records from JSONL. If limit > 0, return last N records."""
    ensure_memory_dir()
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except FileNotFoundError:
        pass
    return records[-limit:] if limit > 0 else records


def load_category_rules() -> dict[str, Any]:
    """Load category_rules.json. Returns empty rules dict on failure."""
    ensure_memory_dir()
    try:
        return json.loads(CATEGORY_RULES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "rules": []}


def save_category_rules(data: dict[str, Any]) -> None:
    ensure_memory_dir()
    CATEGORY_RULES_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
