"""
qwen_client.py - Communication with local Ollama Qwen 2.5:14B.

Endpoint: http://localhost:11434/api/generate
Model:    qwen2.5:14b

Returns strict JSON:
{
  "relevant": true,
  "confidence": 0.86,
  "categories": ["gaming_laptop"],
  "reason": "ASUS TUF Gaming is a gaming laptop."
}

On any failure: returns None. Caller uses fallback scoring. Never crashes.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

import httpx

from src.utils.logger import log

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:14b"
TIMEOUT_S = 30  # Qwen 14B can be slow on first token


async def ask_qwen(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Send a prompt to Qwen via Ollama and return parsed JSON dict.
    Returns None on any failure - caller must handle gracefully.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",  # Force strict JSON output from Ollama
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            if response.status_code != 200:
                log("AI", f"Ollama HTTP error: {response.status_code}", "WARN")
                return None

            data = response.json()
            response_text = data.get("response", "")

            try:
                parsed = json.loads(response_text)
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                log("AI", f"Qwen returned invalid JSON: {response_text[:300]}", "WARN")
                return None

    except httpx.ConnectError:
        log("AI", "Ollama not running or not reachable at localhost:11434", "WARN")
        return None
    except httpx.TimeoutException:
        log("AI", f"Qwen timeout after {TIMEOUT_S}s", "WARN")
        return None
    except Exception as exc:
        log("AI", f"Qwen connection error: {exc}", "WARN")
        return None


async def check_ollama_health() -> bool:
    """Check if Ollama is reachable. Used for startup diagnostics."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get("http://localhost:11434/api/tags")
            return response.status_code == 200
    except Exception:
        return False
