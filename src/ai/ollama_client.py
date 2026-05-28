"""
Laptop-friendly Ollama /api/chat client.

This module is intentionally synchronous at the HTTP layer because requests is
stable on Windows. Async callers use chat_json_async(), which wraps the call in
asyncio.to_thread() so FastAPI progress polling can remain responsive.
"""
from __future__ import annotations

import asyncio
import json
import math
from typing import Any

import requests

from src.config import (
    AI_CLASSIFIER_MODEL,
    AI_CHAT_NUM_CTX,
    AI_CHAT_NUM_PREDICT,
    AI_CHAT_TIMEOUT_SECONDS,
    OLLAMA_BASE_URL,
    OLLAMA_TIMEOUT_SECONDS,
)
from src.utils.logger import log


CHAT_CALLS_ATTEMPTED = 0
CHAT_CALLS_SUCCEEDED = 0

FALLBACK_RESPONSE = {
    "accepted": True,
    "confidence": 0.50,
    "reason": "Classifier unavailable, accepted by safe fallback to avoid empty results",
    "category_match": "fallback",
    "decision_source": "ai_fallback",
}


def estimate_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)


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
        from src.ai.json_repair import parse_json_object

        return parse_json_object(content)
    except Exception:
        try:
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None


def _chat_payload(prompt: str, selected_model: str, use_json_format: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": selected_model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You classify marketplace search results. Return JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        "options": {
            "temperature": 0,
            "num_ctx": AI_CHAT_NUM_CTX,
            "num_predict": AI_CHAT_NUM_PREDICT,
        },
        "keep_alive": "10m",
    }
    if use_json_format:
        payload["format"] = "json"
    return payload


def _is_format_json_failure(response: requests.Response) -> bool:
    if response.status_code not in {400, 422}:
        return False
    text = str(response.text or "").lower()
    return "format" in text and "json" in text


def _post_chat(prompt: str, selected_model: str, timeout: int | None, use_json_format: bool) -> dict[str, Any]:
    result = chat_raw(prompt, selected_model, timeout=timeout, use_json_format=use_json_format)
    if not result.get("ok"):
        raise RuntimeError(str(result.get("error") or "Ollama chat failed"))
    parsed = result.get("parsed")
    if not parsed:
        raise ValueError("Ollama response was not valid JSON")
    parsed.setdefault("accepted", True)
    parsed.setdefault("confidence", 0.5)
    parsed.setdefault("reason", "AI classified product")
    parsed.setdefault("category_match", "ai")
    parsed["_fallback_used"] = False
    parsed["_model"] = selected_model
    return parsed


def chat_raw(
    prompt: str,
    model: str,
    timeout: int | None = None,
    use_json_format: bool = True,
    prompt_tokens_estimated: int | None = None,
) -> dict[str, Any]:
    global CHAT_CALLS_ATTEMPTED, CHAT_CALLS_SUCCEEDED
    effective_timeout = timeout if timeout is not None else AI_CHAT_TIMEOUT_SECONDS
    token_estimate = prompt_tokens_estimated if prompt_tokens_estimated is not None else estimate_tokens(prompt)
    attempts = 0
    last_error = ""
    use_format = bool(use_json_format)
    base_result: dict[str, Any] = {
        "ok": False,
        "model": model,
        "content": "",
        "parsed": None,
        "error": "",
        "timeout": False,
        "attempts": 0,
        "prompt_tokens_estimated": token_estimate,
        "ctx": AI_CHAT_NUM_CTX,
        "num_predict": AI_CHAT_NUM_PREDICT,
    }

    while True:
        payload = _chat_payload(prompt, model, use_format)
        CHAT_CALLS_ATTEMPTED += 1
        attempts += 1
        log(
            "AI_ORCH",
            (
                f"chat_options model={model} num_ctx={AI_CHAT_NUM_CTX} "
                f"num_predict={AI_CHAT_NUM_PREDICT} timeout={effective_timeout} "
                f"prompt_tokens_estimated={token_estimate}"
            ),
            "INFO",
        )
        log("AI_ORCH", f"POST /api/chat selected_model={model} ai_calls_attempted={CHAT_CALLS_ATTEMPTED}", "INFO")
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=effective_timeout,
            )
            if _is_format_json_failure(response) and use_format:
                last_error = response.text
                log("AI_ORCH", "format_json_failed_retrying_without_format=true", "WARN")
                use_format = False
                continue
            if response.status_code == 404 or (
                response.status_code == 400 and "not found" in response.text.lower()
            ):
                return {
                    **base_result,
                    "error": f"model not found: {model}",
                    "attempts": attempts,
                    "status_code": response.status_code,
                }
            response.raise_for_status()
            envelope = response.json()
            content = ""
            if isinstance(envelope, dict):
                message = envelope.get("message")
                content = str((message or {}).get("content") or envelope.get("response") or "")
            CHAT_CALLS_SUCCEEDED += 1
            log("AI_ORCH", f"chat_ok selected_model={model} ai_calls_succeeded={CHAT_CALLS_SUCCEEDED}", "INFO")
            return {
                **base_result,
                "ok": True,
                "content": content,
                "parsed": _parse_chat_content(envelope),
                "error": "",
                "timeout": False,
                "attempts": attempts,
                "format_json": use_format,
                "status_code": response.status_code,
            }
        except Exception as exc:
            last_error = str(exc)
            is_timeout = isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ReadTimeout)) or "timed out" in str(exc).lower()
            log(
                "AI_ORCH",
                f"chat_failed selected_model={model} ai_calls_attempted={CHAT_CALLS_ATTEMPTED} ai_calls_succeeded={CHAT_CALLS_SUCCEEDED} error={exc}",
                "WARN",
            )
            return {
                **base_result,
                "error": last_error,
                "timeout": is_timeout,
                "attempts": attempts,
                "status_code": getattr(getattr(exc, "response", None), "status_code", None),
            }


