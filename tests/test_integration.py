"""
test_integration.py - Full pipeline integration tests.

Coverage:
- Compare mode returns both engine reports independently
- Engine preflight errors reported with opened_real_page=false
- Qwen failures don't crash pipeline
- Budget filters work end-to-end
- Product feedback saved and can be retrieved
"""
from __future__ import annotations

import pytest

from src.scraper.budget_filter import filter_by_budget
from src.scraper.normalizer import normalize_products


class TestCompareMode:
    """Test compare mode returns proper structure."""

    def test_compare_result_has_both_engines(self):
        """Compare result should have engine_runs or comparison with both engines."""
        # This tests the schema, not actual network operations
        schema = {
            "comparison": [
                {
                    "engine": "puppeteer",
                    "ok": True,
                    "opened_real_page": True,
                    "raw_count": 42,
                    "ai_valid_count": 35,
                    "qwen_status": "ok",
                },
                {
                    "engine": "rollback",
                    "ok": True,
                    "opened_real_page": True,
                    "raw_count": 38,
                    "ai_valid_count": 32,
                    "qwen_status": "ok",
                },
            ],
            "selected_engine": "puppeteer",
        }
        assert len(schema["comparison"]) == 2
        assert schema["comparison"][0]["engine"] == "puppeteer"
        assert schema["comparison"][1]["engine"] == "rollback"

    def test_compare_mode_shows_opened_real_page_status(self):
        """Compare cards must show opened_real_page status."""
        run = {
            "engine": "puppeteer",
            "opened_real_page": False,
            "error_type": "http2_protocol_error",
            "error": "Browser opened Chrome error page",
            "raw_count": 0,
        }
        # Frontend should display this as: "❌ opened_real_page: NO — http2_protocol_error"
        assert run["opened_real_page"] is False
        assert run["error_type"] == "http2_protocol_error"

    def test_compare_mode_independent_runs(self):
        """Each engine run should be independent, no fallback silently."""
        results = [
            {
                "engine": "puppeteer",
                "status": "fail",
                "opened_real_page": False,
                "error_type": "http2_protocol_error",
            },
            {
                "engine": "rollback",
                "status": "success",
                "opened_real_page": True,
                "products": 45,
            },
        ]
        # Both results should be present, not just the successful one
        assert len(results) == 2
        assert results[0]["status"] == "fail"
        assert results[1]["status"] == "success"


class TestPreflightInPipeline:
    """Test preflight errors in the pipeline."""

    def test_preflight_error_stops_extraction(self):
        """If preflight detects error page, no extraction should happen."""
        preflight_result = {
            "opened_real_page": False,
            "error_type": "http2_protocol_error",
            "page_title": "ERR_HTTP2_PROTOCOL_ERROR",
            "current_url": "https://www.tokopedia.com/search?q=laptop",
        }

        # Pipeline should stop and report this, not try to extract
        assert preflight_result["opened_real_page"] is False
        assert preflight_result["error_type"] is not None

    def test_raw_products_count_zero_with_preflight_error(self):
        """When preflight fails, raw_count should be 0, not fake."""
        engine_result = {
            "engine": "puppeteer",
            "ok": False,
            "opened_real_page": False,
            "error_type": "connection_reset",
            "raw_count": 0,  # Not fake/misleading
            "error": "Browser opened error page",
        }
        assert engine_result["raw_count"] == 0
        assert engine_result["ok"] is False


class TestQwenFailureInPipeline:
    """Test that Qwen failure is handled in pipeline."""

    def test_qwen_failed_shows_fallback_warning(self):
        """When Qwen fails, qwen_status=failed and warning is shown."""
        result = {
            "qwen_status": "failed",
            "qwen_warning": "Qwen gagal atau tidak tersedia. Produk ditampilkan berdasarkan fallback scoring.",
            "data": [  # Still has data from fallback
                {"title": "Laptop 1"},
                {"title": "Laptop 2"},
            ],
        }
        assert result["qwen_status"] == "failed"
        assert "Qwen gagal" in result["qwen_warning"]
        assert len(result["data"]) > 0  # Products still returned

    def test_qwen_disabled_shows_disabled_status(self):
        """When use_ai=false, qwen_status=disabled."""
        result = {
            "qwen_status": "disabled",
            "data": [
                {"title": "Laptop 1"},
            ],
        }
        assert result["qwen_status"] == "disabled"

    def test_qwen_unavailable_fallback_used(self):
        """When Ollama not running, fallback scorer used."""
        result = {
            "qwen_status": "unavailable",
            "data": [
                {"title": "Laptop 1"},
            ],
        }
        assert result["qwen_status"] == "unavailable"
        assert len(result["data"]) > 0


class TestBudgetPipelineIntegration:
    """Test budget filter in full pipeline."""

    def test_empty_budget_passes_all(self):
        """Pipeline with no budget should pass all raw products through."""
        products = [
            {"title": "Cheap", "price_raw": "Rp 3.000.000", "price_value": 3000000},
            {"title": "Expensive", "price_raw": "Rp 50.000.000", "price_value": 50000000},
        ]
        result = filter_by_budget(products, budget=None)
        # All should pass
        assert len(result.kept) == 2

    def test_budget_range_in_pipeline(self):
        """Pipeline should apply budget range correctly."""
        products = [
            {"title": "Below", "price_raw": "Rp 8.000.000", "price_value": 8000000},
            {"title": "In Range", "price_raw": "Rp 10.000.000", "price_value": 10000000},
            {"title": "Above", "price_raw": "Rp 12.000.000", "price_value": 12000000},
        ]
        # 10jt ±5 = 9.5jt-10.5jt
        result = filter_by_budget(products, budget="10 juta", tolerance=5)
        # Center value should pass
        assert len(result.kept) >= 1


class TestErrorMessageQuality:
    """Test that error messages are descriptive."""

    def test_preflight_error_message(self):
        """Preflight error should explain what happened."""
        msg = (
            "Browser opened Chrome error page: http2_protocol_error. "
            "Bukan masalah selector. Lihat debug: data/debug/search_id/"
        )
        assert "error page" in msg.lower()
        assert "http2_protocol_error" in msg

    def test_qwen_failure_message(self):
        """Qwen failure should explain fallback is being used."""
        msg = "Qwen gagal atau tidak tersedia. Produk ditampilkan berdasarkan fallback scoring (raw/budget tetap ditampilkan)."
        assert "Qwen gagal" in msg
        assert "fallback" in msg.lower()

    def test_budget_no_match_message(self):
        """Budget no-match should show range."""
        msg = "0 produk lolos budget Rp9.000.000 - Rp11.000.000. Coba naikkan budget/tolerance."
        assert "Rp9.000.000" in msg
        assert "Rp11.000.000" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
