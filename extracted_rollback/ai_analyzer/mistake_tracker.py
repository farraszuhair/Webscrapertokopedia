"""
AI Learning System - Stores and learns from AI mistakes

This module tracks incorrect AI analyses and prevents the AI from
making the same mistakes again.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AIMistakeTracker:
    """
    Tracks AI mistakes and provides prevention mechanisms.
    
    Stores historical incorrect analyses to:
    1. Prevent repeating the same mistakes
    2. Identify patterns in AI errors
    3. Improve prompt engineering over time
    """
    
    def __init__(self, storage_dir: str = "ai_learning_data"):
        """
        Initialize the mistake tracker.
        
        Args:
            storage_dir: Directory to store learning data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.mistakes_file = self.storage_dir / "mistakes.jsonl"
        self.corrections_file = self.storage_dir / "corrections.jsonl"
        self.patterns_file = self.storage_dir / "patterns.json"
        
        logger.info(f"AI Learning system initialized at: {self.storage_dir}")
    
    def record_mistake(
        self, 
        product_name: str, 
        product_url: str,
        ai_analysis: Dict[str, Any],
        user_feedback: str,
        correction: Dict[str, Any]
    ) -> None:
        """
        Record an AI mistake for learning.
        
        Args:
            product_name: Name of the product analyzed incorrectly
            product_url: URL of the product
            ai_analysis: The incorrect AI analysis
            user_feedback: Why the analysis was wrong
            correction: What the correct analysis should have been
        """
        mistake_record = {
            "timestamp": datetime.now().isoformat(),
            "product_name": product_name,
            "product_url": product_url,
            "ai_analysis": ai_analysis,
            "user_feedback": user_feedback,
            "correction": correction
        }
        
        # Append to JSONL file (one JSON object per line)
        with open(self.mistakes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(mistake_record, ensure_ascii=False) + "\n")
        
        logger.info(f"Recorded AI mistake for: {product_name}")
        
        # Update patterns
        self._update_patterns()
    
    def get_similar_mistakes(
        self, 
        product_name: str, 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar past mistakes.
        
        Args:
            product_name: Product name to check
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar past mistakes
        """
        if not self.mistakes_file.exists():
            return []
        
        similar = []
        product_name_lower = product_name.lower()
        
        with open(self.mistakes_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    past_product = record.get("product_name", "").lower()
                    
                    # Simple string similarity check
                    similarity = self._string_similarity(product_name_lower, past_product)
                    if similarity >= threshold:
                        similar.append(record)
                except json.JSONDecodeError:
                    continue
        
        return similar
    
    def should_skip_analysis(self, product_name: str) -> bool:
        """
        Check if a product is known to cause AI mistakes.
        
        Args:
            product_name: Product name to check
            
        Returns:
            True if product should be re-analyzed manually, False otherwise
        """
        similar = self.get_similar_mistakes(product_name, threshold=0.8)
        return len(similar) >= 2  # If same product made AI fail twice, skip
    
    def get_correction_for_mistake(self, product_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the known correct analysis for a product that previously failed.
        
        Args:
            product_name: Product name to check
            
        Returns:
            Correction data if available, None otherwise
        """
        similar = self.get_similar_mistakes(product_name, threshold=0.95)
        if similar:
            # Return the most recent correction
            return similar[-1].get("correction")
        return None
    
    def _update_patterns(self) -> None:
        """
        Analyze mistake patterns and store insights.
        This helps identify common AI error types.
        """
        if not self.mistakes_file.exists():
            return
        
        patterns = {
            "total_mistakes": 0,
            "mistake_categories": {},
            "problematic_products": {},
            "common_feedbacks": {}
        }
        
        with open(self.mistakes_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    patterns["total_mistakes"] += 1
                    
                    # Track problematic products
                    product = record.get("product_name", "Unknown")
                    patterns["problematic_products"][product] = \
                        patterns["problematic_products"].get(product, 0) + 1
                    
                    # Track feedback types
                    feedback = record.get("user_feedback", "")
                    patterns["common_feedbacks"][feedback] = \
                        patterns["common_feedbacks"].get(feedback, 0) + 1
                        
                except json.JSONDecodeError:
                    continue
        
        # Sort by frequency
        if patterns["problematic_products"]:
            patterns["problematic_products"] = dict(
                sorted(
                    patterns["problematic_products"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]  # Top 10
            )
        
        with open(self.patterns_file, "w", encoding="utf-8") as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Updated patterns. Total mistakes: {patterns['total_mistakes']}")
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get current mistake patterns."""
        if not self.patterns_file.exists():
            return {
                "total_mistakes": 0,
                "mistake_categories": {},
                "problematic_products": {},
                "common_feedbacks": {}
            }
        
        with open(self.patterns_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate simple string similarity (0-1).
        Using word overlap method.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        
        if not words1 or not words2:
            return 1.0 if s1 == s2 else 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def export_mistakes_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report of AI mistakes.
        
        Args:
            output_file: Optional file to save report to
            
        Returns:
            Report dictionary
        """
        if not self.mistakes_file.exists():
            return {"total_mistakes": 0, "mistakes": []}
        
        mistakes = []
        with open(self.mistakes_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        mistakes.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_mistakes": len(mistakes),
            "patterns": self.get_patterns(),
            "mistakes": mistakes
        }
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"Mistakes report exported to: {output_file}")
        
        return report
    
    def clear_old_mistakes(self, keep_days: int = 30) -> int:
        """
        Remove mistakes older than keep_days.
        
        Args:
            keep_days: Keep mistakes from last N days
            
        Returns:
            Number of mistakes removed
        """
        if not self.mistakes_file.exists():
            return 0
        
        from datetime import timedelta, datetime as dt
        cutoff_date = dt.now() - timedelta(days=keep_days)
        
        kept_mistakes = []
        removed_count = 0
        
        with open(self.mistakes_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    record_date = dt.fromisoformat(record.get("timestamp", ""))
                    if record_date > cutoff_date:
                        kept_mistakes.append(record)
                    else:
                        removed_count += 1
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Rewrite file with kept mistakes
        with open(self.mistakes_file, "w", encoding="utf-8") as f:
            for record in kept_mistakes:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        logger.info(f"Cleared {removed_count} old mistakes (older than {keep_days} days)")
        return removed_count


class ProductAnalyzerWithLearning:
    """
    Wrapper for ProductAIAnalyzer that incorporates learning from mistakes.
    Uses past corrections to improve analysis for known products.
    """
    
    def __init__(self, base_analyzer, mistake_tracker: Optional[AIMistakeTracker] = None):
        """
        Initialize the learning wrapper.
        
        Args:
            base_analyzer: The ProductAIAnalyzer instance
            mistake_tracker: The AIMistakeTracker instance
        """
        self.analyzer = base_analyzer
        self.tracker = mistake_tracker or AIMistakeTracker()
    
    async def analyze_with_learning(
        self,
        products_dict: List[dict],
        batch_size: int = 10,
        limit: int = 10,
        banned_items: List[str] = None
    ) -> tuple[List[Any], List[str]]:
        """
        Analyze products with learning from past mistakes.
        Uses corrections from trained mistakes to improve results.
        
        Args:
            products_dict: Products to analyze
            batch_size: Batch size for processing
            limit: Max products to analyze
            banned_items: Items to ban
            
        Returns:
            Tuple of (analysis_results, warnings_about_past_mistakes)
        """
        warnings = []
        
        # Perform analysis normally
        results = await self.analyzer.analyze(
            products_dict,
            batch_size=batch_size,
            limit=limit,
            banned_items=banned_items
        )
        
        # Apply corrections from trained mistakes
        corrected_results = []
        for result in results:
            product_name = result.nama_produk
            
            # Check if we have a known correction for this product
            correction = self.tracker.get_correction_for_mistake(product_name)
            
            if correction:
                # Apply the correction to the result
                logger.info(f"Applying trained correction for: {product_name}")
                
                # Update scores and recommendation from correction
                if 'trust_score' in correction:
                    result.trust_score = float(correction['trust_score'])
                if 'skor_value' in correction:
                    result.skor_value = float(correction['skor_value'])
                if 'rekomendasi' in correction:
                    result.rekomendasi = str(correction['rekomendasi'])
                
                # Update labels based on new trust_score
                if result.trust_score > 80:
                    result.trust_label = "Terpercaya"
                    result.trust_alasan = "Produk telah diverifikasi dari data historis"
                elif result.trust_score > 50:
                    result.trust_label = "Cukup Terpercaya"
                    result.trust_alasan = "Data historis menunjukkan kepercayaan sedang"
                else:
                    result.trust_label = "Tidak Terpercaya"
                    result.trust_alasan = "Data historis menunjukkan masalah pada produk ini"
                
                warnings.append(f"✓ '{product_name}' - Menggunakan analisis terlatih dari data historis")
            else:
                # Check if product is known to cause mistakes (for warning)
                if self.tracker.should_skip_analysis(product_name):
                    warnings.append(f"⚠️ '{product_name}' - Riwayat analisis bermasalah, verifikasi manual disarankan")
        
        # Combine results (with corrections applied)
        final_results = results  # Results already modified in-place
        
        return final_results, warnings
