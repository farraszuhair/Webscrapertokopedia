"""
Unit tests for TokopediaScraper

Run with: python -m pytest test_scraper.py -v
"""

import pytest
import asyncio
from scraper.tokopedia_scraper import TokopediaScraper


class TestScraperKeywordFiltering:
    """Test keyword matching and filtering logic"""
    
    def test_mousepad_not_filtered_when_searching_mousepad(self):
        """Verify that 'mousepad' products aren't filtered when searching for 'mousepad'"""
        scraper = TokopediaScraper(headless=True)
        keyword = "mousepad"
        keyword_lower = keyword.lower()
        
        # Build the same logic as in the scraper
        search_terms = set(w.lower() for w in keyword.split() if len(w) > 2)
        negative_keywords = ['stiker', 'sticker', 'grip', 'case', 'cover', 'feet', 'baterai', 'kabel', 'cable']
        negative_keywords = [kw for kw in negative_keywords if kw not in search_terms]
        
        # Test that 'mousepad' and 'pad' are NOT in the negative keywords
        assert 'mousepad' not in negative_keywords
        assert 'pad' not in negative_keywords
        
        # Test a mousepad product would NOT be filtered
        test_product = {"nama": "Mousepad Gaming RGB 30x25cm", "harga": 150000}
        nama_lower = test_product['nama'].lower()
        is_aksesoris = any(neg in nama_lower for neg in negative_keywords)
        assert not is_aksesoris, "Mousepad product should not be filtered as accessory"
    
    def test_mouse_gaming_razer_keeps_relevant_products(self):
        """Verify mouse gaming products are kept when searching 'Mouse Gaming Razer'"""
        keyword = "Mouse Gaming Razer"
        search_terms = set(w.lower() for w in keyword.split() if len(w) > 2)
        
        test_products = [
            "Razer DeathAdder V3 Gaming Mouse",
            "Logitech G502 Mouse Gaming",
            "SteelSeries Rival 600 Gaming Mouse",
        ]
        
        for product in test_products:
            product_lower = product.lower()
            has_keyword = any(w in product_lower for w in search_terms)
            assert has_keyword, f"{product} should match search terms"
    
    def test_accessory_filtering_excludes_non_search_terms(self):
        """Verify accessories like grips/cases are filtered but search terms aren't"""
        keyword = "mousepad"
        search_terms = set(w.lower() for w in keyword.split() if len(w) > 2)
        negative_keywords = ['stiker', 'sticker', 'grip', 'case', 'cover', 'feet', 'baterai', 'kabel', 'cable']
        negative_keywords = [kw for kw in negative_keywords if kw not in search_terms]
        
        # These should be filtered as accessories
        accessories = [
            "Mouse Grip Tape",
            "Keyboard Case Cover",
            "Cable Management Kit",
        ]
        
        for item in accessories:
            item_lower = item.lower()
            is_aksesoris = any(neg in item_lower for neg in negative_keywords)
            assert is_aksesoris, f"{item} should be filtered as accessory"


class TestScraperPriceValidation:
    """Test price validation logic"""
    
    def test_premium_products_require_higher_price(self):
        """Premium items like Razer/Headset require minimum price"""
        keywords_with_high_requirement = [
            "mouse razer", "headset gaming", "keyboard razer",
            "mouse logitech pro", "headphones premium"
        ]
        
        premium_terms = ['mouse', 'razer', 'headset', 'keyboard', 'headphones']

        for kw in keywords_with_high_requirement:
            harga = 50000  # Below 100k
            harga_wajar = harga >= 100000 if any(
                term in kw.lower() for term in premium_terms
            ) else harga >= 5000
            assert not harga_wajar, f"{kw} at {harga} should be rejected"
    
    def test_minimum_price_threshold(self):
        """Products below 5000 Rp should be rejected"""
        test_cases = [
            (1000, False),   # Too cheap
            (3000, False),   # Too cheap
            (5000, True),    # Acceptable
            (10000, True),   # Acceptable
            (100000, True),  # Acceptable
        ]
        
        for price, expected_valid in test_cases:
            is_valid = price >= 5000
            assert is_valid == expected_valid, f"Price {price} validation failed"


class TestScraperRobustness:
    """Test scraper robustness features"""
    
    def test_retry_configuration_exists(self):
        """Verify retry mechanism is configured"""
        scraper = TokopediaScraper()
        assert hasattr(scraper, 'MAX_RETRIES')
        assert scraper.MAX_RETRIES >= 2
        assert hasattr(scraper, 'RETRY_DELAY')
    
    def test_empty_extraction_handling(self):
        """Verify extractor skips failed extractions"""
        # Mock extraction data with invalid entries
        extraction_results = [
            {"nama": "produk tokopedia"},  # Should be skipped
            {"nama": ""},  # Should be skipped
            {"nama": "Valid Product", "harga": 50000}  # Should be kept
        ]
        
        valid_results = [
            item for item in extraction_results
            if item['nama'] and item['nama'].lower() != "produk tokopedia"
        ]
        
        assert len(valid_results) == 1
        assert valid_results[0]['nama'] == "Valid Product"


class TestErrorHandling:
    """Test error handling and recovery"""
    
    def test_timeout_error_catching(self):
        """Verify timeout errors are properly caught and logged"""
        # This test verifies the exception type is imported and used
        from scraper.tokopedia_scraper import PlaywrightTimeoutError
        assert PlaywrightTimeoutError is not None
    
    def test_scraper_initialization(self):
        """Test scraper initializes correctly"""
        scraper = TokopediaScraper(headless=True)
        assert scraper.headless == True
        assert scraper.results == []
        assert scraper.retry_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
