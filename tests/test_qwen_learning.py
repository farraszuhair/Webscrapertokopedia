"""
test_qwen_learning.py - AI feedback, multi-category, and reset tests.
"""
import json
import pytest
from pathlib import Path
import tempfile
import os


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_product(title="ASUS TUF Gaming"):
    return {
        "id": "test123",
        "title": title,
        "url": "https://tokopedia.com/shop/product",
        "price_raw": "Rp12.000.000",
        "price_value": 12_000_000,
    }


# ── Feedback Multi-Category ───────────────────────────────────────────────────

class TestFeedbackMultiCategory:
    def test_feedback_saved_with_categories(self, tmp_path, monkeypatch):
        """Feedback with multi-category must save all fields to feedback.jsonl."""
        import src.ai.memory_store as ms
        monkeypatch.setattr(ms, "MEMORY_DIR", tmp_path)
        monkeypatch.setattr(ms, "FEEDBACK_FILE", tmp_path / "feedback.jsonl")
        monkeypatch.setattr(ms, "EXAMPLES_FILE", tmp_path / "examples.jsonl")
        monkeypatch.setattr(ms, "CATEGORY_RULES_FILE", tmp_path / "category_rules.json")

        from src.ai.learning import save_feedback
        save_feedback(
            query="laptop gaming",
            product=_make_product("This is a mouse"),
            ai_decision={"relevant": True, "confidence": 0.8},
            correction="should_exclude",
            categories=["mouse", "not_laptop", "should_exclude"],
            note="This is a mouse, not a laptop.",
        )

        lines = (tmp_path / "feedback.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["correction"] == "should_exclude"
        assert "mouse" in record["categories"]
        assert "not_laptop" in record["categories"]
        assert record["note"] == "This is a mouse, not a laptop."
        assert record["product_title"] == "This is a mouse"

    def test_examples_updated(self, tmp_path, monkeypatch):
        """Patch names in learning module directly since it imports them at module level."""
        import src.ai.memory_store as ms
        import src.ai.learning as lm

        fb_file = tmp_path / "feedback.jsonl"
        ex_file = tmp_path / "examples.jsonl"
        rules_file = tmp_path / "category_rules.json"

        monkeypatch.setattr(ms, "MEMORY_DIR", tmp_path)
        monkeypatch.setattr(ms, "FEEDBACK_FILE", fb_file)
        monkeypatch.setattr(ms, "EXAMPLES_FILE", ex_file)
        monkeypatch.setattr(ms, "CATEGORY_RULES_FILE", rules_file)
        # Also patch the names as used inside learning.py
        monkeypatch.setattr(lm, "FEEDBACK_FILE", fb_file)
        monkeypatch.setattr(lm, "EXAMPLES_FILE", ex_file)
        monkeypatch.setattr(lm, "CATEGORY_RULES_FILE", rules_file)

        from src.ai.learning import save_feedback
        save_feedback(
            query="laptop gaming",
            product=_make_product("ROG Strix G15"),
            ai_decision={"relevant": False, "confidence": 0.2},
            correction="should_include",
            categories=["gaming_laptop"],
            note="This is a gaming laptop.",
        )

        lines = ex_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        ex = json.loads(lines[0])
        assert ex["label"] == "relevant"
        assert "gaming_laptop" in ex["categories"]


# ── AI Reset ─────────────────────────────────────────────────────────────────

class TestAIReset:
    def test_reset_clears_files(self, tmp_path, monkeypatch):
        import src.ai.memory_store as ms
        monkeypatch.setattr(ms, "MEMORY_DIR", tmp_path)
        feedback_file = tmp_path / "feedback.jsonl"
        examples_file = tmp_path / "examples.jsonl"
        rules_file = tmp_path / "category_rules.json"
        monkeypatch.setattr(ms, "FEEDBACK_FILE", feedback_file)
        monkeypatch.setattr(ms, "EXAMPLES_FILE", examples_file)
        monkeypatch.setattr(ms, "CATEGORY_RULES_FILE", rules_file)

        # Write some data first
        feedback_file.write_text('{"test": 1}\n', encoding="utf-8")
        examples_file.write_text('{"ex": 1}\n', encoding="utf-8")
        rules_file.write_text('{"rules": [{"x": 1}]}', encoding="utf-8")

        from src.ai.reset import reset_ai_memory
        result = reset_ai_memory()
        assert result is True

        # All cleared
        assert feedback_file.read_text(encoding="utf-8").strip() == ""
        assert examples_file.read_text(encoding="utf-8").strip() == ""
        rules = json.loads(rules_file.read_text(encoding="utf-8"))
        assert rules["rules"] == []

    def test_reset_does_not_touch_ollama(self, tmp_path, monkeypatch):
        """This test just ensures reset returns True and doesn't call any Ollama endpoint."""
        import src.ai.memory_store as ms
        monkeypatch.setattr(ms, "MEMORY_DIR", tmp_path)
        monkeypatch.setattr(ms, "FEEDBACK_FILE", tmp_path / "feedback.jsonl")
        monkeypatch.setattr(ms, "EXAMPLES_FILE", tmp_path / "examples.jsonl")
        monkeypatch.setattr(ms, "CATEGORY_RULES_FILE", tmp_path / "category_rules.json")

        from src.ai.reset import reset_ai_memory
        # If this touches Ollama it would raise ConnectionError - it must not.
        result = reset_ai_memory()
        assert result is True