def chat_json(
    prompt: str,
    model: str | None = None,
    timeout: int | None = None,
    use_json_format: bool = True,
) -> dict[str, Any]:
    selected_model = model or AI_CLASSIFIER_MODEL

    from src.ai.model_registry import get_installed_model_name
    resolved_model = get_installed_model_name(selected_model)

    try:
        return _post_chat(prompt, resolved_model, timeout, use_json_format)
    except Exception as exc:
        log("AI", f"Ollama chat failed with {resolved_model} (base: {selected_model}): {exc}", "WARN")
        fallback_model = "llama3.2:3b"
        resolved_fallback = get_installed_model_name(fallback_model)
        if resolved_model == resolved_fallback:
            return _fallback(str(exc), resolved_model)
        try:
            return _post_chat(prompt, resolved_fallback, timeout, use_json_format)
        except Exception as fallback_exc:
            log("AI", f"Ollama fallback chat failed with {resolved_fallback} (base: {fallback_model}): {fallback_exc}", "WARN")
            return _fallback(str(fallback_exc), resolved_fallback)


async def chat_json_async(
    prompt: str,
    model: str | None = None,
    timeout: int | None = None,
    use_json_format: bool = True,
) -> dict[str, Any]:
    return await asyncio.to_thread(chat_json, prompt, model, timeout, use_json_format)


async def chat_raw_async(
    prompt: str,
    model: str,
    timeout: int | None = None,
    use_json_format: bool = True,
    prompt_tokens_estimated: int | None = None,
) -> dict[str, Any]:
    return await asyncio.to_thread(chat_raw, prompt, model, timeout, use_json_format, prompt_tokens_estimated)


def get_embedding(text: str, model: str = "nomic-embed-text") -> list[float] | None:
    try:
        from src.ai.model_registry import get_installed_model_name
        resolved_model = get_installed_model_name(model)
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": resolved_model, "prompt": text},
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        embedding = response.json().get("embedding")
        if isinstance(embedding, list):
            return [float(item) for item in embedding]
    except Exception as exc:
        log("AI_ORCH", f"embedding_failed model={model} error={exc}", "WARN")
    return None


async def get_embedding_async(text: str, model: str = "nomic-embed-text") -> list[float] | None:
    return await asyncio.to_thread(get_embedding, text, model)


def cosine_similarity(a: list[float] | None, b: list[float] | None) -> float | None:
    if not a or not b or len(a) != len(b):
        return None
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a <= 0 or norm_b <= 0:
        return None
    return max(0.0, min(1.0, (dot / (norm_a * norm_b) + 1.0) / 2.0))
