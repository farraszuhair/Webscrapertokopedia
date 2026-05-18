"""
selenium_driver.py - Robust Selenium Chrome driver factory.

Strategy:
1. Native Selenium Manager (Selenium 4.6+) - downloads matching chromedriver automatically.
2. webdriver-manager fallback if native fails.
3. Both methods disable HTTP/2 via chrome flags to reduce ERR_HTTP2_PROTOCOL_ERROR.

Key fix: --disable-http2 chrome flag matches Puppeteer's fix.
"""
from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from src.utils.logger import log


def _build_chrome_options() -> Options:
    """Build Chrome options shared by both driver strategies."""
    options = Options()

    headless_env = os.environ.get("SCRAPER_HEADLESS", "true").lower()
    if headless_env == "true":
        options.add_argument("--headless=new")

    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=id-ID")

    # KEY FIX: disable HTTP/2 to reduce ERR_HTTP2_PROTOCOL_ERROR on Tokopedia
    options.add_argument("--disable-http2")

    # Reduce bot detection signals
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Realistic UA
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    options.page_load_strategy = "eager"
    return options


def _set_driver_timeouts(driver: webdriver.Chrome) -> None:
    driver.set_page_load_timeout(45)
    driver.set_script_timeout(30)
    # Remove navigator.webdriver flag to reduce bot detection
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )


def create_chrome_driver(search_id: str, debug_dir: Path) -> Tuple[Optional[webdriver.Chrome], str]:
    """
    Create a Chrome driver using Selenium Manager first, webdriver-manager second.
    Both attempts use HTTP/2-disabled Chrome flags.
    Returns (driver, "") on success or (None, error_message) on failure.
    """
    options = _build_chrome_options()
    error_logs: list[str] = []

    # Attempt 1: Native Selenium Manager (Selenium 4.6+ auto-downloads chromedriver)
    try:
        log(f"[{search_id}]", "[SELENIUM] Starting Chrome via Selenium Manager", "INFO")
        driver = webdriver.Chrome(options=options)
        browser_version = driver.capabilities.get("browserVersion", "Unknown")
        log(f"[{search_id}]", f"[SELENIUM] Chrome {browser_version} started OK", "OK")
        _set_driver_timeouts(driver)
        return driver, ""
    except Exception:
        tb = traceback.format_exc()
        error_logs.append(f"Selenium Manager failed:\n{tb}")
        log(f"[{search_id}]", "[SELENIUM] Native Selenium Manager failed, trying webdriver-manager...", "WARN")

    # Attempt 2: webdriver-manager fallback
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        log(f"[{search_id}]", "[SELENIUM] Starting Chrome via webdriver-manager", "INFO")
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        browser_version = driver.capabilities.get("browserVersion", "Unknown")
        log(f"[{search_id}]", f"[SELENIUM] Chrome {browser_version} started OK via fallback", "OK")
        _set_driver_timeouts(driver)
        return driver, ""
    except Exception:
        tb = traceback.format_exc()
        error_logs.append(f"webdriver-manager failed:\n{tb}")

    # Both failed - write debug artifact
    error_msg = "\n\n".join(error_logs)
    log(f"[{search_id}]", "[SELENIUM] Both driver strategies failed.", "ERROR")

    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
        (debug_dir / "selenium_driver_error.txt").write_text(
            "=== SELENIUM DRIVER STARTUP FAILURE ===\n" + error_msg, encoding="utf-8"
        )
    except Exception:
        pass

    return None, error_msg


def safe_quit_driver(driver: Optional[webdriver.Chrome]) -> None:
    """Quit driver without crashing. Always call in finally blocks."""
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
