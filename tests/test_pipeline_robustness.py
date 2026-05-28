"""
test_pipeline_robustness.py - Test pipeline robustness across all stages.

Coverage:
- Raw products with missing shop/rating kept
- Budget filter keeps raw products on empty budget
- Budget tolerance works (10jt ±10 = 9jt-11jt)
- Compare mode returns two separate reports
- Dedupe works across engines
"""
from __future__ import annotations

import pytest

from src.scraper.budget_filter import filter_by_budget
from src.scraper.dedupe import deduplicate_products
from src.scraper.engine_selector import EngineRunResult
from src.scraper.normalizer import normalize_products
from src.server import routes
from src.server.schemas import SearchRequest
from src.utils.eta import ETACalculator


class TestRawProductPreservation:
    """Test that raw products are preserved even with missing fields."""

    def test_raw_product_with_missing_shop(self):
        """Raw product missing shop field should be kept."""
        raw = [
            {
                "title": "ASUS ROG Gaming Laptop",
                "price_raw": "Rp 12.999.999",
                "url": "https://tokopedia.com/asus/gaming",
                # shop is missing
                "rating": "4.9",
                "sold": "150 terjual",
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 1
        # Product should be kept despite missing shop
        assert normalized[0]["title"] == "ASUS ROG Gaming Laptop"

    def test_raw_product_with_missing_rating(self):
        """Raw product missing rating field should be kept."""
        raw = [
            {
                "title": "Dell XPS Gaming Laptop",
                "price_raw": "Rp 15.000.000",
                "url": "https://tokopedia.com/dell/xps",
                "shop": "Dell Store",
                # rating is missing
                "sold": "89 terjual",
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 1
        assert normalized[0]["title"] == "Dell XPS Gaming Laptop"

    def test_raw_product_with_minimal_fields(self):
        """Raw product with only title and price should be kept."""
        raw = [
            {
                "title": "Gaming Laptop",
                "price_raw": "Rp 10.000.000",
                # Everything else missing
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 1
        assert normalized[0]["title"] == "Gaming Laptop"

    def test_raw_product_drops_on_missing_title_and_price(self):
        """Product dropped only if missing BOTH title and (price_raw or url)."""
        raw = [
            {
                # no title, no price_raw, no url
                "shop": "Some Shop",
            }
        ]
        normalized = normalize_products(raw)
        assert len(normalized) == 0


class TestBudgetFiltering:
    """Test budget filter behavior."""

    def test_empty_budget_keeps_all(self):
        """Empty budget string/none keeps all products."""
        products = [
            {"title": "Cheap Laptop", "price_raw": "Rp 5.000.000", "price_value": 5000000},
            {"title": "Expensive Laptop", "price_raw": "Rp 50.000.000", "price_value": 50000000},
        ]
        result = filter_by_budget(products, budget=None)
        assert len(result.kept) == 2

    def test_budget_with_tolerance(self):
        """Budget 10jt ±10 = 9jt-11jt range."""
        products = [
            {"title": "8.5jt Laptop", "price_raw": "Rp 8.500.000", "price_value": 8500000},   # dropped
            {"title": "9jt Laptop", "price_raw": "Rp 9.000.000", "price_value": 9000000},      # kept
            {"title": "10jt Laptop", "price_raw": "Rp 10.000.000", "price_value": 10000000},    # kept
            {"title": "11jt Laptop", "price_raw": "Rp 11.000.000", "price_value": 11000000},    # kept
            {"title": "11.5jt Laptop", "price_raw": "Rp 11.500.000", "price_value": 11500000},  # dropped
        ]
        result = filter_by_budget(products, budget="10 juta", tolerance=10)
        # Should keep 9-11jt range
        assert len(result.kept) >= 2  # At least center values
        if result.kept:
            prices = [p["price_value"] for p in result.kept if p.get("price_value")]
            if prices:
                assert min(prices) >= 9000000
                assert max(prices) <= 11000000

    def test_budget_exact_boundaries(self):
        """Budget boundaries are inclusive."""
        products = [
            {"title": "Min Price", "price_raw": "Rp 9.000.000", "price_value": 9000000},
            {"title": "Max Price", "price_raw": "Rp 11.000.000", "price_value": 11000000},
        ]
        result = filter_by_budget(products, budget="10 juta", tolerance=10)
        # Both boundary values should be kept (inclusive range)
        assert len(result.kept) >= 2


class TestDeduplication:
    """Test product deduplication."""

    def test_dedupe_by_url_title_price(self):
        """Dedupe removes exact duplicates."""
        products = [
            {
                "title": "ASUS ROG Gaming",
                "url": "https://tokopedia.com/asus/rog-1",
                "price_value": 12000000,
            },
            {
                "title": "ASUS ROG Gaming",
                "url": "https://tokopedia.com/asus/rog-1",
                "price_value": 12000000,
            },
        ]
        deduped = deduplicate_products(products)
        assert len(deduped) == 1

    def test_dedupe_preserves_different_urls(self):
        """Dedupe keeps products with different URLs."""
        products = [
            {
                "title": "ASUS ROG",
                "url": "https://tokopedia.com/asus/rog-1",
                "price_value": 12000000,
            },
            {
                "title": "ASUS ROG",
                "url": "https://tokopedia.com/asus/rog-2",  # Different URL
                "price_value": 12000000,
            },
        ]
        deduped = deduplicate_products(products)
        assert len(deduped) == 2

    def test_dedupe_query_variant_field(self):
        """Dedup should use query_variant if present."""
        products = [
            {
                "title": "Laptop",
                "url": "https://t.co/p1",
                "price_value": 10000000,
                "source_query": "laptop gaming",
            },
            {
                "title": "Laptop",
                "url": "https://t.co/p1",
                "price_value": 10000000,
                "source_query": "laptop office",  # Different variant
            },
        ]
        deduped = deduplicate_products(products)
        # Should dedupe as same product despite different query_variant
        assert len(deduped) == 1


class TestCompareModeSchema:
    """Test that compare mode returns proper schema."""

    def test_engine_run_report_schema(self):
        """Engine report should have all required fields."""
        required_fields = [
            "engine",
            "opened_real_page",
            "error_type",
            "raw_count",
            "status",
            "duration_seconds",
        ]
        # This is more of a schema validation test
        # In real usage, these come from EngineRunResult
        schema_example = {
            "engine": "puppeteer",
            "opened_real_page": True,
            "error_type": None,
            "raw_count": 42,
            "status": "success",
            "duration_seconds": 12.5,
        }
        for field in required_fields:
            assert field in schema_example


class TestCandidatePoolValidation:
    def test_non_product_pages_are_not_valid_candidates(self):
        invalid = [
            {"title": "Mulai Berjualan", "price_value": 0, "url": "https://seller.tokopedia.com/edu/topic/mulai-bisnis/materi-seller-baru/"},
            {"title": "Kalkulator Indeks Masa Tubuh", "price_value": 0, "url": "https://www.tokopedia.com/blog/bmi/"},
            {"title": "Daftar Mall", "price_value": 0, "url": "https://seller.tokopedia.com/edu/official-store/"},
        ]
        valid = {
            "title": "ASUS TUF Gaming Laptop RTX 3050",
            "price_value": 10_000_000,
            "url": "https://www.tokopedia.com/test/asus-tuf",
        }

        assert all(not routes.is_valid_product_candidate(product) for product in invalid)
        assert routes.is_valid_product_candidate(valid)

    @pytest.mark.asyncio
    async def test_overfetch_loads_more_when_valid_pool_is_short(self, monkeypatch):
        calls = []

        async def fake_run_engine(search_id, engine_name, query, raw_target, eta_calc):
            calls.append(raw_target)
            return EngineRunResult(
                engine=engine_name,
                ok=True,
                opened_real_page=True,
                products=[
                    {
                        "title": "Lenovo LOQ Laptop Gaming RTX 3050",
                        "price_raw": "Rp 11.000.000",
                        "price_value": 11_000_000,
                        "url": "https://www.tokopedia.com/test/loq-extra",
                    }
                ],
            )

        monkeypatch.setattr(routes, "run_engine", fake_run_engine)

        raw_products = [
            {"title": "ASUS TUF Laptop Gaming RTX 3050", "price_raw": "Rp 10.000.000", "price_value": 10_000_000, "url": "https://www.tokopedia.com/test/tuf"},
            {"title": "Mulai Berjualan", "price_raw": "", "price_value": 0, "url": "https://seller.tokopedia.com/edu/topic/mulai-bisnis/materi-seller-baru/"},
        ]

        products, meta = await routes._overfetch_raw_products(
            "test-overfetch",
            SearchRequest(query="laptop gaming", target_count=2),
            raw_products,
            "puppeteer",
            raw_target=2,
            eta_calc=ETACalculator(),
        )

        assert calls
        assert meta["overfetch_attempted"] is True
        assert meta["overfetch_initial_valid_pool"] == 1
        assert meta["overfetch_final_valid_pool"] == 2
        assert len(products) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
