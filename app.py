#!/usr/bin/env python3
"""
app.py - Tokopedia scraper entrypoint.

Run command stays:
python app.py
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).parent.resolve()
PORT = int(os.environ.get("PORT", 3000))
REQ_FILE = PROJECT_DIR / "requirements.txt"


def log(message: str, level: str = "INFO") -> None:
    """Small startup logger; runtime logging lives in src/utils/logger.py."""
    print(f"[{level}] {message}", flush=True)


def check_python_deps() -> None:
    """Check core imports only. User installs with requirements.txt."""
    required = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "selenium": "selenium",
        "webdriver_manager": "webdriver-manager",
        "httpx": "httpx",
    }
    missing = [pip_name for import_name, pip_name in required.items() if not importlib.util.find_spec(import_name)]
    if not missing:
        log("Python dependencies found.", "OK")
        return

    log(f"Missing Python packages: {', '.join(missing)}", "ERROR")
    log(f"Install with: {sys.executable} -m pip install -r {REQ_FILE}", "ERROR")
    sys.exit(1)


def check_node_deps() -> None:
    """Puppeteer worker needs Node plus npm packages."""
    if not shutil.which("node"):
        log("Node.js not found. Puppeteer mode will fail until Node is installed.", "WARN")
        return

    package_dir = PROJECT_DIR / "node_modules" / "puppeteer"
    if not package_dir.exists():
        log("node_modules/puppeteer not found. Run: npm install", "WARN")
        return

    try:
        version = subprocess.run(
            ["node", "--version"],
            cwd=str(PROJECT_DIR),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        log(f"Node ready: {version}", "OK")
    except Exception as exc:
        log(f"Node check failed: {exc}", "WARN")


def main() -> None:
    print()
    print("+--------------------------------------+")
    print("| Tokopedia Scraper - Puppeteer/Selenium |")
    print("+--------------------------------------+")
    print()

    check_python_deps()
    check_node_deps()

    log(f"Starting FastAPI server on http://127.0.0.1:{PORT}", "INFO")
    try:
        import uvicorn

        uvicorn.run(
            "src.server.main:app",
            host="127.0.0.1",
            port=PORT,
            log_level="info",
            reload=False,
        )
    except KeyboardInterrupt:
        log("Server stopped by user.", "OK")
    except Exception as exc:
        log(f"Server crashed: {exc}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
