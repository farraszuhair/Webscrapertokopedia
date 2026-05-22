"""
Runtime configuration for MarketSpy AI.

Environment variables can override these defaults, but the checked-in defaults
are intentionally laptop-friendly: one small active model, short timeouts, and
rules-first filtering.
"""
from __future__ import annotations

import os
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


AI_MODE = os.getenv("AI_MODE", "balanced").strip().lower() or "balanced"

AI_MODELS = {
    "fast": "llama3.2:3b",
    "balanced": "gemma3:4b",
    "json": "phi4-mini",
    "accurate": "qwen2.5:14b",
}

AI_FILTER_MODEL = os.getenv("AI_FILTER_MODEL", AI_MODELS["balanced"]).strip() or AI_MODELS["balanced"]
AI_FAST_MODEL = os.getenv("AI_FAST_MODEL", AI_MODELS["fast"]).strip() or AI_MODELS["fast"]
AI_JSON_MODEL = os.getenv("AI_JSON_MODEL", AI_MODELS["json"]).strip() or AI_MODELS["json"]
AI_FALLBACK_MODEL = os.getenv("AI_FALLBACK_MODEL", AI_MODELS["fast"]).strip() or AI_MODELS["fast"]

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text").strip() or "nomic-embed-text"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
OLLAMA_TIMEOUT_SECONDS = _env_int("OLLAMA_TIMEOUT_SECONDS", _env_int("AI_TIMEOUT_SECONDS", 12))

TARGET_COUNT_DEFAULT = _env_int("TARGET_COUNT_DEFAULT", 50)
OVERFETCH_MULTIPLIER = _env_int("OVERFETCH_MULTIPLIER", _env_int("SCRAPER_OVERFETCH_MULTIPLIER", 4))

RULE_ACCEPT_THRESHOLD = _env_float("RULE_ACCEPT_THRESHOLD", 0.72)
RULE_REVIEW_THRESHOLD = _env_float("RULE_REVIEW_THRESHOLD", 0.45)
RULE_REJECT_THRESHOLD = _env_float("RULE_REJECT_THRESHOLD", 0.35)
LLM_ACCEPT_THRESHOLD = _env_float("LLM_ACCEPT_THRESHOLD", 0.62)

AI_BATCH_SIZE = max(1, _env_int("AI_BATCH_SIZE", 8))

FEEDBACK_FILE = Path(os.getenv("FEEDBACK_FILE", "data/feedback/product_feedback.json"))
