"""
test_budget_filter.py - Budget filter behavior.
"""
import pytest
from src.scraper.budget_filter import filter_by_budget


def make_product(title, price_raw, price_value=None):
    return {"title": title, "price_raw": price_raw, "price_value": price_value, "url": f"https://tokopedia.com/{title.lower().replace(' ', '-')}", "source_engine": "test"}


class TestEmptyBudget:
    def test_empty_string_keeps_all(self):
        products = [
            make_product("Laptop A", "Rp5.000.000", 5_000_000),
            make_product("Laptop B", "Rp25.000.000", 25_000_000),
        ]
        result = filter_by_budget(products, "", 20)
        assert result.budget_value is None
        assert len(result.kept) == 2

    def test_none_keeps_all(self):
        products = [make_product("X", "Rp1.000.000", 1_000_000)]
        result = filter_by_budget(products, None, 20)
        assert result.budget_value is None
        assert len(result.kept) == 1

    def test_zero_budget_keeps_all(self):
        products = [make_product("Y", "Rp2.000.000", 2_000_000)]
        result = filter_by_budget(products, "0", 20)
        assert result.budget_value is None
        assert len(result.kept) == 1


class TestBudget10MillionTolerance10:
    """Budget 10.000.000 tolerance 10% = range 9.000.000 - 11.000.000"""

    def _run(self, products):
        return filter_by_budget(products, "10.000.000", 10)

    def test_within_range_kept(self):
        products = [make_product("In Range", "Rp10.000.000", 10_000_000)]
        result = self._run(products)
        assert len(result.kept) == 1

    def test_min_boundary_kept(self):
        products = [make_product("At Min", "Rp9.000.000", 9_000_000)]
        result = self._run(products)
        assert len(result.kept) == 1

    def test_max_boundary_kept(self):
        products = [make_product("At Max", "Rp11.000.000", 11_000_000)]
        result = self._run(products)
        assert len(result.kept) == 1

    def test_below_range_rejected(self):
        products = [make_product("Too Cheap", "Rp1.000.000", 1_000_000)]
        result = self._run(products)
        assert len(result.kept) == 0
        assert result.reasons.get("below_budget_range", 0) == 1

    def test_above_range_rejected(self):
        products = [make_product("Too Expensive", "Rp20.000.000", 20_000_000)]
        result = self._run(products)
        assert len(result.kept) == 0
        assert result.reasons.get("above_budget_range", 0) == 1

    def test_invalid_price_rejected_by_strict_budget_default(self):
        products = [make_product("No Price", "", None)]
        result = self._run(products)
        assert len(result.kept) == 0
        assert result.reasons.get("invalid_price", 0) == 1

    def test_range_values(self):
        result = self._run([])
        assert result.min_price == 9_000_000
        assert result.max_price == 11_000_000
