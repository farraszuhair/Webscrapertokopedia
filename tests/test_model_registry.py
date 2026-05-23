from __future__ import annotations

from src.ai import model_registry


class DummyResponse:
    def __init__(self, payload, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_ai_status_when_no_models(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse({"models": []}))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["ok"] is False
    assert status["classifier"] is None
    assert status["supported"] == []
    assert "gemma3:4b" in status["missing"]
    assert "ollama pull gemma3:4b" in status["install_commands"]


def test_ai_status_filters_to_allowed_models(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    payload = {
        "models": [
            {"name": "gemma3:4b"},
            {"name": "llama3.2:3b"},
            {"name": "unsupported-large:latest"},
        ]
    }
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["ok"] is True
    assert status["classifier"] == "llama3.2:3b"
    assert status["supported"] == ["gemma3:4b", "llama3.2:3b"]
    assert "unsupported-large:latest" not in status["supported"]


def test_ai_status_uses_llama_when_gemma_missing(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    payload = {"models": [{"name": "llama3.2:3b"}, {"name": "nomic-embed-text"}]}
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["classifier"] == "llama3.2:3b"
    assert status["capabilities"]["semantic"] is True
    assert status["capabilities"]["balanced_classifier"] is False


def test_ai_status_normalizes_latest_tags(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    payload = {
        "models": [
            {"name": "nomic-embed-text:latest"},
            {"name": "phi4-mini:latest"},
            {"name": "llama3.2:3b"},
            {"name": "gemma3:4b"},
        ]
    }
    monkeypatch.setattr(model_registry.requests, "get", lambda *args, **kwargs: DummyResponse(payload))

    status = model_registry.get_orchestrator_status(force_refresh=True)

    assert status["ok"] is True
    assert status["classifier"] == "llama3.2:3b"
    assert status["missing"] == []
    assert status["capabilities"] == {
        "semantic": True,
        "balanced_classifier": True,
        "fast_classifier": True,
        "json_repair": True,
    }


def test_model_registry_caches_tags(monkeypatch):
    model_registry._MODEL_CACHE["timestamp"] = 0
    model_registry._MODEL_CACHE["models"] = []
    calls = []
    payload = {"models": [{"name": "llama3.2:3b"}]}

    def fake_get(*args, **kwargs):
        calls.append((args, kwargs))
        return DummyResponse(payload)

    monkeypatch.setattr(model_registry.requests, "get", fake_get)

    first = model_registry.get_installed_ollama_models(force_refresh=True)
    second = model_registry.get_installed_ollama_models()

    assert first == ["llama3.2:3b"]
    assert second == ["llama3.2:3b"]
    assert len(calls) == 1
