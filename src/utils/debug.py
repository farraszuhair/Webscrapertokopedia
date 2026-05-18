"""
debug.py - Handles saving debug artifacts on scraper failure.
Saves HTML, screenshots, and logs.
"""
import os
import json
from pathlib import Path
from src.utils.logger import log

DEBUG_DIR = Path(__file__).parent.parent.parent / "data" / "debug"

def get_debug_dir(search_id: str) -> Path:
    """Gets the debug directory for a search_id."""
    dir_path = DEBUG_DIR / search_id
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

async def save_debug_state(search_id: str, page=None, error_msg: str = ""):
    """Saves error text, html snapshot, and screenshot if page is available."""
    try:
        dir_path = get_debug_dir(search_id)
        
        # Save error txt
        with open(dir_path / "error.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
            
        if page and not page.is_closed():
            try:
                # Save HTML
                html = await page.content()
                with open(dir_path / "page.html", "w", encoding="utf-8") as f:
                    f.write(html)
                    
                # Save Screenshot
                await page.screenshot(path=str(dir_path / "screenshot.png"), full_page=True)
            except Exception as e:
                log("DEBUG", f"HTML/Screenshot unavailable (navigating/closed): {e}", "WARN")
                with open(dir_path / "page.html", "w", encoding="utf-8") as f:
                    f.write("HTML unavailable: page still navigating or closed.")
            
        log("DEBUG", f"Saved debug artifacts for {search_id} to {dir_path}", "OK")
    except Exception as e:
        log("DEBUG", f"Failed to save debug artifacts for {search_id}: {e}", "ERROR")

def save_raw_products(search_id: str, products: list):
    """Saves raw extracted products to JSON."""
    try:
        dir_path = get_debug_dir(search_id)
        with open(dir_path / "raw_products.json", "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log("DEBUG", f"Failed to save raw products for {search_id}: {e}", "ERROR")

def save_progress_state(search_id: str, progress: dict):
    """Saves progress state to JSON."""
    try:
        dir_path = get_debug_dir(search_id)
        with open(dir_path / "progress.json", "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log("DEBUG", f"Failed to save progress for {search_id}: {e}", "ERROR")

def save_debug_state_sync(search_id: str, driver=None, error_msg: str = ""):
    """Synchronous version for Selenium driver."""
    try:
        dir_path = get_debug_dir(search_id)
        with open(dir_path / "error.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        if driver:
            try:
                html = driver.page_source
                with open(dir_path / "page.html", "w", encoding="utf-8") as f:
                    f.write(html)
                driver.save_screenshot(str(dir_path / "screenshot.png"))
            except Exception as e:
                log("DEBUG", f"Could not extract sync page content: {e}", "WARN")
        log("DEBUG", f"Saved sync debug artifacts for {search_id}", "OK")
    except Exception as e:
        log("DEBUG", f"Failed to save sync debug artifacts: {e}", "ERROR")
