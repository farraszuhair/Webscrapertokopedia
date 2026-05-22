"""
Detect installed Ollama models and expose AI Orchestrator capabilities.
"""
from __future__ import annotations

from typing import Any

import requests

from src.config import ALLOWED_OLLAMA_MODELS, AI_MODEL_JOBS, CLASSIFIER_PRIORITY, OLLAMA_BASE_URL
from src.utils.logger import log


def _extract_model_names(payload: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    for item in payload.get("models", []) or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if name:
            names.add(name)
    return sorted(names)


def get_installed_ollama_models() -> list[str]:
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        response.raise_for_status()
        detected = _extract_model_names(response.json())
        models = [model for model in ALLOWED_OLLAMA_MODELS if model in set(detected)]
        ignored = [model for model in detected if model not in set(ALLOWED_OLLAMA_MODELS)]
        if ignored:
            log("AI_ORCH", f"ignored_unsupported_models={ignored}", "INFO")
        log("AI_ORCH", f"installed_models={models}", "INFO")
        return models
    except Exception as exc:
        log("AI_ORCH", f"Ollama model detection unavailable: {exc}", "WARN")
        return []


def get_supported_installed_models() -> list[str]:
    installed = set(get_installed_ollama_models())
    supported = [model for model in ALLOWED_OLLAMA_MODELS if model in installed]
    log("AI_ORCH", f"supported_models={supported}", "INFO")
    return supported


def is_model_installed(model: str) -> bool:
    return model in set(get_supported_installed_models())


def get_best_classifier_model() -> str | None:
    supported = set(get_supported_installed_models())
    for model in CLASSIFIER_PRIORITY:
        if model in supported:
            return model
    return None


def get_orchestrator_status() -> dict[str, Any]:
    installed = get_installed_ollama_models()
    installed_set = set(installed)
    supported = [model for model in ALLOWED_OLLAMA_MODELS if model in installed_set]
    supported_set = set(supported)
    missing = [model for model in ALLOWED_OLLAMA_MODELS if model not in supported_set]
    classifier = next((model for model in CLASSIFIER_PRIORITY if model in supported_set), None)
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
