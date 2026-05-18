"""
Unit tests for AI Learning System

Run with: python -m pytest test_ai_learning.py -v
"""

import pytest
import json
import os
from pathlib import Path
from ai_analyzer.mistake_tracker import AIMistakeTracker, ProductAnalyzerWithLearning


class TestAIMistakeTracker:
    """Test the AI mistake tracking system"""
    
    @pytest.fixture
    def tracker(self):
        """Create a tracker instance for testing"""
        # Use temporary directory for tests
        tracker = AIMistakeTracker(storage_dir=".test_ai_learning")
        yield tracker
        # Cleanup
        import shutil
        if Path(".test_ai_learning").exists():
            shutil.rmtree(".test_ai_learning")
    
    def test_initialize_tracker(self, tracker):
        """Verify tracker initializes with correct directory structure"""
        assert tracker.storage_dir.exists()
        assert tracker.mistakes_file is not None
        assert tracker.corrections_file is not None
        assert tracker.patterns_file is not None
    
    def test_record_mistake(self, tracker):
        """Test recording an AI mistake"""
        tracker.record_mistake(
            product_name="Razer DeathAdder V3",
            product_url="https://tokopedia.com/...",
            ai_analysis={"trust_score": 50, "skor_value": 40},
            user_feedback="Harga terlalu tinggi, AI salah nilai",
            correction={"trust_score": 30, "skor_value": 25}
        )
        
        # Verify file was created and has content
        assert tracker.mistakes_file.exists()
        
        with open(tracker.mistakes_file, "r") as f:
            line = f.readline()
            record = json.loads(line)
            assert record["product_name"] == "Razer DeathAdder V3"
            assert record["user_feedback"] == "Harga terlalu tinggi, AI salah nilai"
    
    def test_find_similar_mistakes(self, tracker):
        """Test finding similar past mistakes"""
        # Record multiple mistakes
        tracker.record_mistake(
            product_name="Razer Mouse Gaming",
            product_url="https://...",
            ai_analysis={"trust_score": 50},
            user_feedback="Salah",
            correction={}
        )
        
        tracker.record_mistake(
            product_name="Razer Keyboard Gaming",
            product_url="https://...",
            ai_analysis={"trust_score": 50},
            user_feedback="Salah",
            correction={}
        )
        
        # Find similar to "Razer Mouse"
        similar = tracker.get_similar_mistakes("Razer Mouse Gaming", threshold=0.5)
        assert len(similar) >= 1
        assert similar[0]["product_name"] == "Razer Mouse Gaming"
    
    def test_should_skip_analysis(self, tracker):
        """Test detection of problematic products"""
        # Record same product failing twice
        for i in range(2):
            tracker.record_mistake(
                product_name="Problematic Product ABC",
                product_url="https://...",
                ai_analysis={"trust_score": 50},
                user_feedback="AI salah lagi",
                correction={}
            )
        
        # Should now recommend skipping analysis
        should_skip = tracker.should_skip_analysis("Problematic Product ABC")
        assert should_skip == True
    
    def test_get_correction_for_mistake(self, tracker):
        """Test retrieving known corrections"""
        correction_data = {"trust_score": 30, "skor_value": 25, "rekomendasi": "TIDAK"}
        
        tracker.record_mistake(
            product_name="Consistent Problem",
            product_url="https://...",
            ai_analysis={"trust_score": 50},
            user_feedback="Selalu salah",
            correction=correction_data
        )
        
        correction = tracker.get_correction_for_mistake("Consistent Problem")
        assert correction is not None
        assert correction["trust_score"] == 30
    
    def test_string_similarity(self, tracker):
        """Test string similarity calculation"""
        # Exact match
        sim = tracker._string_similarity("razer mouse", "razer mouse")
        assert sim == 1.0
        
        # Similar strings
        sim = tracker._string_similarity("razer mouse gaming", "razer mouse")
        assert sim > 0.5
        
        # Different strings
        sim = tracker._string_similarity("razer mouse", "logitech keyboard")
        assert sim < 0.3
    
    def test_get_patterns(self, tracker):
        """Test pattern analysis"""
        # Record multiple mistakes
        for i in range(3):
            tracker.record_mistake(
                product_name="Product A",
                product_url="https://...",
                ai_analysis={},
                user_feedback="Feedback type 1",
                correction={}
            )
        
        tracker.record_mistake(
            product_name="Product B",
            product_url="https://...",
            ai_analysis={},
            user_feedback="Feedback type 2",
            correction={}
        )
        
        patterns = tracker.get_patterns()
        assert patterns["total_mistakes"] == 4
        assert "Product A" in patterns["problematic_products"]
        assert patterns["problematic_products"]["Product A"] == 3
    
    def test_export_mistakes_report(self, tracker):
        """Test exporting a comprehensive report"""
        # Record some mistakes
        for i in range(2):
            tracker.record_mistake(
                product_name=f"Product {i}",
                product_url="https://...",
                ai_analysis={},
                user_feedback="Test feedback",
                correction={}
            )
        
        report = tracker.export_mistakes_report()
        assert report["total_mistakes"] == 2
        assert "timestamp" in report
        assert "patterns" in report
        assert len(report["mistakes"]) == 2
    
    def test_export_to_file(self, tracker):
        """Test exporting report to file"""
        tracker.record_mistake(
            product_name="Test Product",
            product_url="https://...",
            ai_analysis={},
            user_feedback="Test",
            correction={}
        )
        
        output_file = ".test_report.json"
        tracker.export_mistakes_report(output_file=output_file)
        
        assert Path(output_file).exists()
        
        with open(output_file, "r") as f:
            report = json.load(f)
            assert report["total_mistakes"] == 1
        
        # Cleanup
        Path(output_file).unlink()
    
    def test_clear_old_mistakes(self, tracker):
        """Test clearing old mistakes (keep_days)"""
        from datetime import datetime, timedelta
        
        # Record a mistake (will have current timestamp)
        tracker.record_mistake(
            product_name="Recent",
            product_url="https://...",
            ai_analysis={},
            user_feedback="Recent",
            correction={}
        )
        
        # Clearing with keep_days=365 (one year) should not remove recent mistakes
        removed = tracker.clear_old_mistakes(keep_days=365)
        assert removed == 0  # Recent mistake should still be there
        
        # Verify the mistake is still there
        mistakes_file_size = tracker.mistakes_file.stat().st_size
        assert mistakes_file_size > 0  # File should have content
    
    def test_empty_tracker_queries(self, tracker):
        """Test querying empty tracker returns sensible defaults"""
        # Query non-existent product
        similar = tracker.get_similar_mistakes("Non Existent Product")
        assert similar == []
        
        # Query correction for non-existent product
        correction = tracker.get_correction_for_mistake("Non Existent Product")
        assert correction is None
        
        # Check if should skip non-existent product
        should_skip = tracker.should_skip_analysis("Non Existent Product")
        assert should_skip == False
        
        # Get patterns from empty tracker
        patterns = tracker.get_patterns()
        assert patterns["total_mistakes"] == 0


