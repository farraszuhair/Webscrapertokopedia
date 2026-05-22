"""
test_qwen_client.py - Tests for Qwen client error handling.

These tests mock httpx so they work WITHOUT Ollama running.
The goal: verify the client NEVER crashes the scraping pipeline.

Tested:
  - HTTP 500 returns None (not exception)
  - Timeout returns None (not exception)
  - Connection refused returns None
  - Invalid JSON from model returns None
  - Valid response parsed correctly
  - check_ollama_health() returns False when Ollama is down
  - check_ollama_health() returns True when Ollama is up
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# The functions we're testing
from src.ai.qwen_client import (
    GenerateResult,
    MODEL_NAME,
    OLLAMA_GENERATE_URL,
    OllamaModelSelection,
    TIMEOUT_S,
    ask_qwen,
    check_model_loaded,
    check_ollama_health,
)


# ── Timeout constant ─────────────────────────────────────────────────────────

def test_timeout_is_laptop_realtime_friendly():
    """Realtime filtering should use a short timeout for laptop-friendly models."""
    assert TIMEOUT_S <= 30, f"TIMEOUT_S={TIMEOUT_S} is too slow for realtime borderline filtering"


def test_default_model_is_balanced_gemma():
    """The project intentionally defaults to the balanced small model."""
    assert MODEL_NAME == "gemma3:4b"


# ── ask_qwen: HTTP 500 ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_qwen_http_500_returns_none():
    """
    Ollama returns 500 when model is loading or OOM.
    ask_qwen must return None, not raise an exception.
    """
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error - model loading"

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await ask_qwen("test prompt")
        assert result is None, "HTTP 500 must return None, not raise"


@pytest.mark.asyncio
async def test_ask_qwen_http_500_does_not_raise():
    """Pipeline must NOT crash when Qwen returns 500."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = ""

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        # This must complete without exception
        try:
            result = await ask_qwen("laptop gaming relevance check")
            assert result is None
        except Exception as exc:
            pytest.fail(f"ask_qwen raised exception on HTTP 500: {exc}")


# ── ask_qwen: Timeout ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_qwen_timeout_returns_none():
    """httpx.TimeoutException must return None, not propagate."""
    import httpx

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_client_class.return_value = mock_client

        result = await ask_qwen("test prompt")
        assert result is None, "Timeout must return None, not raise"


# ── ask_qwen: Connection refused ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_qwen_connection_refused_returns_none():
    """Ollama not running = ConnectError. Must return None."""
    import httpx

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client_class.return_value = mock_client

        result = await ask_qwen("test prompt")
        assert result is None


# ── ask_qwen: Invalid JSON from model ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_qwen_invalid_json_returns_none():
    """Model output plain text instead of JSON. Must return None, not crash."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "This is a gaming laptop, very relevant.",  # plain text, not JSON
        "done": True,
    }

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await ask_qwen("test prompt")
        assert result is None, "Non-JSON model output must return None"


# ── ask_qwen: Valid response ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ask_qwen_valid_response_parsed():
    """Valid Qwen JSON response must be returned as a dict."""
    expected = {
        "relevant": True,
        "confidence": 0.92,
        "categories": ["gaming_laptop"],
        "reason": "ASUS TUF Gaming with RTX is a gaming laptop.",
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": json.dumps(expected),
        "done": True,
    }

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await ask_qwen("test prompt")
        assert result is not None
        assert result["relevant"] is True
        assert result["confidence"] == 0.92
        assert result["categories"] == ["gaming_laptop"]


# ── check_ollama_health ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_check_ollama_health_returns_false_when_down():
    """Ollama not running -> ConnectError -> health returns False, not exception."""
    import httpx

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client_class.return_value = mock_client

        result = await check_ollama_health()
        assert result is False


@pytest.mark.asyncio
async def test_check_ollama_health_returns_true_when_up():
    """Ollama running -> health returns True."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("src.ai.qwen_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await check_ollama_health()
        assert result is True


# ── filter_relevance: AI unavailable doesn't crash pipeline ─────────────────

@pytest.mark.asyncio
async def test_filter_relevance_ai_unavailable_keeps_rule_matches():
    """
    When local AI is unavailable, filter_relevance must:
    - NOT crash
    - Return (products, status)
    - Keep obvious products through deterministic rules
    """
    from src.ai.relevance import filter_relevance

    products = [
        {
            "title": "ASUS TUF Gaming F15 RTX 3050 Laptop",
            "price_raw": "Rp10.000.000",
            "price_value": 10_000_000,
            "url": "https://tokopedia.test/tuf",
            "source_engine": "puppeteer",
        },
        {
            "title": "Lenovo Legion 5 Pro",
            "price_raw": "Rp15.000.000",
            "price_value": 15_000_000,
            "url": "https://tokopedia.test/legion",
            "source_engine": "rollback",
        },
    ]

    with patch("src.ai.model_registry.requests.get", side_effect=RuntimeError("Ollama down")):
        result_products, ai_status = await filter_relevance("laptop gaming", products, use_ai=True)

        assert isinstance(result_products, list), "Must return list even when AI fails"
        assert ai_status in ("ok", "partial", "unavailable")
        assert len(result_products) > 0, "Fallback must keep at least some products"


@pytest.mark.asyncio
async def test_filter_relevance_ollama_down_uses_fallback():
    """When Ollama is down, obvious rule matches still pass."""
    from src.ai.relevance import filter_relevance

    products = [
        {
            "title": "ASUS ROG Strix G16 RTX 4060 Gaming Laptop",
            "price_raw": "Rp18.000.000",
            "price_value": 18_000_000,
            "url": "https://tokopedia.test/rog",
            "source_engine": "puppeteer",
        },
    ]

    with patch("src.ai.model_registry.requests.get", side_effect=RuntimeError("Ollama down")):
        result_products, ai_status = await filter_relevance("laptop gaming", products, use_ai=True)

        assert ai_status in ("ok", "unavailable")
        assert isinstance(result_products, list)
        # ROG laptop should survive fallback
        assert len(result_products) == 1
