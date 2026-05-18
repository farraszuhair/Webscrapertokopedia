"""
base.py - Base interface for scraper engines.
"""
from typing import List, Dict, Any, Tuple
from src.utils.eta import ETACalculator

class BaseEngine:
    def __init__(self, search_id: str):
        self.search_id = search_id
        
    async def scrape(self, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Executes the scraping process.
        Returns: (success_bool, products_list, error_message)
        """
        raise NotImplementedError("Scraper engine must implement scrape()")
    
    async def close(self):
        """Cleanup resources."""
        pass
