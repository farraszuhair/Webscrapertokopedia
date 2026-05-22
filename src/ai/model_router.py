"""
Select exactly one local LLM for a filtering run.
"""
from __future__ import annotations

from src.config import AI_FILTER_MODEL, AI_MODELS, AI_MODE


def get_ai_model(mode: str = "balanced") -> str:
    models = {
        "fast": "llama3.2:3b",
        "balanced": "gemma3:4b",
        "json": "phi4-mini",
        "accurate": "qwen2.5:14b",
    }
    selected_mode = (mode or AI_MODE or "balanced").strip().lower()
    if selected_mode == "balanced" and AI_FILTER_MODEL:
        return AI_FILTER_MODEL
    return models.get(selected_mode, AI_MODELS["balanced"])


def get_fallback_model() -> str:
    return "llama3.2:3b"
