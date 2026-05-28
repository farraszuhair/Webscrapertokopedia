from __future__ import annotations

import pytest

from src.ai import ai_filter, model_registry, ollama_client
import src.ai.feedback_store as feedback_store
import src.ai.relevance as relevance
from src.ai.relevance import filter_relevance
from src.server import routes
from src.server.schemas import SearchRequest
from src.scraper.engine_selector import EngineRunResult
from src.utils.eta import ETACalculator


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

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        products[0]["_audit_id"] = "p1"
        calls.append({"args": args, "kwargs": kwargs})
        return {
            "ok": True,
            "items": [{
                "id": "p1",
                "accepted": True,
                "confidence": 0.72,
                "reason": "Borderline accessory matched query intent",
                "category_match": "accessory",
                "decision_source": "ai_orchestrator",
            }],
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)

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
    assert captured["payload"]["options"]["num_ctx"] == 4096
    assert captured["payload"]["options"]["num_predict"] == 180
    assert captured["payload"]["keep_alive"] == "10m"
    assert captured["timeout"] == 75


def test_cpu_mode_does_not_override_classifier_priority():
    assert model_registry.get_best_classifier_model(["llama3.2:3b", "gemma3:4b"]) == "gemma3:4b"


@pytest.mark.asyncio
async def test_cpu_mode_selects_gemma_and_posts_gemma_to_chat(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0.0
    model_registry._MODEL_CACHE["models"] = []
    monkeypatch.setattr(model_registry, "CLASSIFIER_PRIORITY", ["gemma3:4b", "llama3.2:3b"])
    monkeypatch.setattr(ai_filter, "AI_CPU_MODE", True)
    monkeypatch.setattr(ai_filter, "AI_AUDIT_MAX_PRODUCTS", 3)
    monkeypatch.setattr(ai_filter, "AI_BATCH_SIZE", 3)
    monkeypatch.setattr(ai_filter, "AI_CHAT_NUM_CTX", 4096)
    monkeypatch.setattr(ai_filter, "AI_CHAT_NUM_PREDICT", 180)
    monkeypatch.setattr(ai_filter, "AI_CHAT_TIMEOUT_SECONDS", 75)
    monkeypatch.setattr(ollama_client, "AI_CHAT_NUM_CTX", 4096)
    monkeypatch.setattr(ollama_client, "AI_CHAT_NUM_PREDICT", 180)
    monkeypatch.setattr(ollama_client, "AI_CHAT_TIMEOUT_SECONDS", 75)

    captured = {}
    log_messages = []

    def recording_log(tag, msg, level="INFO"):
        log_messages.append((tag, msg, level))
        print(f"[{tag}] {msg}", flush=True)

    monkeypatch.setattr(ai_filter, "log", recording_log)
    monkeypatch.setattr(ollama_client, "log", recording_log)

    class TagsResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"models": [{"name": "llama3.2:3b"}, {"name": "gemma3:4b"}]}

    class ChatResponse:
        status_code = 200
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": '{"items":[{"id":"borderline-gemma","accepted":true,"confidence":0.8,"reason":"ok","category_match":"match"}]}'}}

    def fake_get(url, timeout):
        assert url.endswith("/api/tags")
        return TagsResponse()

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["payload"] = json
        captured["timeout"] = timeout
        return ChatResponse()

    monkeypatch.setattr(model_registry.requests, "get", fake_get)
    monkeypatch.setattr(ollama_client.requests, "post", fake_post)
    monkeypatch.setattr(relevance, "detect_query_intent", lambda query: "main_product")
    monkeypatch.setattr(relevance, "detect_product_category", lambda product: "main_product")
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: 0.55)
    monkeypatch.setattr(relevance, "apply_laptop_gaming_boost", lambda query, product, score: score)
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(feedback_store, "extract_query_constraints", lambda *args, **kwargs: {})
    monkeypatch.setattr(feedback_store, "load_feedback_context", lambda *args, **kwargs: {"feedback_examples_loaded": 0})
    monkeypatch.setattr(feedback_store, "load_learned_patterns", lambda *args, **kwargs: [])
    monkeypatch.setattr(feedback_store, "compute_constraint_mismatch_penalty", lambda *args, **kwargs: (0.0, []))
    monkeypatch.setattr(feedback_store, "compute_learned_adjustment", lambda *args, **kwargs: (0.0, []))

    result = await filter_relevance(
        "office laptop",
        [{
            "id": "borderline-gemma",
            "title": "Budget office laptop",
            "price": 9_500_000,
            "price_value": 9_500_000,
            "url": "https://tokopedia.test/borderline-gemma",
            "_requested_target": 1,
        }],
        use_ai=True,
    )

    assert result.meta["classifier_checked"] == 1
    assert captured["url"].endswith("/api/chat")
    assert captured["payload"]["model"] == "gemma3:4b"
    assert captured["timeout"] == 75
    assert captured["payload"]["options"]["num_ctx"] == 4096
    assert captured["payload"]["options"]["num_predict"] == 180
    assert ("AI_ORCH", "selected_classifier=gemma3:4b cpu_mode=true ctx=4096 predict=180 timeout=75 batch=true max_products=3", "INFO") in log_messages
    assert any(
        tag == "AI_ORCH" and msg.startswith("chat_options model=gemma3:4b num_ctx=4096 num_predict=180 timeout=75")
        for tag, msg, _level in log_messages
    )
    assert any(
        tag == "AI_ORCH" and msg.startswith("POST /api/chat selected_model=gemma3:4b")
        for tag, msg, _level in log_messages
    )


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
async def test_laptop_gaming_pipeline_keeps_rtx_bundle_and_ai_checks_borderline(monkeypatch):
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
    monkeypatch.setattr(
        routes,
        "get_orchestrator_status",
        lambda: {
            "classifier": "gemma3:4b",
            "capabilities": {"semantic": False, "json_repair": False},
        },
    )
    monkeypatch.setattr(feedback_store, "load_learned_patterns", lambda *args, **kwargs: [])
    monkeypatch.setattr(feedback_store, "load_feedback_context", lambda *args, **kwargs: {"feedback_examples_loaded": 0})

    calls = []

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        calls.append(products)
        items = []
        for product in products:
            product["_audit_id"] = str(product.get("id"))
            items.append({
                "id": str(product.get("id")),
                "accepted": True,
                "confidence": 0.78,
                "reason": "borderline laptop accepted",
                "category_match": "main_product",
                "decision_source": "ai_orchestrator",
            })
        return {
            "ok": True,
            "items": items,
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 465,
            "truncated_by_app": False,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)

    invalid_pages = [
        {"title": "Mulai Berjualan", "price_raw": "", "price_value": 0, "url": "https://seller.tokopedia.com/edu/topic/mulai-bisnis/materi-seller-baru/"},
        {"title": "Kalkulator Indeks Masa Tubuh", "price_raw": "", "price_value": 0, "url": "https://www.tokopedia.com/blog/bmi/"},
        {"title": "Daftar Mall", "price_raw": "", "price_value": 0, "url": "https://seller.tokopedia.com/edu/official-store/"},
    ]
    olacom = {
        "title": (
            "OLACOM Laptop Gaming NVIDIA GeForce RTX 3050 Intel Core i5 13420H "
            "16GB RAM 512GB /1TB SSD 16.0 WUXGA 300Hz Free Tas Laptop"
        ),
        "price_raw": "Rp 12.000.000",
        "price_value": 12_000_000,
        "url": "https://www.tokopedia.com/ola-com/olacom-laptop-gaming-rtx-3050",
    }
    borderline = {
        "title": "Laptop bekas murah",
        "price_raw": "Rp 4.500.000",
        "price_value": 4_500_000,
        "url": "https://www.tokopedia.com/test/laptop-bekas-borderline",
    }
    fillers = [
        {
            "title": f"ASUS TUF Gaming Laptop RTX 3050 Core i5 16GB RAM 512GB SSD Unit {index}",
            "price_raw": f"Rp {10_000_000 + index:,}".replace(",", "."),
            "price_value": 10_000_000 + index,
            "url": f"https://www.tokopedia.com/test/asus-tuf-{index}",
        }
        for index in range(48)
    ]

    filtered = await routes._filter_pipeline(
        "test-laptop-gaming",
        SearchRequest(query="laptop gaming", target_count=50, use_ai=True),
        [*invalid_pages, olacom, borderline, *fillers],
        ETACalculator(),
        "puppeteer",
        overfetch_meta={},
    )

    metadata = filtered["metadata"]
    olacom_result = next(product for product in filtered["ai_valid"] if product["title"].startswith("OLACOM"))

    assert calls
    assert len(calls[0]) == 3
    assert metadata["ai_calls_attempted"] == 1
    assert metadata["ai_calls_succeeded"] == 1
    assert metadata["ai_checked"] == 3
    assert metadata["ai_accepted"] == 3
    assert metadata["prompt_truncated_by_app"] is False
    assert metadata["ctx"] == 4096
    assert metadata["invalid_non_product_removed"] == 3
    assert metadata["candidate_pool_count"] == 50
    assert metadata["target_display"] == 50
    assert metadata["displayed"] == 50
    assert olacom_result["decision_source"] != "rule_reject"
    assert olacom_result["product_constraints"]["category"] == "laptop"