class TestProductAnalyzerWithLearning:
    """Test the learning wrapper for ProductAIAnalyzer"""
    
    @pytest.fixture
    def mock_analyzer(self):
        """Create a mock analyzer"""
        class MockAnalyzer:
            async def analyze(self, products, batch_size, limit, banned_items):
                from ai_analyzer.product_analyzer import AnalysisResult
                return [
                    AnalysisResult(
                        nama_produk="Test Product",
                        harga=100000,
                        harga_display="Rp 100.000",
                        nama_toko="Test Shop",
                        trust_score=80.0,
                        trust_label="Terpercaya",
                        trust_alasan="Test reason",
                        skor_value=75.0,
                        rekomendasi="DIREKOMENDASIKAN",
                        catatan_ai="Test comment",
                        rating_toko=4.8,
                        terjual="100",
                        badge_toko="Power Merchant",
                        lokasi_toko="Jakarta",
                        url_produk="https://...",
                        url_gambar="https://..."
                    )
                ]
        
        return MockAnalyzer()
    
    @pytest.fixture
    def tracker(self):
        """Create test tracker"""
        tracker = AIMistakeTracker(storage_dir=".test_ai_learning_wrapper")
        yield tracker
        # Cleanup
        import shutil
        if Path(".test_ai_learning_wrapper").exists():
            shutil.rmtree(".test_ai_learning_wrapper")
    
    @pytest.mark.asyncio
    async def test_analyze_with_learning_no_warnings(self, mock_analyzer, tracker):
        """Test analysis with learning when no past mistakes exist"""
        analyzer = ProductAnalyzerWithLearning(mock_analyzer, tracker)
        
        products = [{"nama": "New Product", "harga": 100000}]
        results, warnings = await analyzer.analyze_with_learning(products)
        
        assert len(results) == 1
        assert len(warnings) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_learning_generates_warning(self, mock_analyzer, tracker):
        """Test analysis generates warning for problematic product"""
        # Pre-record multiple failures for a product
        for i in range(2):
            tracker.record_mistake(
                product_name="Problematic Mouse",
                product_url="https://...",
                ai_analysis={},
                user_feedback="AI salah",
                correction={}
            )
        
        analyzer = ProductAnalyzerWithLearning(mock_analyzer, tracker)
        products = [{"nama": "Problematic Mouse", "harga": 100000}]
        results, warnings = await analyzer.analyze_with_learning(products)
        
        assert len(warnings) >= 1
        assert "Problematic Mouse" in warnings[0]


