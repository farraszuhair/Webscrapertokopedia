"""
test_normalizer.py - Normalizer keeps raw products even with missing optional fields.
"""
import pytest
from src.scraper.normalizer import normalize_product, normalize_products


class TestNormalizerKeepsWeakProducts:
    def test_keeps_product_missing_shop(self):
        raw = {"title": "ASUS TUF Gaming F15", "price_raw": "Rp12.000.000", "url": "https://tokopedia.com/x/y"}
        result = normalize_product(raw)
        assert result is not None
        assert result["title"] == "ASUS TUF Gaming F15"
        assert result["shop"] == ""  # missing is OK

    def test_keeps_product_missing_rating(self):
        raw = {"title": "Legion 5 Pro", "price_raw": "Rp15.000.000", "url": "https://tokopedia.com/a/b"}
        result = normalize_product(raw)
        assert result is not None
        assert result["rating"] == ""

    def test_keeps_product_missing_image(self):
        raw = {"title": "ROG Strix", "price_raw": "Rp20.000.000", "url": "https://tokopedia.com/c/d"}
        result = normalize_product(raw)
        assert result is not None
        assert result["image"] == ""

    def test_drops_product_missing_title(self):
        raw = {"price_raw": "Rp5.000.000", "url": "https://tokopedia.com/x/y"}
        result = normalize_product(raw)
        assert result is None

    def test_drops_product_missing_url_and_price(self):
        raw = {"title": "Some product"}
        result = normalize_product(raw)
        assert result is None

    def test_keeps_product_with_price_but_no_url(self):
        """Product with price but no URL is kept - URL is not strictly required."""
        raw = {"title": "Laptop Gaming", "price_raw": "Rp8.000.000"}
        result = normalize_product(raw)
        assert result is not None

    def test_batch_normalize_keeps_partial(self):
        products = [
            {"title": "OK Product", "price_raw": "Rp5.000.000", "url": "https://tokopedia.com/ok"},
            {"price_raw": "no title should drop"},
        ]
        result = normalize_products(products)
        assert len(result) == 1
        assert result[0]["title"] == "OK Product"