@pytest.mark.asyncio
async def test_overfetch_loads_more_when_valid_pool_is_below_requested(monkeypatch):
    calls = []

    def product(index: int) -> dict:
        return {
            "title": f"ASUS TUF Gaming Laptop RTX 3050 Core i5 Unit {index}",
            "price_raw": f"Rp {10_000_000 + index:,}".replace(",", "."),
            "price_value": 10_000_000 + index,
            "url": f"https://www.tokopedia.com/test/overfetch-{index}",
        }

    async def fake_run_engine(search_id, engine_name, query, raw_target, eta_calc):
        calls.append({
            "search_id": search_id,
            "engine_name": engine_name,
            "query": query,
            "raw_target": raw_target,
        })
        return EngineRunResult(
            engine=engine_name,
            ok=True,
            opened_real_page=True,
            products=[product(49)],
        )

    monkeypatch.setattr(routes, "run_engine", fake_run_engine)

    raw_products, meta = await routes._overfetch_raw_products(
        "test-overfetch",
        SearchRequest(query="laptop gaming", target_count=50, use_ai=True),
        [product(index) for index in range(49)],
        "puppeteer",
        50,
        ETACalculator(),
    )

    snapshot = routes._candidate_pool_snapshot(
        raw_products,
        SearchRequest(query="laptop gaming", target_count=50, use_ai=True),
        "puppeteer",
    )

    assert calls
    assert meta["overfetch_attempted"] is True
    assert meta["overfetch_initial_valid_pool"] == 49
    assert meta["overfetch_final_valid_pool"] == 50
    assert meta["overfetch_rounds"] == 1
    assert meta["overfetch_max_raw"] == 500
    assert meta["overfetch_stop_reason"] == "target_met"
    assert snapshot["candidate_pool_count"] == 50


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
            "title": f"Budget electronics candidate {index}",
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
            "title": f"Safe budget electronics candidate {index}",
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
async def test_classifier_limit_sends_only_top_four_borderline_products(monkeypatch):
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

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        calls.extend(product["id"] for product in products)
        items = []
        for product in products:
            product["_audit_id"] = product["id"]
            items.append({
                "id": product["id"],
                "accepted": True,
                "confidence": 0.70,
                "reason": "classified",
                "category_match": "main",
                "decision_source": "ai_orchestrator",
            })
        return {
            "ok": True,
            "items": items,
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)
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

    assert len(calls) == 3
    assert result.meta["classifier_checked"] == 3
    assert result.meta["ai_calls_attempted"] == 1
    assert result.meta["fallback_added"] == 17
    assert result.meta["displayed"] == 20
    assert any(product["decision_source"] == "fallback_not_classified_cpu_limit" for product in result.products)


