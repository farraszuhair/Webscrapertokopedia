#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py - Main entrypoint for Tokopedia Scraper (Python/Playwright)
Handles dependency checks, playwright browser installation, and uvicorn server startup.
Usage: python app.py
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# -------------------------------------------
# CONFIG
# -------------------------------------------
PROJECT_DIR = Path(__file__).parent.resolve()
PORT = int(os.environ.get("PORT", 3000))
REQ_FILE = PROJECT_DIR / "requirements.txt"

# -------------------------------------------
# HELPERS
# -------------------------------------------
def log(msg, level="INFO"):
    colors = {
        "INFO":  "\033[94m[INFO]\033[0m",
        "OK":    "\033[92m[ OK ]\033[0m",
        "WARN":  "\033[93m[WARN]\033[0m",
        "ERROR": "\033[91m[ERR ]\033[0m",
    }
    tag = colors.get(level, "[INFO]")
    print(f"{tag} {msg}", flush=True)

def check_and_install_deps():
    """Checks if requirements are installed, installs via pip if not."""
    required = ["fastapi", "uvicorn", "playwright", "requests", "pydantic"]
    missing = []
    for req in required:
        if not importlib.util.find_spec(req):
            missing.append(req)
            
    if missing:
        log(f"Missing packages: {', '.join(missing)} - running pip install...", "WARN")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE)],
                cwd=str(PROJECT_DIR),
                check=True
            )
            log("Dependencies installed successfully.", "OK")
        except subprocess.CalledProcessError as e:
            log(f"pip install failed: {e}", "ERROR")
            sys.exit(1)
    else:
        log("All Python dependencies satisfied.", "OK")

def check_playwright_browsers():
    """Ensure playwright browsers (chromium) are installed."""
    try:
        # Check if playwright CLI works and browsers are present
        # We only need chromium. 
        log("Checking Playwright browsers...", "INFO")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            cwd=str(PROJECT_DIR),
            check=True,
            capture_output=True # hide output if already installed
        )
        log("Playwright browsers ready.", "OK")
    except subprocess.CalledProcessError as e:
        log(f"Playwright install failed: {e.stderr.decode() if e.stderr else e}", "ERROR")
        sys.exit(1)

# -------------------------------------------
# MAIN
# -------------------------------------------
def main():
    print()
    print("  +---------------------------------------+")
    print("  |   Tokopedia Scraper - Startup (Py)    |")
    print("  +---------------------------------------+")
    print()

    # 1. Dependency check
    check_and_install_deps()
    
    # 2. Playwright check
    check_playwright_browsers()
    
    # 3. Diagnostic startup checks
    print("\n[CHECK] Python OK")
    try:
        import selenium
        print(f"[CHECK] Selenium version: {selenium.__version__}")
        
        # Check webdriver-manager
        import webdriver_manager
        print(f"[CHECK] Webdriver Manager version: {webdriver_manager.__version__}")
    except ImportError:
        print("[CHECK] Selenium/Webdriver-Manager not installed yet")
        
    old_chromedriver_found = False
    for root, dirs, files in os.walk(PROJECT_DIR):
        if "chromedriver.exe" in files:
            old_chromedriver_found = True
            break
            
    print(f"[CHECK] Old chromedriver.exe found: {'yes' if old_chromedriver_found else 'no'}")
    if old_chromedriver_found:
        log("Old chromedriver.exe detected. Ignoring it.", "WARN")
        
    print("[CHECK] Selenium Manager available: yes (included in Selenium 4.6+)")
    print()

    # 4. Start Uvicorn
    log(f"Starting FastAPI server on port {PORT}...", "INFO")
    try:
        import uvicorn
        uvicorn.run(
            "src.server.main:app", 
            host="127.0.0.1", 
            port=PORT, 
            log_level="info",
            reload=False # turn off reload for production stability
        )
    except KeyboardInterrupt:
        print()
        log("Server stopped by user.", "OK")
    except Exception as e:
        log(f"Server crashed: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
