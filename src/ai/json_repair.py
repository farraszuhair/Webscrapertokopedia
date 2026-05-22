"""
Parse and repair small JSON objects returned by local chat models.
"""
from __future__ import annotations

import json
import re
from typing import Any


FALLBACK_JSON = {
    "accepted": True,
    "confidence": 0.50,
    "reason": "AI unavailable, accepted by safe fallback to avoid empty results",
    "category_match": "fallback",
    "decision_source": "ai_fallback",
}


def _strip_markdown(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def _remove_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def _extract_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def parse_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    candidates = [
        text,
        _strip_markdown(text),
        _extract_object(_strip_markdown(text)),
        _remove_trailing_commas(_extract_object(_strip_markdown(text))),
    ]
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


async def repair_json_or_fallback(raw_text: str, *, phi_available: bool = False, model: str = "phi4-mini") -> dict[str, Any]:
    parsed = parse_json_object(raw_text)
    if parsed is not None:
        return parsed

    if phi_available:
        try:
            from src.ai.ollama_client import chat_raw_async

            prompt = (
                "Repair this into valid JSON only. Required keys: "
                "accepted, confidence, reason, category_match.\n\n"
                f"{raw_text[:2000]}"
            )
            result = await chat_raw_async(prompt, model=model, use_json_format=True)
            if result.get("parsed"):
                return result["parsed"]
            parsed = parse_json_object(str(result.get("content") or ""))
            if parsed is not None:
                return parsed
        except Exception:
            pass

    return dict(FALLBACK_JSON)