@pytest.mark.asyncio
async def test_ai_reject_cannot_drop_positive_laptop_evidence(monkeypatch):
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

    async def fake_classify_batch(*args, **kwargs):
        products = args[2]
        products[0]["_audit_id"] = "p1"
        return {
            "ok": True,
            "items": [{
                "id": "p1",
                "accepted": False,
                "confidence": 0.90,
                "reason": "fake rejection",
                "category_match": "no",
                "decision_source": "ai_orchestrator",
            }],
            "_chat_ok": True,
            "_fallback_used": False,
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)
    monkeypatch.setattr(relevance, "compute_rule_score", lambda query, product, intent=None: 0.72)
    monkeypatch.setattr(relevance, "apply_laptop_gaming_boost", lambda query, product, score: score)
    monkeypatch.setattr(relevance, "is_obvious_junk_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(relevance, "is_obvious_match_for_intent", lambda query, product, intent=None: False)
    monkeypatch.setattr(feedback_store, "extract_query_constraints", lambda *args, **kwargs: {})
    monkeypatch.setattr(feedback_store, "load_feedback_context", lambda *args, **kwargs: {"feedback_examples_loaded": 0})
    monkeypatch.setattr(feedback_store, "load_learned_patterns", lambda *args, **kwargs: [])
    monkeypatch.setattr(feedback_store, "compute_constraint_mismatch_penalty", lambda *args, **kwargs: (0.0, []))
    monkeypatch.setattr(feedback_store, "compute_learned_adjustment", lambda *args, **kwargs: (0.0, []))

    result = await filter_relevance(
        "laptop gaming",
        [{
            "id": "msi-modern",
            "title": "MSI Modern 14 Core i7 16GB 512GB",
            "price": 9_500_000,
            "price_value": 9_500_000,
            "url": "https://tokopedia.test/msi-modern",
            "_requested_target": 1,
            "_budget_valid": 1,
        }],
        use_ai=True,
    )

    assert result.meta["displayed"] == 1
    assert result.meta["ai_rejected"] == 1
    assert result.products[0]["decision_source"] == "fallback_after_ai_reject_positive_laptop"


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

    async def fake_classify_batch(*args, **kwargs):
        return {
            "ok": False,
            "items": [],
            "_chat_ok": False,
            "_fallback_used": True,
            "_timeout": True,
            "_error": "timeout",
            "attempts": 1,
            "prompt_tokens_estimated": 600,
            "ctx": 4096,
        }

    monkeypatch.setattr(ai_filter, "classify_product_batch", fake_classify_batch)
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

    assert result.meta["classifier_checked"] == 0
    assert result.meta["ai_calls_attempted"] == 1
    assert result.meta["ai_timeouts"] == 1
    assert result.meta["ai_circuit_open"] is True
    assert result.meta["ai_skip_reason"] == "Gemma classifier timeout/failure, used rule+learning fallback"
    assert result.meta["displayed"] == 10
    assert len(result.products) == 10
