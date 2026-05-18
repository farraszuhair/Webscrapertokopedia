"""
qwen_client.py - Ollama Qwen 2.5:14B communication layer.

Endpoint: http://localhost:11434/api/generate
Model:    qwen2.5:14b

Root cause of Ollama 500:
  Ollama returns HTTP 500 when:
    - model is loading (cold start, takes 30-60s for 14B)
    - context window too large
    - GPU memory full

Fixes applied:
  - TIMEOUT_S = 120  (was 30, 14B model needs time on first token)
  - health_check() verifies Ollama is alive before any generate call
  - check_model_loaded() checks if model is in tags list
  - ask_qwen() catches HTTP 500 specifically and returns None (fallback)
  - Never raises exceptions. Always returns None on failure.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx

from src.utils.logger import log

import os

OLLAMA_BASE = os.getenv("OLLAMA_URL", "http://localhost:11434").replace("/api/generate", "")
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE}/api/tags"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# KEY FIX: 14B model cold start can take 60+ seconds.
# 30s was guaranteed to timeout on first call.
TIMEOUT_S = 120
HEALTH_TIMEOUT_S = 4  # short probe - if Ollama doesn't respond in 4s it's down


async def check_ollama_health() -> bool:
    """
    Check if Ollama server is reachable.
    Returns True only if we get HTTP 200 from /api/tags.
    """
    try:
        async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT_S) as client:
            response = await client.get(OLLAMA_TAGS_URL)
            return response.status_code == 200
    except Exception:
        return False


async def check_model_loaded(model_name: str = MODEL_NAME) -> bool:
    """
    Check if the required model is available in Ollama.
    Ollama returns HTTP 500 when you call generate on a model that isn't pulled.
    """
    try:
        async with httpx.AsyncClient(timeout=HEALTH_TIMEOUT_S) as client:
            response = await client.get(OLLAMA_TAGS_URL)
            if response.status_code != 200:
                return False
            tags = response.json()
            models = tags.get("models", [])
            # model name can be "qwen2.5:14b" or just appear as prefix
            return any(model_name in m.get("name", "") for m in models)
    except Exception:
        return False


async def ask_qwen(prompt: str, search_id: str | None = None) -> Optional[Dict[str, Any]]:
    """
    Send a prompt to Qwen via Ollama and return parsed JSON dict.

    Returns None on ANY failure. Caller must handle None gracefully.
    Failure cases:
      - Ollama not running (ConnectError)
      - Model not loaded (HTTP 500)
      - Timeout (14B model first token can be slow)
      - Invalid JSON response (model outputted text instead of JSON)
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        # format=json tells Ollama to enforce JSON output from the model
        "format": "json",
        # Keep context small - large context causes OOM which gives HTTP 500
        "options": {
            "num_ctx": 2048,
            "temperature": 0,
            "num_predict": 300,
        },
    }

    try:
        # Single client per call - no connection reuse needed for this use case
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
            response = await client.post(OLLAMA_GENERATE_URL, json=payload)

            # Ollama HTTP 500: model loading, OOM, or crash.
            # Do NOT retry here - caller decides whether to retry or fallback.
            if response.status_code == 500:
                error_body = response.text[:500]
                log("QWEN", f"Ollama HTTP 500: {error_body}", "WARN")
                _save_qwen_error(search_id, {
                    "endpoint": OLLAMA_GENERATE_URL,
                    "model": MODEL_NAME,
                    "timeout": TIMEOUT_S,
                    "status_code": 500,
                    "response_text": error_body,
                    "error": "Ollama returned HTTP 500 - model may be loading or OOM",
                })
                return None

            if response.status_code != 200:
                log("QWEN", f"Ollama HTTP {response.status_code}", "WARN")
                return None

            # Parse the outer Ollama response envelope
            try:
                data = response.json()
            except Exception as exc:
                log("QWEN", f"Ollama response not JSON: {exc}", "WARN")
                return None

            response_text = data.get("response", "")

            # Parse the inner model output as JSON
            try:
                # Try to extract JSON between { and }
                import re
                match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict):
                        return parsed
                parsed = json.loads(response_text)
                if not isinstance(parsed, dict):
                    log("QWEN", f"Qwen returned non-dict JSON: {type(parsed)}", "WARN")
                    return None
                return parsed
            except json.JSONDecodeError as exc:
                log("QWEN", f"Qwen returned invalid JSON: {response_text[:300]} | err={exc}", "WARN")
                _save_qwen_error(search_id, {
                    "endpoint": OLLAMA_GENERATE_URL,
                    "model": MODEL_NAME,
                    "timeout": TIMEOUT_S,
                    "status_code": 200,
                    "response_text": response_text[:1000],
                    "error": f"JSON decode failed: {exc}",
                })
                return None

    except httpx.ConnectError:
        log("QWEN", "Ollama not running or not reachable at localhost:11434", "WARN")
        return None
    except httpx.TimeoutException:
        log("QWEN", f"Qwen timeout after {TIMEOUT_S}s (model still loading?)", "WARN")
        _save_qwen_error(search_id, {
            "endpoint": OLLAMA_GENERATE_URL,
            "model": MODEL_NAME,
            "timeout": TIMEOUT_S,
            "status_code": None,
            "response_text": "",
            "error": f"httpx.TimeoutException after {TIMEOUT_S}s",
        })
        return None
    except Exception as exc:
        log("QWEN", f"Unexpected Qwen error: {exc}", "WARN")
        return None


def _save_qwen_error(search_id: str | None, payload: dict[str, Any]) -> None:
    """
    Write Qwen error to data/debug/{search_id}/qwen_error.json.
    Silently skips if no search_id or file write fails.
    """
    if not search_id:
        return
    try:
        from src.utils.debug import save_json_debug
        save_json_debug(search_id, "qwen_error.json", payload)
    except Exception:
        pass
