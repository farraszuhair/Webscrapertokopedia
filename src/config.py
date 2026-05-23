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


AI_ORCHESTRATION_ENABLED = os.getenv("AI_ORCHESTRATION_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
AI_CPU_MODE = os.getenv("AI_CPU_MODE", "true").strip().lower() not in {"0", "false", "no", "off"}

ALLOWED_OLLAMA_MODELS = [
    "gemma3:4b",
    "llama3.2:3b",
    "phi4-mini",
    "nomic-embed-text",
]

AI_MODEL_JOBS = {
    "semantic": "nomic-embed-text",
    "balanced_classifier": "gemma3:4b",
    "fast_classifier": "llama3.2:3b",
    "json_repair": "phi4-mini",
}

CLASSIFIER_PRIORITY = (
    ["llama3.2:3b", "gemma3:4b"]
    if AI_CPU_MODE
    else ["gemma3:4b", "llama3.2:3b"]
)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
OLLAMA_TIMEOUT_SECONDS = _env_int("OLLAMA_TIMEOUT_SECONDS", _env_int("AI_TIMEOUT_SECONDS", 12))
AI_CLASSIFIER_MAX_PRODUCTS = max(1, _env_int("AI_CLASSIFIER_MAX_PRODUCTS", 12))
AI_CHAT_TIMEOUT_SECONDS = max(1, _env_int("AI_CHAT_TIMEOUT_SECONDS", 25))
AI_CHAT_NUM_PREDICT = max(16, _env_int("AI_CHAT_NUM_PREDICT", 80))
AI_CHAT_NUM_CTX = max(512, _env_int("AI_CHAT_NUM_CTX", 1024))
AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK = max(1, _env_int("AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK", 3))
AI_MODEL_CACHE_TTL_SECONDS = max(1, _env_int("AI_MODEL_CACHE_TTL_SECONDS", 60))

TARGET_COUNT_DEFAULT = _env_int("TARGET_COUNT_DEFAULT", 50)
OVERFETCH_MULTIPLIER = _env_int("OVERFETCH_MULTIPLIER", _env_int("SCRAPER_OVERFETCH_MULTIPLIER", 4))

RULE_ACCEPT_THRESHOLD = _env_float("RULE_ACCEPT_THRESHOLD", 0.72)
RULE_REVIEW_THRESHOLD = _env_float("RULE_REVIEW_THRESHOLD", 0.45)
RULE_REJECT_THRESHOLD = _env_float("RULE_REJECT_THRESHOLD", 0.35)
FALLBACK_EXPANSION_THRESHOLD = _env_float("FALLBACK_EXPANSION_THRESHOLD", 0.20)
LLM_ACCEPT_THRESHOLD = _env_float("LLM_ACCEPT_THRESHOLD", 0.62)

AI_BATCH_SIZE = max(1, _env_int("AI_BATCH_SIZE", 8))

FEEDBACK_FILE = Path(os.getenv("FEEDBACK_FILE", "data/feedback/product_feedback.json"))
