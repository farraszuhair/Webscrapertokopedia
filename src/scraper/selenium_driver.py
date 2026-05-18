import os
import traceback
from pathlib import Path
from typing import Tuple, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.utils.logger import log

def create_chrome_driver(search_id: str, debug_dir: Path) -> Tuple[Optional[webdriver.Chrome], str]:
    """
    Creates a robust Selenium Chrome driver.
    Attempts to use Selenium Manager natively (Selenium 4.6+),
    falls back to webdriver-manager if there is a mismatch.
    """
    # 1. Setup Options
    options = Options()
    
    # Headless config
    headless_env = os.environ.get("SCRAPER_HEADLESS", "true").lower()
    is_headless = headless_env == "true"
    
    if is_headless:
        options.add_argument("--headless=new")
        
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=id-ID")
    options.page_load_strategy = "eager"

    error_logs = []

    # Attempt 1: Native Selenium Manager (Selenium 4.6+)
    try:
        log(f"[{search_id}]", "[SELENIUM] Starting Chrome via Selenium Manager", "INFO")
        # In Selenium 4.6+, webdriver.Chrome() automatically downloads the matched chromedriver.
        driver = webdriver.Chrome(options=options)
        
        # Verify version
        browser_version = driver.capabilities.get("browserVersion", "Unknown")
        chromedriver_version = driver.capabilities.get("chrome", {}).get("chromedriverVersion", "Unknown")
        log(f"[{search_id}]", f"[SELENIUM] Chrome version detected: {browser_version}", "OK")
        log(f"[{search_id}]", "[SELENIUM] Browser started OK", "OK")
        
        driver.set_page_load_timeout(45)
        driver.set_script_timeout(30)
        return driver, ""
    except Exception as e:
        tb1 = traceback.format_exc()
        error_logs.append(f"Selenium Manager failed:\n{tb1}")
        log(f"[{search_id}]", "[SELENIUM] Native Selenium Manager failed, attempting webdriver-manager fallback...", "WARN")
    
    # Attempt 2: Webdriver-Manager Fallback
    try:
        log(f"[{search_id}]", "[SELENIUM] Starting Chrome via webdriver-manager", "INFO")
        
        # Install matched driver
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        
        browser_version = driver.capabilities.get("browserVersion", "Unknown")
        log(f"[{search_id}]", f"[SELENIUM] Chrome version detected via fallback: {browser_version}", "OK")
        log(f"[{search_id}]", "[SELENIUM] Browser started OK", "OK")
        
        driver.set_page_load_timeout(45)
        driver.set_script_timeout(30)
        return driver, ""
    except Exception as e:
        tb2 = traceback.format_exc()
        error_logs.append(f"Webdriver-Manager failed:\n{tb2}")
        
    # Both failed, write debug artifact
    error_msg = "\n\n".join(error_logs)
    log(f"[{search_id}]", "[SELENIUM] Driver Chrome otomatis gagal dibuat. Update Chrome/Selenium atau cek network webdriver-manager.", "ERROR")
    
    # Write artifact
    try:
        os.makedirs(debug_dir, exist_ok=True)
        with open(debug_dir / "selenium_driver_error.txt", "w", encoding="utf-8") as f:
            f.write("=== SELENIUM DRIVER STARTUP FAILURE ===\n")
            f.write(error_msg)
    except Exception:
        pass
        
    return None, error_msg

def safe_quit_driver(driver: webdriver.Chrome):
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
