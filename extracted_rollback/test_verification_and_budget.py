"""
Comprehensive tests for Product Verification and Budget Filtering Systems

Tests for:
- VerifiedProductTracker
- BudgetFilter
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from ai_analyzer.verified_products import VerifiedProductTracker
from ai_analyzer.budget_filter import BudgetFilter


class TestVerifiedProductTracker:
    """Test suite for VerifiedProductTracker"""
    
    @pytest.fixture
    def tracker(self):
        """Create a tracker with temporary storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VerifiedProductTracker(storage_dir=tmpdir)
            yield tracker
    
    def test_initialize_tracker(self, tracker):
        """Test tracker initialization"""
        assert tracker.storage_dir.exists()
        assert isinstance(tracker.verified_file, Path)
        assert isinstance(tracker.verified_patterns_file, Path)
    
    def test_record_verification(self, tracker):
        """Test recording a verified product"""
        record = tracker.record_verification(
            product_name="Razer Mouse",
            product_url="https://tokopedia.com/razer-mouse",
            ai_analysis={"trust_score": 90, "skor_value": 85},
            user_note="Harga sesuai, original"
        )
        
        assert record is not None
        assert record["product_name"] == "Razer Mouse"
        assert record["verified_count"] == 1
        assert "timestamp" in record
    
    def test_duplicate_verification_increments_count(self, tracker):
        """Test that verifying same product increments count"""
        # First verification
        tracker.record_verification(
            product_name="Razer Mouse V3",
            product_url="https://tokopedia.com/razer",
            ai_analysis={"trust_score": 90}
        )
        
        # Second verification
        record = tracker.record_verification(
            product_name="Razer Mouse V3",
            product_url="https://tokopedia.com/razer",
            ai_analysis={"trust_score": 90}
        )
        
        assert record["verified_count"] == 2
    
    def test_get_verified_product(self, tracker):
        """Test retrieving verified product"""
        tracker.record_verification(
            product_name="Logitech Mouse",
            product_url="https://...",
            ai_analysis={"trust_score": 85}
        )
        
        verified = tracker.get_verified_product("Logitech Mouse")
        assert verified is not None
        assert verified["product_name"] == "Logitech Mouse"
    
    def test_get_verified_count(self, tracker):
        """Test getting verification count"""
        tracker.record_verification(
            product_name="Gaming Keyboard",
            product_url="https://...",
            ai_analysis={"trust_score": 80}
        )
        
        tracker.record_verification(
            product_name="Gaming Keyboard",
            product_url="https://...",
            ai_analysis={"trust_score": 80}
        )
        
        count = tracker.get_verified_count("Gaming Keyboard")
        assert count == 2
    
    def test_get_confidence_boost(self, tracker):
        """Test confidence boost calculation"""
        # Single verification
        tracker.record_verification(
            product_name="Product A",
            product_url="https://...",
            ai_analysis={}
        )
        
        boost = tracker.get_confidence_boost("Product A")
        assert boost == 5.0  # 1 verification * 5%
    
    def test_confidence_boost_capped_at_50(self, tracker):
        """Test that confidence boost caps at 50%"""
        product_name = "Very Popular Product"
        
        # Add 20 verifications
        for _ in range(20):
            tracker.record_verification(
                product_name=product_name,
                product_url="https://...",
                ai_analysis={}
            )
        
        boost = tracker.get_confidence_boost(product_name)
        assert boost == 50.0  # Capped at 50%
    
    def test_get_verification_status(self, tracker):
        """Test getting verification status"""
        tracker.record_verification(
            product_name="Test Product",
            product_url="https://...",
            ai_analysis={"trust_score": 88, "skor_value": 82},
            user_note="Great product"
        )
        
        status = tracker.get_verification_status("Test Product")
        
        assert status["is_verified"] is True
        assert status["verification_count"] >= 1
        assert status["confidence_boost"] >= 0
        assert status["user_note"] == "Great product"
    
    def test_get_patterns(self, tracker):
        """Test getting verification patterns"""
        tracker.record_verification(
            product_name="Product X",
            product_url="https://...",
            ai_analysis={"rekomendasi": "DIREKOMENDASIKAN"}
        )
        
        tracker.record_verification(
            product_name="Product Y",
            product_url="https://...",
            ai_analysis={"rekomendasi": "TIDAK DIREKOMENDASIKAN"}
        )
        
        patterns = tracker.get_patterns()
        
        assert patterns["total_verified"] >= 2
        assert "verified_products" in patterns
        assert "common_recommendations" in patterns
    
    def test_export_verified_report(self, tracker):
        """Test exporting verification report"""
        tracker.record_verification(
            product_name="Report Test",
            product_url="https://...",
            ai_analysis={"trust_score": 75}
        )
        
        report = tracker.export_verified_report()
        
        assert report["total_verified"] >= 1
        assert "verified_products" in report
        assert "patterns" in report
    
    def test_export_to_file(self, tracker):
        """Test exporting report to file"""
        tracker.record_verification(
            product_name="File Test",
            product_url="https://...",
            ai_analysis={}
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_file = f.name
        
        report = tracker.export_verified_report(output_file=output_file)
        
        assert Path(output_file).exists()
        
        with open(output_file, 'r') as f:
            saved_report = json.load(f)
        
        assert saved_report["total_verified"] >= 1
    
    def test_string_similarity(self, tracker):
        """Test string similarity calculation"""
        # Exact match
        similarity = tracker._string_similarity("Razer Mouse", "Razer Mouse")
        assert similarity == 1.0
        
        # Partial match
        similarity = tracker._string_similarity("Razer DeathAdder V3", "Razer DeathAdder")
        assert 0.5 < similarity < 1.0
        
        # No match
        similarity = tracker._string_similarity("Razer", "Logitech")
        assert similarity == 0.0
    
    def test_clear_old_verifications(self, tracker):
        """Test clearing old verifications"""
        tracker.record_verification(
            product_name="Old Product",
            product_url="https://...",
            ai_analysis={}
        )
        
        # This should keep the recent product
        tracker.clear_old_verifications(keep_days=365)
        
        verified = tracker.get_verified_product("Old Product")
        assert verified is not None  # Recent, should be kept
    
    def test_empty_tracker_queries(self, tracker):
        """Test querying empty tracker"""
        verified = tracker.get_verified_product("Nonexistent Product")
        assert verified is None
        
        count = tracker.get_verified_count("Nonexistent Product")
        assert count == 0
        
        boost = tracker.get_confidence_boost("Nonexistent Product")
        assert boost == 0.0
        
        patterns = tracker.get_patterns()
        assert patterns["total_verified"] == 0


class TestBudgetFilter:
    """Test suite for BudgetFilter"""
    
    @pytest.fixture
    def sample_products(self):
        """Create sample products for testing"""
        return [
            {"nama_produk": "Mouse Cheap", "harga": 100000, "trust_score": 60},
            {"nama_produk": "Mouse Mid", "harga": 500000, "trust_score": 85},
            {"nama_produk": "Mouse Expensive", "harga": 2000000, "trust_score": 95},
            {"nama_produk": "Mouse Premium", "harga": 3000000, "trust_score": 90},
        ]
    
    def test_filter_no_budget(self, sample_products):
        """Test filtering without budget"""
        filtered, metadata = BudgetFilter.filter_by_budget(sample_products, budget=None)
        
        assert metadata["budget_applied"] is False
        assert len(filtered) == len(sample_products)
    
    def test_filter_with_budget(self, sample_products):
        """Test filtering with budget"""
        filtered, metadata = BudgetFilter.filter_by_budget(
            sample_products,
            budget=1000000
        )
        
        assert metadata["budget_applied"] is True
        assert metadata["budget"] == 1000000
        assert metadata["products_in_budget"] >= 2
    
    def test_filter_budget_sorting(self, sample_products):
        """Test that filtered products are sorted correctly"""
        filtered, _ = BudgetFilter.filter_by_budget(
            sample_products,
            budget=1000000
        )
        
        # Should be sorted by price (in budget first)
        in_budget = [p for p in filtered if p["harga"] <= 1000000]
        assert len(in_budget) > 0
        
        # Check sorting
        for i in range(len(in_budget) - 1):
            assert in_budget[i]["harga"] <= in_budget[i+1]["harga"]
    
    def test_budget_with_tolerance(self, sample_products):
        """Test budget with tolerance percentage"""
        filtered, metadata = BudgetFilter.filter_by_budget(
            sample_products,
            budget=500000,
            tolerance_percent=10.0
        )
        
        assert metadata["tolerance_percent"] == 10.0
        assert metadata["tolerance_amount"] == 50000
        assert metadata["extended_budget"] == 550000
    
    def test_get_budget_recommendations(self, sample_products):
        """Test getting budget recommendations"""
        recommendations = BudgetFilter.get_budget_recommendations(
            sample_products,
            budget=1000000
        )
        
        assert recommendations["status"] == "success"
        assert recommendations["min_price"] == 100000
        assert recommendations["max_price"] == 3000000
        assert "budget_coverage" in recommendations
    
    def test_get_budget_recommendations_no_budget(self, sample_products):
        """Test recommendations without budget"""
        recommendations = BudgetFilter.get_budget_recommendations(sample_products)
        
        assert recommendations["status"] == "success"
        assert "budget" not in recommendations
    
    def test_add_budget_info_to_product(self, sample_products):
        """Test adding budget info to product"""
        product = sample_products[0].copy()
        
        updated = BudgetFilter.add_budget_info_to_product(product, budget=500000)
        
        assert "budget_info" in updated
        assert updated["budget_info"]["status"] == "dalam_budget"
        assert updated["budget_info"]["difference"] > 0
    
    def test_add_budget_info_above_budget(self, sample_products):
        """Test budget info for product above budget"""
        product = sample_products[3].copy()  # 3M product
        
        updated = BudgetFilter.add_budget_info_to_product(product, budget=1000000)
        
        assert updated["budget_info"]["status"] == "di_atas_budget"
        assert updated["budget_info"]["difference"] > 0
    
    def test_categorize_by_price_range(self, sample_products):
        """Test categorizing products by price range"""
        categorized = BudgetFilter.categorize_by_price_range(
            sample_products,
            ranges=[(0, 500000), (500000, 2000000), (2000000, float('inf'))]
        )
        
        assert len(categorized) > 0
        assert sum(len(products) for products in categorized.values()) == len(sample_products)
    
    def test_calculate_best_value(self, sample_products):
        """Test finding best value product"""
        best = BudgetFilter.calculate_best_value(sample_products)
        
        assert best is not None
        # Should pick highest trust score
        assert best["trust_score"] == max(p["trust_score"] for p in sample_products)
    
    def test_calculate_best_value_with_budget(self, sample_products):
        """Test best value with budget constraint"""
        best = BudgetFilter.calculate_best_value(
            sample_products,
            budget=1000000
        )
        
        assert best is not None
        assert best["harga"] <= 1000000
    
    def test_calculate_best_value_empty(self):
        """Test best value with empty products"""
        best = BudgetFilter.calculate_best_value([])
        assert best is None
    
    def test_budget_recommendations_empty_products(self):
        """Test recommendations with empty products"""
        recommendations = BudgetFilter.get_budget_recommendations([])
        assert recommendations["status"] == "no_products"


class TestIntegration:
    """Integration tests for verification and budget features"""
    
    @pytest.fixture
    def tracker(self):
        """Create tracker for integration tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = VerifiedProductTracker(storage_dir=tmpdir)
            yield tracker
    
    def test_workflow_verify_and_check(self, tracker):
        """Test complete verification workflow"""
        product_name = "Integration Test Product"
        
        # Verify product
        tracker.record_verification(
            product_name=product_name,
            product_url="https://...",
            ai_analysis={"trust_score": 88, "skor_value": 82},
            user_note="Test verification"
        )
        
        # Check status
        status = tracker.get_verification_status(product_name)
        assert status["is_verified"] is True
        assert status["verification_count"] >= 1
    
    def test_workflow_multiple_verifications_and_patterns(self, tracker):
        """Test multiple verifications and pattern generation"""
        products = ["Product A", "Product B", "Product A", "Product C", "Product A"]
        
        for product in products:
            tracker.record_verification(
                product_name=product,
                product_url="https://...",
                ai_analysis={"rekomendasi": "DIREKOMENDASIKAN"}
            )
        
        patterns = tracker.get_patterns()
        assert patterns["total_verified"] >= len(products)
        assert "Product A" in patterns["verified_products"]
    
    def test_budget_and_best_value(self):
        """Test budget filtering and best value selection"""
        products = [
            {"nama_produk": "P1", "harga": 300000, "trust_score": 70},
            {"nama_produk": "P2", "harga": 600000, "trust_score": 90},
            {"nama_produk": "P3", "harga": 1200000, "trust_score": 85},
        ]
        
        # Filter by budget
        filtered, metadata = BudgetFilter.filter_by_budget(products, budget=800000)
        assert metadata["products_in_budget"] >= 2
        
        # Get best value
        best = BudgetFilter.calculate_best_value(filtered, budget=800000)
        assert best["trust_score"] == 90  # P2 has highest trust within budget
