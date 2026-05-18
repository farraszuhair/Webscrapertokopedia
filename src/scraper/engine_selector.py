"""
engine_selector.py - Evaluates and selects the best working scraping engine.
Fallback chain: HTTP -> Playwright -> Selenium
"""
from typing import List, Dict, Any, Tuple
from src.utils.logger import log
from src.utils.eta import ETACalculator
from src.server.progress import update_progress
from src.scraper.tokopedia_http import HttpEngine
from src.scraper.tokopedia_playwright import PlaywrightEngine
from src.scraper.tokopedia_selenium import SeleniumEngine

async def run_scraper_chain(search_id: str, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Attempts to scrape data using a chain of engines.
    Returns (success, products, error)
    """
    update_progress(search_id, stage="selecting_engine", percent=3, message="Memilih engine scraper...")
    
    # Engine 1: HTTP API (Fastest, but likely blocked)
    http_engine = HttpEngine(search_id)
    success, products, error = await http_engine.scrape(query, raw_target, eta_calc)
    if success and products:
        log("ENGINE", f"Selected HTTP API. Found {len(products)} products.", "OK")
        return True, products, ""
    
    log("ENGINE", f"HTTP API failed/blocked: {error}. Falling back to Playwright.", "WARN")
    
    # Engine 2: Playwright (Standard, handles JS)
    pw_engine = PlaywrightEngine(search_id)
    success, products, error = await pw_engine.scrape(query, raw_target, eta_calc)
    if success and products:
        log("ENGINE", f"Selected Playwright. Found {len(products)} products.", "OK")
        return True, products, ""
        
    log("ENGINE", f"Playwright failed: {error}. Falling back to Selenium.", "WARN")
    
    # Engine 3: Selenium (undetected-chromedriver)
    sel_engine = SeleniumEngine(search_id)
    success, products, error = await sel_engine.scrape(query, raw_target, eta_calc)
    if success and products:
        log("ENGINE", f"Selected Selenium. Found {len(products)} products.", "OK")
        return True, products, ""
        
    # All failed
    error_msg = "Semua engine scraping gagal. HTTP gagal, Playwright gagal, Selenium gagal. Cek log server."
    log("ENGINE", error_msg, "ERROR")
    return False, [], error_msg
