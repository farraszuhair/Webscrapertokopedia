"""Detect installed Ollama models and expose AI Orchestrator capabilities."""
from __future__ import annotations

from typing import Any
import requests

from src.config import ALLOWED_OLLAMA_MODELS, AI_MODEL_JOBS, CLASSIFIER_PRIORITY, OLLAMA_BASE_URL
from src.utils.logger import log


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


def get_installed_tag_map() -> dict[str, str]:
    """Map normalized model names to the exact installed Ollama tags."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        response.raise_for_status()
        detected = _extract_model_names(response.json())
        mapping = {}
        for tag in detected:
            norm = normalize_model_name(tag)
            mapping[norm] = tag
        return mapping
    except Exception as exc:
        log("AI_ORCH", f"Ollama tag mapping failed: {exc}", "WARN")
        return {}


def get_installed_model_name(wanted: str) -> str:
    """
    Resolves an allowed model name (e.g., 'phi4-mini') to the exact installed name
    found in Ollama (e.g., 'phi4-mini:latest'). If not found or mapping fails,
    returns the original wanted name.
    """
    norm_wanted = normalize_model_name(wanted)
    mapping = get_installed_tag_map()
    if norm_wanted in mapping:
        return mapping[norm_wanted]
    return wanted


def get_installed_ollama_models() -> list[str]:
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        response.raise_for_status()
        detected = _extract_model_names(response.json())
        models = [tag for tag in detected if has_model(ALLOWED_OLLAMA_MODELS, tag)]
        ignored = [tag for tag in detected if tag not in models]
        if ignored:
            log("AI_ORCH", f"ignored_unsupported_models={ignored}", "INFO")
        log("AI_ORCH", f"installed_models={models}", "INFO")
        return models
    except Exception as exc:
        log("AI_ORCH", f"Ollama model detection unavailable: {exc}", "WARN")
        return []


def get_supported_installed_models(installed: list[str] | None = None) -> list[str]:
    installed_models = get_installed_ollama_models() if installed is None else installed
    supported = [allowed for allowed in ALLOWED_OLLAMA_MODELS if has_model(installed_models, allowed)]
    log("AI_ORCH", f"supported_models={supported}", "INFO")
    return supported


def is_model_installed(model: str) -> bool:
    return has_model(get_installed_ollama_models(), model)


def get_best_classifier_model(installed: list[str] | None = None) -> str | None:
    installed_models = get_installed_ollama_models() if installed is None else installed
    for model in CLASSIFIER_PRIORITY:
        if has_model(installed_models, model):
            return model
    return None


def get_orchestrator_status() -> dict[str, Any]:
    installed = get_installed_ollama_models()
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
