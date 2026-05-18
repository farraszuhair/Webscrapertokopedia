"""
engine_selector.py - Evaluates and selects the best working scraping engine.
Fallback chain: Puppeteer -> Rollback (Selenium)
"""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from src.utils.logger import log
from src.server.progress import update_progress
from src.utils.eta import ETACalculator
from src.scraper.puppeteer_engine import PuppeteerEngine
from src.scraper.rollback_engine import RollbackEngine

@dataclass
class ScrapeResult:
    ok: bool = False
    products: list = field(default_factory=list)
    error: str = ""
    engine: str = "unknown"

async def run_scraper_chain(search_id: str, query: str, raw_target: int, eta_calc: ETACalculator) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Attempts to scrape data using a chain of engines.
    Returns (success, products, error) to maintain backward compatibility.
    """
    update_progress(search_id, stage="engine_selecting", percent=5, message="Memilih engine scraper...")
    
    # Engine 1: Puppeteer Engine
    log(f"[{search_id}]", "[ENGINE] Trying puppeteer", "INFO")
    pw_engine = PuppeteerEngine(search_id)
    
    # Guarantee we catch any unexpected exception from the engine
    try:
        success, products, pw_error = await pw_engine.scrape(query, raw_target, eta_calc)
        if success and products:
            log(f"[{search_id}]", f"[ENGINE] Selected puppeteer_engine. Found {len(products)} products.", "OK")
            return True, products, ""
    except Exception as e:
        pw_error = f"Puppeteer unhandled exception: {str(e)}"
        success, products = False, []
        
    log(f"[{search_id}]", f"[ENGINE] Puppeteer failed: {pw_error}. Switching to rollback Selenium", "WARN")
    
    # Update progress visibly to show fallback
    update_progress(
        search_id, 
        stage="switching_to_rollback", 
        percent=45, 
        message="Puppeteer gagal karena HTTP2. Menggunakan rollback Selenium..."
    )
    
    # Engine 2: Rollback Engine (Selenium)
    log(f"[{search_id}]", "[ROLLBACK] Starting rollback scraper...", "INFO")
    rb_engine = RollbackEngine(search_id)
    
    try:
        success, products, rb_error = await rb_engine.scrape(query, raw_target, eta_calc)
        if success and products:
            log(f"[{search_id}]", f"[ENGINE] Selected rollback_engine. Found {len(products)} products.", "OK")
            return True, products, ""
    except Exception as e:
        rb_error = f"Rollback unhandled exception: {str(e)}"
        
    # All failed
    combined_error = f"Puppeteer gagal ({pw_error}) dan rollback scraper juga gagal ({rb_error}). Cek debug log."
    log(f"[{search_id}]", f"[ENGINE] {combined_error}", "ERROR")
    
    return False, [], combined_error
