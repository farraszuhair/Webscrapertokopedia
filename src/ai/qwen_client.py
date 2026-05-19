"""
Ollama/Qwen client.

The scraper must only fall back after it knows why Qwen cannot run. This module
keeps the availability check, model selection, and /api/generate call explicit.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from src.utils.logger import log


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _base_url_from_env() -> str:
    raw = (
        os.getenv("OLLAMA_BASE_URL")
        or os.getenv("OLLAMA_URL")
        or "http://localhost:11434"
    ).strip()
    for suffix in ("/api/generate", "/api/tags", "/api"):
        if raw.endswith(suffix):
            raw = raw[: -len(suffix)]
    return raw.rstrip("/") or "http://localhost:11434"


OLLAMA_BASE_URL = _base_url_from_env()
OLLAMA_BASE = OLLAMA_BASE_URL  # backward compatibility for older imports
OLLAMA_GENERATE_URL = (
    os.getenv("OLLAMA_GENERATE_URL", f"{OLLAMA_BASE_URL}/api/generate")
    .strip()
    .rstrip("/")
)
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:3b").strip() or "qwen2.5:3b"
AI_ALLOW_HEAVY_MODEL = _env_bool("AI_ALLOW_HEAVY_MODEL", False)

TIMEOUT_S = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
HEALTH_TIMEOUT_S = float(os.getenv("OLLAMA_HEALTH_TIMEOUT_SECONDS", "4"))


@dataclass
class OllamaTagsResult:
    reachable: bool
    models: list[str] = field(default_factory=list)
    error: str = ""
    status_code: int | None = None


@dataclass
class OllamaModelSelection:
    ok: bool
    selected_model: str | None
    available_models: list[str]
    warning: str = ""
    reason: str = ""
    base_url: str = OLLAMA_BASE_URL
    generate_url: str = OLLAMA_GENERATE_URL


@dataclass
class GenerateResult:
    ok: bool
    data: dict[str, Any] | None = None
    raw_response: str = ""
    error: str = ""
    elapsed_seconds: float = 0.0
    model: str = MODEL_NAME


def _extract_model_names(payload: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for item in payload.get("models", []) or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if name:
            names.append(name)
    return sorted(set(names))


def _parse_model_json(response_text: str) -> tuple[dict[str, Any] | None, str]:
    text = (response_text or "").strip()
    if not text:
        return None, "empty model response"

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed, ""
        return None, f"model returned {type(parsed).__name__}, expected object"
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        fragment = text[start : end + 1]
        try:
            parsed = json.loads(fragment)
            if isinstance(parsed, dict):
                return parsed, ""
            return None, f"extracted JSON was {type(parsed).__name__}, expected object"
        except json.JSONDecodeError as exc:
            return None, f"extracted JSON decode failed: {exc}"

    return None, "no JSON object found in model response"


async def get_ollama_tags() -> OllamaTagsResult:
    """Fetch /api/tags and return exact model names."""
    log("OLLAMA", f"base_url={OLLAMA_BASE_URL}", "INFO")
    try:
        async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT_S) as client:
            response = await client.get(OLLAMA_TAGS_URL)
    except httpx.ConnectError as exc:
        msg = f"Ollama not reachable at {OLLAMA_BASE_URL}: {exc}"
        log("OLLAMA", msg, "WARN")
        return OllamaTagsResult(False, error=msg)
    except httpx.TimeoutException:
        msg = f"Ollama /api/tags timed out after {HEALTH_TIMEOUT_S}s"
        log("OLLAMA", msg, "WARN")
        return OllamaTagsResult(False, error=msg)
    except Exception as exc:
        msg = f"Ollama /api/tags failed: {exc}"
        log("OLLAMA", msg, "WARN")
        return OllamaTagsResult(False, error=msg)

    if response.status_code != 200:
        msg = f"Ollama /api/tags returned HTTP {response.status_code}"
        log("OLLAMA", msg, "WARN")
        return OllamaTagsResult(False, error=msg, status_code=response.status_code)

    try:
        payload = response.json()
    except Exception as exc:
        msg = f"Ollama /api/tags response was not JSON: {exc}"
        log("OLLAMA", msg, "WARN")
        return OllamaTagsResult(False, error=msg, status_code=response.status_code)

    models = _extract_model_names(payload)
    log("OLLAMA", f"available_models={models}", "INFO")
    return OllamaTagsResult(True, models=models, status_code=response.status_code)


async def is_ollama_model_available(model: str) -> bool:
    """Return True only when the exact model tag exists."""
    tags = await get_ollama_tags()
    return tags.reachable and model in tags.models


async def check_ollama_health() -> bool:
    """Backward-compatible health probe."""
    tags = await get_ollama_tags()
    return tags.reachable


async def check_model_loaded(model_name: str = MODEL_NAME) -> bool:
    """Backward-compatible exact model probe."""
    return await is_ollama_model_available(model_name)


async def select_ollama_model(preferred_model: str | None = None) -> OllamaModelSelection:
    """Select the configured Qwen model, with opt-in heavy-model fallback."""
    preferred = (preferred_model or MODEL_NAME).strip() or "qwen2.5:3b"
    tags = await get_ollama_tags()
    if not tags.reachable:
        warning = f"AI skipped: Ollama not reachable at {OLLAMA_BASE_URL}"
        if tags.error:
            warning = f"{warning}. {tags.error}"
        log("AI", warning, "WARN")
        return OllamaModelSelection(
            ok=False,
            selected_model=None,
            available_models=tags.models,
            warning=warning,
            reason="ollama_not_reachable",
        )

    if preferred in tags.models:
        log("OLLAMA", f"selected_model={preferred}", "INFO")
        return OllamaModelSelection(True, preferred, tags.models)

    heavy_model = "qwen2.5:14b"
    if preferred == "qwen2.5:3b" and heavy_model in tags.models:
        if AI_ALLOW_HEAVY_MODEL:
            log("OLLAMA", f"selected_model={heavy_model}", "WARN")
            return OllamaModelSelection(
                ok=True,
                selected_model=heavy_model,
                available_models=tags.models,
                warning="Using qwen2.5:14b because qwen2.5:3b is missing and AI_ALLOW_HEAVY_MODEL=true",
            )

        warning = "AI model qwen2.5:3b not found. Run: ollama pull qwen2.5:3b"
        log("AI", warning, "WARN")
        return OllamaModelSelection(
            ok=False,
            selected_model=None,
            available_models=tags.models,
            warning=warning,
            reason="model_missing",
        )

    warning = f"AI model {preferred} not found. Run: ollama pull {preferred}"
    log("AI", warning, "WARN")
    return OllamaModelSelection(
        ok=False,
        selected_model=None,
        available_models=tags.models,
        warning=warning,
        reason="model_missing",
    )


async def call_ollama_generate(
    prompt: str,
    model: str | None = None,
    search_id: str | None = None,
) -> GenerateResult:
    """Call POST /api/generate and parse the model's JSON object response."""
    selected = (model or MODEL_NAME).strip() or "qwen2.5:3b"
    payload = {
        "model": selected,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 400,
            "num_ctx": 2048,
        },
    }

    log("AI", "calling /api/generate", "INFO")
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
            response = await client.post(OLLAMA_GENERATE_URL, json=payload)
    except httpx.ConnectError as exc:
        elapsed = time.perf_counter() - started
        error = f"Ollama not reachable during generate: {exc}"
        log("AI", error, "WARN")
        return GenerateResult(False, error=error, elapsed_seconds=elapsed, model=selected)
    except httpx.TimeoutException:
        elapsed = time.perf_counter() - started
        error = f"Ollama generate timeout after {TIMEOUT_S}s"
        log("AI", error, "WARN")
        _save_qwen_error(search_id, {
            "endpoint": OLLAMA_GENERATE_URL,
            "model": selected,
            "timeout": TIMEOUT_S,
            "status_code": None,
            "response_text": "",
            "error": error,
        })
        return GenerateResult(False, error=error, elapsed_seconds=elapsed, model=selected)
    except Exception as exc:
        elapsed = time.perf_counter() - started
        error = f"Ollama generate failed: {exc}"
        log("AI", error, "WARN")
        return GenerateResult(False, error=error, elapsed_seconds=elapsed, model=selected)

    elapsed = time.perf_counter() - started
    log("AI", f"generate_elapsed={elapsed:.2f}s", "INFO")

    if response.status_code != 200:
        raw = response.text[:1000]
        error = f"Ollama generate HTTP {response.status_code}: {raw[:300]}"
        log("AI", error, "WARN")
        _save_qwen_error(search_id, {
            "endpoint": OLLAMA_GENERATE_URL,
            "model": selected,
            "timeout": TIMEOUT_S,
            "status_code": response.status_code,
            "response_text": raw,
            "error": error,
        })
        return GenerateResult(False, raw_response=raw, error=error, elapsed_seconds=elapsed, model=selected)

    try:
        envelope = response.json()
    except Exception as exc:
        raw = response.text[:1000]
        error = f"Ollama generate envelope was not JSON: {exc}"
        log("AI", error, "WARN")
        return GenerateResult(False, raw_response=raw, error=error, elapsed_seconds=elapsed, model=selected)

    response_text = str(envelope.get("response") or "")
    parsed, parse_error = _parse_model_json(response_text)
    if parsed is None:
        log("AI", f"invalid JSON from model: {parse_error}; raw={response_text[:500]}", "WARN")
        _save_qwen_error(search_id, {
            "endpoint": OLLAMA_GENERATE_URL,
            "model": selected,
            "timeout": TIMEOUT_S,
            "status_code": response.status_code,
            "response_text": response_text[:2000],
            "error": parse_error,
        })
        return GenerateResult(
            False,
            raw_response=response_text,
            error=f"invalid_json: {parse_error}",
            elapsed_seconds=elapsed,
            model=selected,
        )

    return GenerateResult(True, data=parsed, raw_response=response_text, elapsed_seconds=elapsed, model=selected)


async def ask_qwen(prompt: str, search_id: str | None = None) -> dict[str, Any] | None:
    """
    Backward-compatible wrapper used by older tests/callers.

    New code should prefer select_ollama_model() once, then call_ollama_generate()
    with the selected model to avoid repeated /api/tags probes.
    """
    result = await call_ollama_generate(prompt, MODEL_NAME, search_id)
    return result.data if result.ok else None


def _save_qwen_error(search_id: str | None, payload: dict[str, Any]) -> None:
    if not search_id:
        return
    try:
        from src.utils.debug import save_json_debug

        save_json_debug(search_id, "qwen_error.json", payload)
    except Exception:
        pass
