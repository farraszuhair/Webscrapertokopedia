"""
Runtime configuration for MarketSpy AI.

Environment variables can override these defaults, but the checked-in defaults
are intentionally laptop-friendly: one small active model, CPU-safe chat
settings, and rules-first filtering.
"""
from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() not in {"", "0", "false", "no", "off"}


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


AI_ORCHESTRATION_ENABLED = parse_bool(os.getenv("AI_ORCHESTRATION_ENABLED", "true"))
AI_CPU_MODE = parse_bool(os.getenv("AI_CPU_MODE", "true"))
AI_MODEL = os.getenv("AI_MODEL", os.getenv("AI_CLASSIFIER_MODEL", "gemma3:4b")).strip()
AI_CLASSIFIER_MODEL = AI_MODEL

ALLOWED_OLLAMA_MODELS = list(dict.fromkeys([
    AI_CLASSIFIER_MODEL,
    "gemma3:4b",
    "llama3.2:3b",
    "phi4-mini",
    "nomic-embed-text",
]))

AI_MODEL_JOBS = {
    "semantic": "nomic-embed-text",
    "balanced_classifier": AI_CLASSIFIER_MODEL,
    "fast_classifier": "llama3.2:3b",
    "json_repair": "phi4-mini",
}

CLASSIFIER_PRIORITY = [
    AI_CLASSIFIER_MODEL,
    "llama3.2:3b",
]

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
OLLAMA_TIMEOUT_SECONDS = _env_int("OLLAMA_TIMEOUT_SECONDS", _env_int("AI_TIMEOUT_SECONDS", 12))
AI_CHAT_TIMEOUT_SECONDS = int(os.getenv("AI_CHAT_TIMEOUT_SECONDS", "75"))
AI_CHAT_NUM_CTX = int(os.getenv("AI_CHAT_NUM_CTX", "4096"))
AI_CHAT_NUM_PREDICT = int(os.getenv("AI_CHAT_NUM_PREDICT", "180"))
AI_AUDIT_MAX_PRODUCTS = int(os.getenv("AI_AUDIT_MAX_PRODUCTS", os.getenv("AI_CLASSIFIER_MAX_PRODUCTS", "3")))
AI_CLASSIFIER_MAX_PRODUCTS = AI_AUDIT_MAX_PRODUCTS
AI_BATCH_CLASSIFY = parse_bool(os.getenv("AI_BATCH_CLASSIFY", "true"))
AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK = max(1, _env_int("AI_MAX_FAILURES_BEFORE_CIRCUIT_BREAK", 1))
AI_MODEL_CACHE_TTL_SECONDS = max(1, _env_int("AI_MODEL_CACHE_TTL_SECONDS", 300))

TARGET_COUNT_DEFAULT = _env_int("TARGET_COUNT_DEFAULT", 50)
OVERFETCH_MULTIPLIER = _env_int("OVERFETCH_MULTIPLIER", _env_int("SCRAPER_OVERFETCH_MULTIPLIER", 4))
STRICT_BUDGET_MODE = parse_bool(os.getenv("STRICT_BUDGET_MODE", "true"))
TARGET_FIRST_MODE = parse_bool(os.getenv("TARGET_FIRST_MODE", "false"))

RULE_ACCEPT_THRESHOLD = _env_float("RULE_ACCEPT_THRESHOLD", 0.76)
RULE_REVIEW_THRESHOLD = _env_float("RULE_REVIEW_THRESHOLD", 0.50)
RULE_REJECT_THRESHOLD = _env_float("RULE_REJECT_THRESHOLD", 0.30)
FALLBACK_EXPANSION_THRESHOLD = _env_float("FALLBACK_EXPANSION_THRESHOLD", 0.10)
WEAK_FALLBACK_THRESHOLD = _env_float("WEAK_FALLBACK_THRESHOLD", 0.05)
LLM_ACCEPT_THRESHOLD = _env_float("LLM_ACCEPT_THRESHOLD", 0.62)

AI_BATCH_SIZE = max(1, _env_int("AI_BATCH_SIZE", 3))

FEEDBACK_FILE = Path(os.getenv("FEEDBACK_FILE", "data/feedback/product_feedback.json"))
