"""Detect installed Ollama models and expose AI Orchestrator capabilities."""
from __future__ import annotations

import time
from typing import Any
import requests

from src.config import (
    AI_MODEL_CACHE_TTL_SECONDS,
    ALLOWED_OLLAMA_MODELS,
    AI_MODEL_JOBS,
    CLASSIFIER_PRIORITY,
    OLLAMA_BASE_URL,
)
from src.utils.logger import log


_MODEL_CACHE: dict[str, Any] = {
    "timestamp": 0.0,
    "models": [],
}


def normalize_model_name(name: str) -> str:
    """Normalize Ollama tags while preserving meaningful size tags."""
    normalized = str(name or "").strip()
    if normalized.endswith(":latest"):
        normalized = normalized[:-7]
    return normalized


def has_model(installed: list[str], wanted: str) -> bool:
    """Return True when installed tags satisfy a supported model name."""
    wanted_norm = normalize_model_name(wanted)
    return any(normalize_model_name(item) == wanted_norm for item in installed or [])


def _extract_model_names(payload: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    for item in payload.get("models", []) or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if name:
            names.add(name)
    return sorted(names)


def get_installed_tag_map(force_refresh: bool = False) -> dict[str, str]:
    """Map normalized model names to the exact installed Ollama tags."""
    mapping = {}
    for tag in get_installed_ollama_models(force_refresh=force_refresh):
        mapping[normalize_model_name(tag)] = tag
    return mapping


def get_installed_model_name(wanted: str, installed: list[str] | None = None) -> str:
    """
    Resolves an allowed model name (e.g., 'phi4-mini') to the exact installed name
    found in Ollama (e.g., 'phi4-mini:latest'). If not found or mapping fails,
    returns the original wanted name.
    """
    norm_wanted = normalize_model_name(wanted)
    source = get_installed_ollama_models() if installed is None else installed
    mapping = {normalize_model_name(tag): tag for tag in source}
    if norm_wanted in mapping:
        return mapping[norm_wanted]
    return wanted


def get_installed_ollama_models(force_refresh: bool = False) -> list[str]:
    now = time.time()
    cached = list(_MODEL_CACHE.get("models") or [])
    timestamp = float(_MODEL_CACHE.get("timestamp") or 0.0)
    if not force_refresh and timestamp > 0 and now - timestamp < AI_MODEL_CACHE_TTL_SECONDS:
        return cached

    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        response.raise_for_status()
        detected = _extract_model_names(response.json())
        models = [tag for tag in detected if has_model(ALLOWED_OLLAMA_MODELS, tag)]
        ignored = [tag for tag in detected if tag not in models]
        if ignored:
            log("AI_ORCH", f"ignored_unsupported_models={ignored}", "INFO")
        log("AI_ORCH", f"installed_models={models}", "INFO")
        _MODEL_CACHE["timestamp"] = now
        _MODEL_CACHE["models"] = list(models)
        return list(models)
    except Exception as exc:
        log("AI_ORCH", f"Ollama model detection unavailable: {exc}", "WARN")
        _MODEL_CACHE["timestamp"] = now
        return cached


def get_supported_installed_models(installed: list[str] | None = None, force_refresh: bool = False) -> list[str]:
    installed_models = get_installed_ollama_models(force_refresh=force_refresh) if installed is None else installed
    supported = [allowed for allowed in ALLOWED_OLLAMA_MODELS if has_model(installed_models, allowed)]
    log("AI_ORCH", f"supported_models={supported}", "INFO")
    return supported


def is_model_installed(model: str, force_refresh: bool = False) -> bool:
    return has_model(get_installed_ollama_models(force_refresh=force_refresh), model)


def get_best_classifier_model(installed: list[str] | None = None, force_refresh: bool = False) -> str | None:
    installed_models = get_installed_ollama_models(force_refresh=force_refresh) if installed is None else installed
    for model in CLASSIFIER_PRIORITY:
        if has_model(installed_models, model):
            return model
    return None


def get_orchestrator_status(force_refresh: bool = False) -> dict[str, Any]:
    installed = get_installed_ollama_models(force_refresh=force_refresh)
    supported = get_supported_installed_models(installed)
    supported_set = set(supported)
    missing = [model for model in ALLOWED_OLLAMA_MODELS if model not in supported_set]
    classifier = get_best_classifier_model(installed)
    capabilities = {
        "semantic": AI_MODEL_JOBS["semantic"] in supported_set,
        "balanced_classifier": AI_MODEL_JOBS["balanced_classifier"] in supported_set,
        "fast_classifier": AI_MODEL_JOBS["fast_classifier"] in supported_set,
        "json_repair": AI_MODEL_JOBS["json_repair"] in supported_set,
    }
    ok = classifier is not None
    message = "AI Orchestrator ready" if ok else "No supported Ollama model installed. Run: ollama pull gemma3:4b"
    status = {
        "ok": ok,
        "installed": installed,
        "supported": supported,
        "missing": missing,
        "capabilities": capabilities,
        "classifier": classifier,
        "message": message,
        "install_commands": [
            "ollama pull gemma3:4b",
            "ollama pull llama3.2:3b",
            "ollama pull phi4-mini",
            "ollama pull nomic-embed-text",
        ],
    }
    log(
        "AI_ORCH",
        (
            f"classifier={classifier or 'none'} semantic={capabilities['semantic']} "
            f"json_repair={capabilities['json_repair']} missing={missing}"
        ),
        "INFO",
    )
    return status
