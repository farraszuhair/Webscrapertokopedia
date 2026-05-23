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
    assert captured["payload"]["options"]["num_ctx"] == 1024
    assert captured["payload"]["options"]["num_predict"] == 80
    assert captured["payload"]["keep_alive"] == "10m"
    assert captured["timeout"] == 20


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


@pytest.mark.asyncio
async def test_fallback_expansion_fills_from_twenty_five_to_requested_fifty(monkeypatch):
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: product["score"] >= 0.78)

    candidates = []
    for index in range(64):
        score = 0.82 if index < 25 else 0.20
        candidates.append({
            "id": f"p-{index}",
            "title": f"Budget gaming laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/fill-{index}",
            "_requested_target": 50,
            "_budget_valid": 64,
            "score": score,
        })

    result = await filter_relevance("laptop gaming", candidates, use_ai=False)

    assert len(result.products) == 50
    assert result.meta["displayed"] == 50
    assert result.meta["fallback_added"] == 25
    assert result.meta["candidate_pool"] == 64


@pytest.mark.asyncio
async def test_requested_fifty_fills_from_weak_safe_candidates(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": False,
            "installed": [],
            "supported": [],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": False, "fast_classifier": False, "json_repair": False},
            "classifier": None,
            "message": "rules only",
        },
    )
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: product["score"] >= 0.78)

    candidates = []
    for index in range(50):
        score = 0.82 if index < 21 else 0.01
        candidates.append({
            "id": f"p-{index}",
            "title": f"Safe budget gaming laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/weak-fill-{index}",
            "_requested_target": 50,
            "_budget_valid": 50,
            "score": score,
        })

    result = await filter_relevance("laptop gaming", candidates, use_ai=False)

    assert len(result.products) == 50
    assert result.meta["target_display"] == 50
    assert result.meta["displayed"] == 50
    assert result.meta["accepted_before_fallback"] == 21
    assert result.meta["fallback_added"] == 29
    assert result.meta["weak_fallback_candidates_count"] == 29
    assert result.meta["ai_checked"] == 0
    assert result.meta["ai_skip_reason"] == "AI disabled"


@pytest.mark.asyncio
async def test_classifier_limit_sends_only_top_six_borderline_products(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["llama3.2:3b"],
            "supported": ["llama3.2:3b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": False, "fast_classifier": True, "json_repair": False},
            "classifier": "llama3.2:3b",
            "message": "AI Orchestrator ready",
        },
    )
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: product["score"])
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)

    calls = []

    async def fake_classify(*args, **kwargs):
        calls.append(args[2]["id"])
        return {
            "accepted": True,
            "confidence": 0.70,
            "reason": "classified",
            "category_match": "main",
            "decision_source": "ai_orchestrator",
            "_chat_ok": True,
            "_fallback_used": False,
        }

    monkeypatch.setattr(ai_filter, "classify_borderline_product", fake_classify)
    candidates = [
        {
            "id": f"p-{index}",
            "title": f"Budget laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/limit-{index}",
            "_requested_target": 20,
            "score": 0.55 - index * 0.001,
        }
        for index in range(20)
    ]

    result = await filter_relevance("laptop gaming", candidates, use_ai=True)

    assert len(calls) == 6
    assert result.meta["classifier_checked"] == 6
    assert result.meta["ai_calls_attempted"] == 6
    assert result.meta["fallback_added"] == 14
    assert result.meta["displayed"] == 20
    assert any(product["decision_source"] == "fallback_not_classified_cpu_limit" for product in result.products)


@pytest.mark.asyncio
async def test_classifier_circuit_breaker_turns_timeouts_into_fallback(monkeypatch):
    monkeypatch.setattr(
        ai_filter,
        "get_orchestrator_status",
        lambda: {
            "ok": True,
            "installed": ["llama3.2:3b"],
            "supported": ["llama3.2:3b"],
            "missing": [],
            "capabilities": {"semantic": False, "balanced_classifier": False, "fast_classifier": True, "json_repair": False},
            "classifier": "llama3.2:3b",
            "message": "AI Orchestrator ready",
        },
    )
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: 0.55)
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)

    async def fake_classify(*args, **kwargs):
        return {
            "accepted": True,
            "confidence": 0.50,
            "reason": "Classifier unavailable, accepted by safe fallback to avoid empty results",
            "category_match": "fallback",
            "decision_source": "ai_fallback",
            "_chat_ok": False,
            "_fallback_used": True,
            "_timeout": True,
        }

    monkeypatch.setattr(ai_filter, "classify_borderline_product", fake_classify)
    candidates = [
        {
            "id": f"p-{index}",
            "title": f"Budget laptop {index}",
            "price": 9_500_000 + index,
            "price_value": 9_500_000 + index,
            "url": f"https://tokopedia.test/timeout-{index}",
            "_requested_target": 10,
        }
        for index in range(10)
    ]

    result = await filter_relevance("laptop gaming", candidates, use_ai=True)

    assert result.meta["classifier_checked"] == 2
    assert result.meta["ai_calls_attempted"] == 2
    assert result.meta["ai_timeouts"] == 2
    assert result.meta["ai_circuit_open"] is True
    assert result.meta["ai_skip_reason"] == "AI classifier circuit breaker opened for this search"
    assert result.meta["displayed"] == 10
    assert len(result.products) == 10
