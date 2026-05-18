"""
debug.py - Handles saving debug artifacts on scraper failure.
"""
import os
import json
from pathlib import Path
from typing import Any
from src.utils.logger import log

DEBUG_DIR = Path(__file__).parent.parent.parent / "data" / "debug"

def get_debug_dir(search_id: str) -> Path:
    """Gets the debug directory for a search_id."""
    dir_path = DEBUG_DIR / search_id
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def safe_save_debug(search_id: str, error: str, products: list, progress: dict = None, page_source: str = None):
    """
    Safely saves debug state without throwing new errors.
    """
    try:
        dir_path = get_debug_dir(search_id)
        
        # Save error.txt
        try:
            with open(dir_path / "error.txt", "w", encoding="utf-8") as f:
                f.write(str(error))
        except Exception: pass
        
        # Save raw_products.json
        try:
            with open(dir_path / "raw_products.json", "w", encoding="utf-8") as f:
                json.dump(products or [], f, indent=2, ensure_ascii=False)
        except Exception: pass
        
        # Save progress.json
        try:
            if progress:
                with open(dir_path / "progress.json", "w", encoding="utf-8") as f:
                    json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception: pass
        
        # Save HTML
        try:
            with open(dir_path / "page.html", "w", encoding="utf-8") as f:
                if page_source:
                    f.write(page_source)
                else:
                    f.write("HTML unavailable: page navigating/closed")
        except Exception: pass

        log("DEBUG", f"Saved debug artifacts for {search_id} to {dir_path}", "OK")
    except Exception as e:
        log("DEBUG", f"Failed to save debug artifacts for {search_id}: {e}", "ERROR")

def save_budget_filter_debug(search_id: str, payload: dict[str, Any], engine_name: str | None = None) -> str:
    """
    Save budget filter decisions. Normal mode uses the required exact filename;
    compare mode gets per-engine files so runs do not overwrite each other.
    """
    dir_path = get_debug_dir(search_id)
    filename = "budget_filter_debug.json"
    if engine_name:
        filename = f"budget_filter_debug_{engine_name}.json"

    output_path = dir_path / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    log("DEBUG", f"Saved budget filter debug to {output_path}", "OK")
    return str(output_path)

def save_category_filter_debug(search_id: str, payload: dict[str, Any], engine_name: str) -> str:
    """Save category filter decisions per engine."""
    dir_path = get_debug_dir(search_id)
    output_path = dir_path / f"category_filter_debug_{engine_name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    log("DEBUG", f"Saved category filter debug to {output_path}", "OK")
    return str(output_path)

def save_debug_state_sync(search_id: str, driver=None, error_msg: str = ""):
    """Synchronous version for Selenium driver."""
    from src.server.progress import get_progress
    page_source = None
    if driver:
        try:
            page_source = driver.page_source
        except Exception:
            pass
            
    safe_save_debug(
        search_id=search_id,
        error=error_msg,
        products=[], 
        progress=get_progress(search_id),
        page_source=page_source
    )
