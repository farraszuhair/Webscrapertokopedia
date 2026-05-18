"""
Budget-Aware Product Filtering - Smart filtering based on budget constraints

This module filters products based on budget to:
1. Find products within specified budget
2. Recommend products closest to budget
3. Prevent AI from scraping only the cheapest items
4. Improve shopping experience with budget awareness
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class BudgetFilter:
    """
    Filters and ranks products based on budget constraints.
    
    Provides smart filtering to help users find products that match
    their budget, not just the cheapest available.
    """
    
    def __init__(self):
        """Initialize budget filter."""
        pass
    
    @staticmethod
    def filter_by_budget(
        products: List[Dict[str, Any]],
        budget: Optional[int] = None,
        tolerance_percent: float = 10.0
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Filter and sort products based on budget.
        
        If budget is specified:
        - Returns products within budget first (sorted by price)
        - Then products above budget, sorted by proximity
        
        Args:
            products: List of product dictionaries
            budget: Maximum budget in IDR (optional)
            tolerance_percent: How much above budget to include (e.g., 10%)
            
        Returns:
            Tuple of (filtered_products, metadata)
        """
        if not budget:
            # No budget specified, return all products sorted by price
            return (
                sorted(products, key=lambda p: p.get("harga", float('inf'))),
                {
                    "budget_applied": False,
                    "budget": None,
                    "products_in_budget": len(products),
                    "products_above_budget": 0,
                    "budget_status": "No budget specified"
                }
            )
        
        # Separate products: within budget and above budget
        in_budget = []
        above_budget = []
        
        tolerance_amount = budget * (tolerance_percent / 100.0)
        extended_budget = budget + tolerance_amount
        
        for product in products:
            price = product.get("harga", float('inf'))
            
            if price <= budget:
                in_budget.append(product)
            elif price <= extended_budget:
                # Within tolerance
                above_budget.append(product)
        
        # Sort both lists by price
        in_budget.sort(key=lambda p: p.get("harga", float('inf')))
        above_budget.sort(key=lambda p: abs(p.get("harga", float('inf')) - budget))
        
        # Combine: within budget first, then tolerance
        filtered_products = in_budget + above_budget
        
        metadata = {
            "budget_applied": True,
            "budget": budget,
            "tolerance_percent": tolerance_percent,
            "tolerance_amount": int(tolerance_amount),
            "extended_budget": int(extended_budget),
            "products_in_budget": len(in_budget),
            "products_above_budget": len(above_budget),
            "budget_status": (
                f"{len(in_budget)} products within budget, "
                f"{len(above_budget)} products within {tolerance_percent}% tolerance"
            )
        }
        
        logger.info(
            f"Budget filter: Budget={budget:,}, "
            f"In-budget={len(in_budget)}, "
            f"Tolerance={len(above_budget)}"
        )
        
        return filtered_products, metadata
    
    @staticmethod
    def get_budget_recommendations(
        products: List[Dict[str, Any]],
        budget: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get detailed budget recommendations.
        
        Args:
            products: List of product dictionaries
            budget: Maximum budget in IDR
            
        Returns:
            Dictionary with recommendations
        """
        if not products:
            return {
                "status": "no_products",
                "message": "No products available"
            }
        
        prices = [p.get("harga", float('inf')) for p in products if p.get("harga")]
        
        if not prices:
            return {
                "status": "no_prices",
                "message": "No price data available"
            }
        
        recommendations = {
            "status": "success",
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": int(sum(prices) / len(prices)),
            "products_count": len(products),
        }
        
        if budget:
            in_budget = sum(1 for p in prices if p <= budget)
            recommendations.update({
                "budget": budget,
                "products_in_budget": in_budget,
                "budget_coverage": f"{(in_budget / len(prices) * 100):.1f}%",
                "recommendation": (
                    f"Budget covers {in_budget}/{len(prices)} products"
                    if in_budget > 0
                    else f"No products within budget. Cheapest is {min(prices):,}"
                )
            })
        
        return recommendations
    
    @staticmethod
    def add_budget_info_to_product(
        product: Dict[str, Any],
        budget: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add budget-related information to a product.
        
        Args:
            product: Product dictionary
            budget: Budget in IDR
            
        Returns:
            Product dictionary with budget info added
        """
        if not budget:
            product["budget_info"] = None
            return product
        
        price = product.get("harga", 0)
        
        if price <= budget:
            status = "dalam_budget"
            difference = budget - price
            percentage = (difference / budget * 100)
        else:
            status = "di_atas_budget"
            difference = price - budget
            percentage = (difference / budget * 100)
        
        product["budget_info"] = {
            "status": status,
            "difference": difference,
            "difference_percent": f"{percentage:.1f}%",
            "dalam_budget": status == "dalam_budget"
        }
        
        return product
    
    @staticmethod
    def categorize_by_price_range(
        products: List[Dict[str, Any]],
        ranges: Optional[List[Tuple[int, int]]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize products by price ranges.
        
        Args:
            products: List of product dictionaries
            ranges: List of (min, max) tuples for ranges
            
        Returns:
            Dictionary with price range categories
        """
        if ranges is None:
            # Default ranges
            ranges = [
                (0, 500000),           # Under 500k
                (500000, 1000000),     # 500k-1M
                (1000000, 2000000),    # 1M-2M
                (2000000, 5000000),    # 2M-5M
                (5000000, float('inf')) # 5M+
            ]
        
        categorized = {}
        
        for min_price, max_price in ranges:
            range_key = f"{min_price:,}-{max_price:,}" if max_price != float('inf') else f"{min_price:,}+"
            categorized[range_key] = [
                p for p in products
                if min_price <= p.get("harga", 0) < max_price
            ]
        
        return categorized
    
    @staticmethod
    def calculate_best_value(
        products: List[Dict[str, Any]],
        budget: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best value product based on trust score and price.
        
        Products with highest trust score are best value.
        If budget specified, prefer products within budget.
        
        Args:
            products: List of product dictionaries
            budget: Budget in IDR
            
        Returns:
            Best value product or None
        """
        if not products:
            return None
        
        # Sort by trust score (descending)
        sorted_products = sorted(
            products,
            key=lambda p: p.get("trust_score", 0),
            reverse=True
        )
        
        if budget:
            # Prefer products within budget
            in_budget = [p for p in sorted_products if p.get("harga", 0) <= budget]
            if in_budget:
                best = in_budget[0]
            else:
                best = sorted_products[0]
        else:
            best = sorted_products[0]
        
        return best
