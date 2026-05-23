"""
test_feedback_learning.py - Test user feedback and AI learning.

Coverage:
- Feedback multi-category saved
- Reset clears AI memory files
- Learning data format correct
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

import src.ai.ai_filter as ai_filter
from src.ai.learning import save_feedback
import src.ai.feedback_store as feedback_store
from src.ai.memory_store import FEEDBACK_FILE, EXAMPLES_FILE, CATEGORY_RULES_FILE, ensure_memory_dir, read_jsonl
from src.ai.reset import reset_ai_memory


@pytest.fixture(autouse=True)
def isolate_sqlite_feedback(tmp_path, monkeypatch):
    monkeypatch.setattr(feedback_store, "FEEDBACK_DB_PATH", tmp_path / "marketspy_feedback.db")


class TestFeedbackSaving:
    """Test saving user feedback."""

    def test_save_feedback_structure(self):
        """Saved feedback should have all required fields."""
        ensure_memory_dir()

        save_feedback(
            query="laptop gaming",
            product={
                "title": "ASUS ROG Gaming Laptop",
                "url": "https://tokopedia.com/asus",
                "price_raw": "Rp 12.999.999",
            },
            ai_decision={"relevant": True, "confidence": 0.9},
            correction="should_exclude",
            categories=["mouse", "not_laptop"],
            note="This is actually a mouse, not a laptop.",
        )

        # Read the saved feedback
        feedback_lines = read_jsonl(FEEDBACK_FILE)
        assert len(feedback_lines) > 0

        last_feedback = feedback_lines[-1]
        assert last_feedback["query"] == "laptop gaming"
        assert last_feedback["product_title"] == "ASUS ROG Gaming Laptop"
        assert last_feedback["correction"] == "should_exclude"
        assert last_feedback["categories"] == ["mouse", "not_laptop"]
        assert "timestamp" in last_feedback

    def test_save_feedback_multi_category(self):
        """Feedback can have multiple category tags."""
        ensure_memory_dir()

        save_feedback(
            query="laptop",
            product={"title": "Test Product", "url": "https://t.co/p1"},
            ai_decision={},
            correction="categorize",
            categories=["gaming_laptop", "office_laptop", "should_include"],
            note="Multi-category assignment",
        )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        last = feedback_lines[-1]
        assert len(last["categories"]) >= 2
        assert "gaming_laptop" in last["categories"] or "should_include" in last["categories"]

    def test_save_feedback_empty_note(self):
        """Feedback can be saved with empty note."""
        ensure_memory_dir()

        save_feedback(
            query="laptop",
            product={"title": "Test", "url": "https://t.co/p1"},
            ai_decision={},
            correction="benar",
            categories=["gaming_laptop"],
            note="",  # empty
        )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        last = feedback_lines[-1]
        assert "note" in last


class TestAIMemoryReset:
    """Test resetting AI memory."""

    def test_reset_clears_feedback_file(self):
        """Reset should clear feedback.jsonl."""
        ensure_memory_dir()

        # Save some feedback
        save_feedback(
            query="test",
            product={"title": "Test", "url": "https://t.co/p1"},
            ai_decision={},
            correction="test",
            categories=[],
        )

        # Verify feedback was saved
        lines_before = read_jsonl(FEEDBACK_FILE)
        assert len(lines_before) > 0

        # Reset
        reset_ai_memory()

        # Verify feedback is cleared
        lines_after = read_jsonl(FEEDBACK_FILE)
        assert len(lines_after) == 0

    def test_reset_clears_examples_file(self):
        """Reset should clear examples.jsonl."""
        ensure_memory_dir()

        # Save feedback (also saves to examples)
        save_feedback(
            query="test",
            product={"title": "Test", "url": "https://t.co/p1"},
            ai_decision={},
            correction="test",
            categories=[],
        )

        lines_before = read_jsonl(EXAMPLES_FILE)
        assert len(lines_before) > 0

        reset_ai_memory()

        lines_after = read_jsonl(EXAMPLES_FILE)
        assert len(lines_after) == 0

    def test_reset_returns_true_on_success(self):
        """Reset should return True."""
        ensure_memory_dir()
        result = reset_ai_memory()
        assert result is True


class TestFeedbackCategories:
    """Test valid feedback category values."""

    def test_valid_correction_types(self):
        """Valid correction types can be saved."""
        valid_corrections = [
            "benar",
            "salah",
            "relevan",
            "tidak_relevan",
            "should_include",
            "should_exclude",
        ]

        ensure_memory_dir()

        for correction in valid_corrections:
            save_feedback(
                query="test",
                product={"title": "Test", "url": "https://t.co/p1"},
                ai_decision={},
                correction=correction,
                categories=[],
            )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        corrections_saved = {f["correction"] for f in feedback_lines}
        for correction in valid_corrections:
            assert correction in corrections_saved

    def test_valid_category_tags(self):
        """Valid category tags can be saved."""
        valid_categories = [
            "gaming_laptop",
            "office_laptop",
            "mouse",
            "keyboard",
            "charger",
            "not_laptop",
            "wrong_price",
            "duplicate",
            "should_include",
            "should_exclude",
        ]

        ensure_memory_dir()

        for category in valid_categories:
            save_feedback(
                query="test",
                product={"title": "Test", "url": "https://t.co/p1"},
                ai_decision={},
                correction="categorize",
                categories=[category],
            )

        feedback_lines = read_jsonl(FEEDBACK_FILE)
        last = feedback_lines[-1]
        assert len(last["categories"]) >= 1


class TestScopedSQLiteLearning:
    """SQLite learning keeps negative feedback scoped to the query context."""

    def test_spec_mismatch_creates_constraint_scoped_penalty(self):
        result = feedback_store.save_feedback_event(
            query="RTX 5060",
            query_intent="main_product",
            product={
                "title": "Laptop Gaming RTX 4060",
                "url": "https://tokopedia.com/rtx4060",
                "price_value": 10000000,
                "store": "Test Store",
            },
            feedback_type="negative",
            reasons=["Spesifikasi tidak sesuai query"],
            note="Saya cari RTX 5060, ini RTX 4060",
            learning_scope_hint="query_constraint",
            decision_source="rule_accept",
            confidence=0.72,
            rule_score=0.30,
            semantic_score=0.70,
            combined_score=0.62,
            learned_adjustment=0.0,
        )

        assert result["ok"] is True
        assert result["learning_updated"] is True

        q5060 = feedback_store.extract_query_constraints("RTX 5060")
        patterns_5060 = feedback_store.load_learned_patterns("RTX 5060", "main_product", q5060)
        penalty = next(p for p in patterns_5060 if p["pattern"] == "rtx 4060")
        assert penalty["scope"] == "query_constraint"
        assert penalty["constraint_key"] == "gpu_model:rtx 5060"
        assert penalty["weight"] == -0.45

        product_4060 = {"title": "Laptop Gaming RTX 4060"}
        adjustment, matches = feedback_store.compute_learned_adjustment(
            "RTX 5060",
            "main_product",
            q5060,
            product_4060,
            patterns_5060,
        )
        assert adjustment < 0
        assert matches[0]["scope"] == "query_constraint"

        q4060 = feedback_store.extract_query_constraints("RTX 4060")
        patterns_4060 = feedback_store.load_learned_patterns("RTX 4060", "main_product", q4060)
        adjustment_4060, matches_4060 = feedback_store.compute_learned_adjustment(
            "RTX 4060",
            "main_product",
            q4060,
            {"title": "Laptop Gaming RTX 4060"},
            patterns_4060,
        )
        assert adjustment_4060 == 0
        assert matches_4060 == []

    def test_constraint_reset_clears_only_constraint_patterns(self):
        feedback_store.save_feedback_event(
            query="RTX 5060",
            query_intent="main_product",
            product={"title": "Laptop RTX 4060", "url": "https://tokopedia.com/p1", "price_value": 1},
            feedback_type="negative",
            reasons=["Spesifikasi tidak sesuai query"],
            learning_scope_hint="query_constraint",
        )
        feedback_store.save_feedback_event(
            query="laptop gaming",
            query_intent="main_product",
            product={"title": "MSI Thin RTX3050 Laptop Gaming", "url": "https://tokopedia.com/p2", "price_value": 1},
            feedback_type="positive",
            reasons=[],
            learning_scope_hint="exact_query",
        )

        reset = feedback_store.reset_learning(scope="constraint", constraint_key="gpu_model:rtx 5060")
        assert reset["deleted_learned_patterns"] >= 1
        remaining_5060_patterns = feedback_store.load_learned_patterns(
            "RTX 5060",
            "main_product",
            feedback_store.extract_query_constraints("RTX 5060"),
        )
        assert all(pattern.get("constraint_key") != "gpu_model:rtx 5060" for pattern in remaining_5060_patterns)
        assert feedback_store.load_learned_patterns(
            "laptop gaming",
            "main_product",
            feedback_store.extract_query_constraints("laptop gaming"),
        )

    def test_next_filter_loads_feedback_and_exposes_learned_adjustment(self, monkeypatch):
        monkeypatch.setattr(
            ai_filter,
            "get_orchestrator_status",
            lambda: {
                "classifier": None,
                "installed": [],
                "supported": [],
                "missing": [],
                "capabilities": {"semantic": False, "json_repair": False},
            },
        )
        monkeypatch.setattr(ai_filter, "get_best_classifier_model", lambda models=None: None)

        feedback_store.save_feedback_event(
            query="RTX 5060",
            query_intent="main_product",
            product={"title": "Laptop Gaming RTX 4060", "url": "https://tokopedia.com/rtx4060", "price_value": 1},
            feedback_type="negative",
            reasons=["Spesifikasi tidak sesuai query"],
            learning_scope_hint="query_constraint",
        )

        result = asyncio.run(ai_filter.filter_products(
            "RTX 5060",
            [
                {"title": "Laptop Gaming RTX 4060", "url": "https://tokopedia.com/rtx4060", "price_value": 1, "_requested_target": 2},
                {"title": "Laptop Gaming RTX 5060", "url": "https://tokopedia.com/rtx5060", "price_value": 1, "_requested_target": 2},
            ],
            use_ai=False,
        ))
        learned_product = next(p for p in result.products if "RTX 4060" in p["title"])
        assert learned_product["learned_adjustment"] < 0
        assert learned_product["learned_matches"]
        assert learned_product["constraint_mismatch_reasons"] == [
            "GPU mismatch: query wants rtx 5060, product has rtx 4060"
        ]
        assert result.meta["learned_patterns_loaded"] >= 1
        assert result.meta["learning_adjusted_products"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
