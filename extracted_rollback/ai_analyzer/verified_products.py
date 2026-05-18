"""
Product Verification System - Positive feedback to reinforce AI learning

This module tracks verified correct analyses to:
1. Reinforce correct AI patterns
2. Build a library of verified analyses
3. Improve AI confidence over time
4. Provide reference data for future searches
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VerifiedProductTracker:
    """
    Tracks verified correct product analyses.
    
    Stores verified products to:
    1. Reinforce correct AI decisions
    2. Build confidence data
    3. Speed up future similar searches
    4. Track patterns in correct analyses
    """
    
    def __init__(self, storage_dir: str = "ai_learning_data"):
        """
        Initialize the verified product tracker.
        
        Args:
            storage_dir: Directory to store learning data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.verified_file = self.storage_dir / "verified_products.jsonl"
        self.verified_patterns_file = self.storage_dir / "verified_patterns.json"
        
        logger.info(f"Verified products system initialized at: {self.storage_dir}")
    
    def record_verification(
        self,
        product_name: str,
        product_url: str,
        ai_analysis: Dict[str, Any],
        user_note: str = ""
    ) -> Dict[str, Any]:
        """
        Record a verified correct product analysis.
        
        Args:
            product_name: Name of the product
            product_url: URL to the product
            ai_analysis: The AI analysis that was correct
            user_note: Optional user note about why it's correct
            
        Returns:
            Dictionary with verification record
        """
        verified_count = 1
        
        # Check if product already verified
        existing = self._find_existing_verification(product_name)
        if existing:
            verified_count = existing.get("verified_count", 1) + 1
            logger.info(f"Product verified again: {product_name} (count: {verified_count})")
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "product_name": product_name,
            "product_url": product_url,
            "ai_analysis": ai_analysis,
            "user_note": user_note,
            "verified_count": verified_count
        }
        
        # Append to file
        with open(self.verified_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        # Update patterns
        self._update_patterns()
        
        logger.info(f"Verified product recorded: {product_name}")
        return record
    
    def _find_existing_verification(self, product_name: str) -> Optional[Dict]:
        """Find existing verification and return the one with highest count."""
        if not self.verified_file.exists():
            return None
        
        best_match = None
        best_count = 0
        
        with open(self.verified_file, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if self._string_similarity(record.get("product_name", ""), product_name) > 0.95:
                    count = record.get("verified_count", 1)
                    if count > best_count:
                        best_count = count
                        best_match = record
        
        return best_match
    
    def get_verified_product(self, product_name: str, threshold: float = 0.8) -> Optional[Dict]:
        """
        Get verified analysis for a similar product.
        
        Returns the most recent/highest verified_count record for the product.
        
        Args:
            product_name: Product name to search for
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            Verified product record or None
        """
        if not self.verified_file.exists():
            return None
        
        best_match = None
        best_similarity = threshold
        best_count = 0
        
        with open(self.verified_file, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                similarity = self._string_similarity(
                    record.get("product_name", ""),
                    product_name
                )
                
                # Prefer records with higher verified_count, then higher similarity
                if similarity > best_similarity or (similarity > threshold and record.get("verified_count", 1) > best_count):
                    best_similarity = similarity
                    best_count = record.get("verified_count", 1)
                    best_match = record
        
        if best_match:
            logger.info(f"Found verified product: {best_match['product_name']} (similarity: {best_similarity:.2%}, count: {best_count})")
            return best_match
        
        return None
    
    def get_verified_count(self, product_name: str) -> int:
        """Get how many times a product was verified."""
        verified = self.get_verified_product(product_name, threshold=0.95)
        if verified:
            return verified.get("verified_count", 1)
        return 0
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get statistical patterns from verified products."""
        if self.verified_patterns_file.exists():
            with open(self.verified_patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "total_verified": 0,
            "verified_products": {},
            "common_recommendations": {}
        }
    
    def _update_patterns(self):
        """Update verified patterns automatically."""
        if not self.verified_file.exists():
            patterns = {
                "total_verified": 0,
                "verified_products": {},
                "common_recommendations": {}
            }
        else:
            patterns = {
                "total_verified": 0,
                "verified_products": {},
                "common_recommendations": {}
            }
            
            with open(self.verified_file, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line)
                    patterns["total_verified"] += 1
                    
                    # Track verified products
                    product = record.get("product_name", "Unknown")
                    patterns["verified_products"][product] = record.get("verified_count", 1)
                    
                    # Track recommendations
                    rekomendasi = record.get("ai_analysis", {}).get("rekomendasi", "UNKNOWN")
                    if rekomendasi not in patterns["common_recommendations"]:
                        patterns["common_recommendations"][rekomendasi] = 0
                    patterns["common_recommendations"][rekomendasi] += 1
        
        with open(self.verified_patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Updated verified patterns: {patterns['total_verified']} verified products")
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate word-based similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0.0-1.0)
        """
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 or not words2:
            return 1.0 if str1.lower() == str2.lower() else 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def export_verified_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Export comprehensive report of verified products.
        
        Args:
            output_file: Optional file path to save report
            
        Returns:
            Report dictionary
        """
        if not self.verified_file.exists():
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_verified": 0,
                "patterns": self.get_patterns(),
                "verified_products": []
            }
        else:
            verified_products = []
            with open(self.verified_file, 'r', encoding='utf-8') as f:
                for line in f:
                    verified_products.append(json.loads(line))
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_verified": len(verified_products),
                "patterns": self.get_patterns(),
                "verified_products": verified_products
            }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"Verified products report exported to: {output_file}")
        
        return report
    
    def get_confidence_boost(self, product_name: str) -> float:
        """
        Get confidence boost percentage for a product (0-100%).
        
        Higher verification count = higher confidence.
        
        Args:
            product_name: Product name
            
        Returns:
            Confidence boost percentage (0.0-100.0)
        """
        verified = self.get_verified_product(product_name, threshold=0.8)
        if verified:
            count = verified.get("verified_count", 1)
            # Each verification adds 5%, capped at +50%
            return min(count * 5.0, 50.0)
        
        return 0.0
    
    def get_verification_status(self, product_name: str) -> Dict[str, Any]:
        """
        Get full verification status for a product.
        
        Args:
            product_name: Product name
            
        Returns:
            Status dictionary
        """
        verified = self.get_verified_product(product_name, threshold=0.8)
        
        return {
            "product_name": product_name,
            "is_verified": verified is not None,
            "verification_count": verified.get("verified_count", 0) if verified else 0,
            "confidence_boost": self.get_confidence_boost(product_name),
            "verified_analysis": verified.get("ai_analysis") if verified else None,
            "user_note": verified.get("user_note", "") if verified else ""
        }
    
    def clear_old_verifications(self, keep_days: int = 365):
        """
        Remove verified products older than specified days.
        
        Args:
            keep_days: Number of days to keep
        """
        if not self.verified_file.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        kept_records = []
        deleted_count = 0
        
        with open(self.verified_file, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                record_date = datetime.fromisoformat(record["timestamp"])
                
                if record_date > cutoff_date:
                    kept_records.append(record)
                else:
                    deleted_count += 1
        
        with open(self.verified_file, 'w', encoding='utf-8') as f:
            for record in kept_records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        self._update_patterns()
        
        logger.info(f"Cleared old verified products: {deleted_count} deleted, {len(kept_records)} kept")
