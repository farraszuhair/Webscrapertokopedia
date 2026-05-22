"""
Laptop-friendly Ollama /api/chat client.

This module is intentionally synchronous at the HTTP layer because requests is
stable on Windows. Async callers use chat_json_async(), which wraps the call in
asyncio.to_thread() so FastAPI progress polling can remain responsive.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

import requests

from src.ai.model_router import get_ai_model, get_fallback_model
from src.config import OLLAMA_BASE_URL, OLLAMA_TIMEOUT_SECONDS
from src.utils.logger import log


FALLBACK_RESPONSE = {
    "accepted": True,
    "confidence": 0.50,
    "reason": "AI unavailable, accepted by fallback to avoid empty results",
    "category_match": "fallback",
}


def _fallback(error: str = "", model: str | None = None) -> dict[str, Any]:
    payload = dict(FALLBACK_RESPONSE)
    payload["_fallback_used"] = True
    payload["_error"] = error
    payload["_model"] = model or ""
    return payload


def _parse_chat_content(response_payload: dict[str, Any]) -> dict[str, Any] | None:
    content = ""
    message = response_payload.get("message")
    if isinstance(message, dict):
        content = str(message.get("content") or "")
    if not content:
        content = str(response_payload.get("response") or "")
    content = content.strip()
    if not content:
        return None

    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(content[start : end + 1])
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                return None
    return None


def _post_chat(prompt: str, selected_model: str, timeout: int | None, use_json_format: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": selected_model,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "options": {
            "temperature": 0,
            "num_ctx": 2048,
            "num_predict": 160,
        },
    }
    if use_json_format:
        payload["format"] = "json"

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=timeout or OLLAMA_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    parsed = _parse_chat_content(response.json())
    if not parsed:
        raise ValueError("Ollama response was not valid JSON")
    parsed.setdefault("accepted", True)
    parsed.setdefault("confidence", 0.5)
    parsed.setdefault("reason", "AI classified product")
    parsed.setdefault("category_match", "ai")
    parsed["_fallback_used"] = False
    parsed["_model"] = selected_model
    return parsed


def chat_json(
    prompt: str,
    model: str | None = None,
    timeout: int | None = None,
    use_json_format: bool = True,
) -> dict[str, Any]:
    selected_model = model or get_ai_model("balanced")

    try:
        return _post_chat(prompt, selected_model, timeout, use_json_format)
    except Exception as exc:
        log("AI", f"Ollama chat failed with {selected_model}: {exc}", "WARN")
        fallback_model = get_fallback_model()
        if selected_model == fallback_model:
            return _fallback(str(exc), selected_model)
        try:
            return _post_chat(prompt, fallback_model, timeout, use_json_format)
        except Exception as fallback_exc:
            log("AI", f"Ollama fallback chat failed with {fallback_model}: {fallback_exc}", "WARN")
            return _fallback(str(fallback_exc), fallback_model)


async def chat_json_async(
    prompt: str,
    model: str | None = None,
    timeout: int | None = None,
    use_json_format: bool = True,
) -> dict[str, Any]:
    return await asyncio.to_thread(chat_json, prompt, model, timeout, use_json_format)
