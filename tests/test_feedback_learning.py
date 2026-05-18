"""
test_feedback_learning.py - Test user feedback and AI learning.

Coverage:
- Feedback multi-category saved
- Reset clears AI memory files
- Learning data format correct
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.ai.learning import save_feedback
from src.ai.memory_store import FEEDBACK_FILE, EXAMPLES_FILE, CATEGORY_RULES_FILE, ensure_memory_dir, read_jsonl
from src.ai.reset import reset_ai_memory


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
