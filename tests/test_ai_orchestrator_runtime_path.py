from __future__ import annotations

import pytest

from src.ai import ai_filter, ollama_client
import src.ai.relevance as relevance
from src.ai.relevance import filter_relevance


@pytest.mark.asyncio
async def test_borderline_product_calls_ai_orchestrator(monkeypatch):
    calls = []

    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["gemma3:4b"],
            "supported": ["gemma3:4b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": True, "fast_classifier": False, "json_repair": False},
            "classifier": "gemma3:4b",
            "message": "AI Orchestrator ready",
        },
    )

    async def fake_classify(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        return {
            "accepted": True,
            "confidence": 0.72,
            "reason": "Borderline accessory matched query intent",
            "category_match": "accessory",
            "decision_source": "ai_orchestrator",
            "_chat_ok": True,
            "_fallback_used": False,
        }

    monkeypatch.setattr(ai_filter, "classify_borderline_product", fake_classify)

    products, status = await filter_relevance(
        "charger iphone",
        [{"title": "Adapter USB C 20W", "price": 99000, "price_value": 99000, "url": "https://tokopedia.test/adapter"}],
        use_ai=True,
    )

    assert status == "ok"
    assert calls
    assert products[0]["decision_source"] == "ai_orchestrator"
    assert products[0]["confidence"] >= 0.62


def test_chat_raw_posts_to_ollama_chat(monkeypatch):
    captured = {}

    class DummyResponse:
        status_code = 200
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": '{"accepted": true, "confidence": 0.8, "reason": "ok", "category_match": "match"}'}}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["payload"] = json
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setattr(ollama_client.requests, "post", fake_post)

    result = ollama_client.chat_raw("prompt", model="gemma3:4b")

    assert result["ok"] is True
    assert captured["url"].endswith("/api/chat")
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["messages"][0]["role"] == "system"
    assert captured["payload"]["messages"][1]["role"] == "user"
    assert captured["payload"]["options"]["temperature"] == 0


@pytest.mark.asyncio
async def test_fallback_expansion_fills_toward_candidate_pool(monkeypatch):
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: product["score"] >= 0.72)

    candidates = []
    for index in range(45):
        score = 0.8 if index < 19 else 0.21
        candidates.append({
            "id": f"p-{index}",
            "title": f"Budget laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/p-{index}",
            "_requested_target": 50,
            "score": score,
        })

    result = await filter_relevance("laptop gaming", candidates, use_ai=False)

    assert len(result.products) == 45
    assert result.meta["displayed"] == 45
    assert result.meta["fallback_added"] == 26
