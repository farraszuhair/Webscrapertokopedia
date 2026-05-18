"""
engine_selector.py - Evaluates and selects the best working scraping engine.
Fallback chain: Puppeteer -> Rollback (Selenium)
"""
from typing import List, Dict, Any, Tuple
from src.utils.logger import log
from src.server.progress import update_progress
from src.utils.eta import ETACalculator
from src.scraper.puppeteer_engine import PuppeteerEngine
from src.scraper.rollback_engine import RollbackEngine

async def run_scraper_chain(search_id: str, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Attempts to scrape data using a chain of engines.
    Returns (success, products, error)
    """
    update_progress(search_id, stage="engine_selecting", percent=5, message="Memilih engine scraper...")
    
    # Engine 1: Puppeteer Engine
    log(f"[{search_id}]", "[ENGINE] Trying puppeteer", "INFO")
    pw_engine = PuppeteerEngine(search_id)
    success, products, error = await pw_engine.scrape(query, raw_target, eta_calc)
    
    if success and products:
        log(f"[{search_id}]", f"[ENGINE] Selected puppeteer_engine. Found {len(products)} products.", "OK")
        return True, products, ""
        
    log(f"[{search_id}]", f"[ENGINE] Puppeteer failed: {error}. Switching to rollback scraper.", "WARN")
    
    # Update progress visibly to show fallback
    update_progress(search_id, stage="switching_to_rollback", percent=45, message="Puppeteer gagal, pindah ke rollback scraper...")
    
    # Engine 2: Rollback Engine (Selenium)
    rb_engine = RollbackEngine(search_id)
    success, products, error = await rb_engine.scrape(query, raw_target, eta_calc)
    
    if success and products:
        log(f"[{search_id}]", f"[ENGINE] Selected rollback_engine. Found {len(products)} products.", "OK")
        return True, products, ""
        
    # All failed
    error_msg = "Semua engine scraping gagal. Puppeteer gagal, Rollback gagal."
    log(f"[{search_id}]", f"[ENGINE] {error_msg}", "ERROR")
    return False, [], error_msg