class TestMistakeTrackerIntegration:
    """Integration tests for the learning system"""
    
    @pytest.fixture
    def tracker(self):
        """Create a tracker instance"""
        tracker = AIMistakeTracker(storage_dir=".test_integration")
        yield tracker
        # Cleanup
        import shutil
        if Path(".test_integration").exists():
            shutil.rmtree(".test_integration")
    
    def test_full_workflow(self, tracker):
        """Test complete mistake tracking workflow"""
        # 1. Record initial mistake
        tracker.record_mistake(
            product_name="Gaming Mouse Razer",
            product_url="https://tokopedia.com/gaming-mouse-razer",
            ai_analysis={"trust_score": 45, "skor_value": 35},
            user_feedback="AI terlalu pesimis tentang produk ini",
            correction={"trust_score": 75, "skor_value": 80}
        )
        
        # 2. Check patterns
        patterns = tracker.get_patterns()
        assert patterns["total_mistakes"] == 1
        
        # 3. Query similar mistakes
        similar = tracker.get_similar_mistakes("Gaming Mouse Razer", threshold=0.8)
        assert len(similar) == 1
        
        # 4. Get correction
        correction = tracker.get_correction_for_mistake("Gaming Mouse Razer")
        assert correction is not None
        assert correction["trust_score"] == 75
        
        # 5. Export report
        report = tracker.export_mistakes_report()
        assert report["total_mistakes"] == 1
        assert "Gaming Mouse Razer" in report["patterns"]["problematic_products"]
    
    def test_multiple_mistakes_same_product(self, tracker):
        """Test tracking multiple mistakes for same product"""
        product = "Consistent Problem Product"
        
        # Record 3 mistakes
        for i in range(3):
            tracker.record_mistake(
                product_name=product,
                product_url="https://...",
                ai_analysis={"error": f"mistake_{i}"},
                user_feedback=f"Feedback {i}",
                correction={}
            )
        
        # Verify
        patterns = tracker.get_patterns()
        assert patterns["problematic_products"][product] == 3
        
        # Should skip analysis
        should_skip = tracker.should_skip_analysis(product)
        assert should_skip == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
