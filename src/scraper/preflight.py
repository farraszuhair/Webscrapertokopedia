"""
preflight.py - Browser preflight check.

Before scraping, verify that the browser actually opens Tokopedia and NOT
a Chrome network error page. This is the ONLY correct fix for raw = 0 when
ERR_HTTP2_PROTOCOL_ERROR or similar network failures occur.

Returns a clear dict so the pipeline can stop cleanly and show real diagnosis
instead of lying with "selector failed" or "0 products found".
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Any

from src.utils.logger import log


# Strings that indicate Chrome is showing an error page, NOT a real site.
# These are matched against page title and body text.
CHROME_ERROR_SIGNALS = [
    "err_http2_protocol_error",
    "err_connection_reset",
    "err_connection_refused",
    "err_connection_timed_out",
    "err_name_not_resolved",
    "err_address_unreachable",
    "this site can't be reached",
    "situs ini tidak dapat dijangkau",
    "no internet",
    "dns_probe_finished_no_internet",
    "dns_probe_finished_nxdomain",
]

# Tokopedia page signals - at least one of these must exist on the real page.
TOKOPEDIA_REAL_PAGE_SIGNALS = [
    "tokopedia",
    "toped",
]


def _detect_error_type(title: str, body: str, url: str) -> str | None:
    """
    Scan title + body + url for known Chrome network error codes.
    Returns a short error type key, or None if no error detected.
    """
    combined = f"{title} {body} {url}".lower()

    # Map raw signals to clean error_type keys.
    patterns = [
        (r"err_http2_protocol_error", "http2_protocol_error"),
        (r"err_connection_reset", "connection_reset"),
        (r"err_connection_refused", "connection_refused"),
        (r"err_connection_timed_out", "connection_timed_out"),
        (r"err_name_not_resolved", "name_not_resolved"),
        (r"err_address_unreachable", "address_unreachable"),
        (r"dns_probe_finished_no_internet", "no_internet"),
        (r"dns_probe_finished_nxdomain", "dns_nxdomain"),
        (r"this site can.t be reached", "site_unreachable"),
        (r"situs ini tidak dapat dijangkau", "site_unreachable_id"),
    ]

    for pattern, error_key in patterns:
        if re.search(pattern, combined):
            return error_key

    # Fallback: about:blank means navigation never happened.
    if url.strip().lower() in ("about:blank", "chrome://newtab/", ""):
        return "blank_page"

    return None


def _is_real_tokopedia_page(title: str, body: str, url: str) -> bool:
    """Check if the page looks like a real Tokopedia page."""
    combined = f"{title} {body} {url}".lower()
    return any(signal in combined for signal in TOKOPEDIA_REAL_PAGE_SIGNALS)


def build_preflight_result(
    url: str,
    title: str,
    body_sample: str,
    current_url: str,
    load_time_ms: float,
    engine: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build the standardized preflight result dict.

    opened_real_page=False means: scraper must NOT attempt extraction.
    The engine opened a Chrome error page. Show diagnosis and stop.
    """
    error_type = _detect_error_type(title, body_sample, current_url)
    is_real = _is_real_tokopedia_page(title, body_sample, current_url)

    # Even if no known error detected, if no Tokopedia signal exists it's wrong.
    if error_type is None and not is_real:
        error_type = "unknown_non_tokopedia_page"

    opened_real_page = (error_type is None) and is_real

    result: dict[str, Any] = {
        "engine": engine,
        "target_url": url,
        "current_url": current_url,
        "opened_real_page": opened_real_page,
        "error_type": error_type,
        "page_title": title,
        "body_text_sample": body_sample[:500],
        "load_time_ms": round(load_time_ms, 1),
        "message": (
            "Browser opened real Tokopedia product page."
            if opened_real_page
            else f"Browser opened Chrome error/non-Tokopedia page. error_type={error_type}. "
                 "Extraction cannot work on this page. Stopping cleanly."
        ),
    }

    if extra:
        result.update(extra)

    return result


def save_preflight_debug(search_id: str, result: dict[str, Any], engine: str) -> str:
    """Write preflight result to data/debug/<search_id>/<engine>_preflight.json."""
    from src.utils.debug import get_debug_dir
    debug_dir = get_debug_dir(search_id)
    debug_dir.mkdir(parents=True, exist_ok=True)
    path = debug_dir / f"{engine}_preflight.json"
    try:
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)
    except Exception as exc:
        log(f"[{search_id}]", f"[PREFLIGHT] Failed to save debug: {exc}", "WARN")
        return ""


async def preflight_puppeteer(
    search_id: str,
    url: str,
    timeout_ms: int = 20000,
) -> dict[str, Any]:
    """
    Run Puppeteer-based preflight via a tiny inline Node script.
    Checks if the given URL opens a real Tokopedia page or an error page.
    """
    script = """
const puppeteer = require('puppeteer');
(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
             '--disable-http2']  // disable HTTP/2 to reduce ERR_HTTP2_PROTOCOL_ERROR
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1366, height: 768 });
    // Pretend to be a real Chrome browser
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36');

    let navError = null;
    try {
      await page.goto(process.env.PREFLIGHT_URL, {
        waitUntil: 'domcontentloaded',
        timeout: parseInt(process.env.PREFLIGHT_TIMEOUT || '15000')
      });
    } catch (e) {
      navError = e.message || String(e);
    }

    const currentUrl = page.url();
    const title = await page.title().catch(() => '');
    const bodyText = await page.evaluate(() =>
      document.body ? (document.body.innerText || '').slice(0, 1000) : ''
    ).catch(() => '');

    process.stdout.write(JSON.stringify({
      current_url: currentUrl,
      title,
      body_text: bodyText,
      nav_error: navError
    }) + '\\n');
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
})().catch(e => {
  process.stdout.write(JSON.stringify({ error: e.message || String(e) }) + '\\n');
  process.exit(1);
});
"""
    started = time.perf_counter()
    env = {
        "PREFLIGHT_URL": url,
        "PREFLIGHT_TIMEOUT": str(timeout_ms),
    }

    import os
    full_env = {**os.environ, **env}
    worker_dir = Path(__file__).parent

    try:
        process = await asyncio.create_subprocess_exec(
            "node",
            "--eval",
            script,
            cwd=str(worker_dir.parent.parent),  # project root where node_modules lives
            env=full_env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=(timeout_ms / 1000) + 5
            )
        except asyncio.TimeoutError:
            process.kill()
            return build_preflight_result(
                url=url, title="", body_sample="", current_url="",
                load_time_ms=(time.perf_counter() - started) * 1000,
                engine="puppeteer",
                extra={"nav_error": "preflight_process_timeout"},
            )

        elapsed_ms = (time.perf_counter() - started) * 1000
        raw = stdout.decode("utf-8", errors="replace").strip()

        try:
            data = json.loads(raw.split("\n")[0])
        except json.JSONDecodeError:
            data = {}

        if "error" in data:
            return build_preflight_result(
                url=url, title="", body_sample=data.get("error", ""),
                current_url="", load_time_ms=elapsed_ms, engine="puppeteer",
                extra={"nav_error": data.get("error")},
            )

        result = build_preflight_result(
            url=url,
            title=data.get("title", ""),
            body_sample=data.get("body_text", ""),
            current_url=data.get("current_url", ""),
            load_time_ms=elapsed_ms,
            engine="puppeteer",
            extra={"nav_error": data.get("nav_error")},
        )

        path = save_preflight_debug(search_id, result, "puppeteer")
        result["debug_path"] = path
        log(f"[{search_id}]", f"[PREFLIGHT] puppeteer opened_real_page={result['opened_real_page']} error_type={result['error_type']}", "INFO")
        return result

    except FileNotFoundError:
        # Node not installed
        return build_preflight_result(
            url=url, title="", body_sample="", current_url="",
            load_time_ms=0, engine="puppeteer",
            extra={"nav_error": "node_not_found"},
        )
    except Exception as exc:
        return build_preflight_result(
            url=url, title="", body_sample="", current_url="",
            load_time_ms=(time.perf_counter() - started) * 1000,
            engine="puppeteer",
            extra={"nav_error": str(exc)},
        )


def preflight_selenium(
    search_id: str,
    url: str,
    timeout_s: int = 20,
) -> dict[str, Any]:
    """
    Selenium-based preflight. Synchronous because Selenium is blocking.
    Call this from asyncio.to_thread().
    """
    from src.scraper.selenium_driver import create_chrome_driver, safe_quit_driver

    debug_dir = Path("data/debug") / search_id
    started = time.perf_counter()
    driver, driver_error = create_chrome_driver(search_id, debug_dir)

    if not driver:
        return build_preflight_result(
            url=url, title="", body_sample="", current_url="",
            load_time_ms=(time.perf_counter() - started) * 1000,
            engine="rollback",
            extra={"nav_error": f"driver_bootstrap_failed: {driver_error}"},
        )

    try:
        driver.set_page_load_timeout(timeout_s)
        nav_error = None
        try:
            driver.get(url)
        except Exception as exc:
            nav_error = str(exc)

        elapsed_ms = (time.perf_counter() - started) * 1000
        current_url = driver.current_url
        title = driver.title
        try:
            body_text = driver.execute_script(
                "return document.body ? (document.body.innerText || '').slice(0, 1000) : '';"
            ) or ""
        except Exception:
            body_text = ""

        result = build_preflight_result(
            url=url,
            title=title,
            body_sample=body_text,
            current_url=current_url,
            load_time_ms=elapsed_ms,
            engine="rollback",
            extra={"nav_error": nav_error},
        )

        path = save_preflight_debug(search_id, result, "rollback")
        result["debug_path"] = path
        log(f"[{search_id}]", f"[PREFLIGHT] rollback opened_real_page={result['opened_real_page']} error_type={result['error_type']}", "INFO")
        return result

    finally:
        safe_quit_driver(driver)


async def run_preflight(
    search_id: str,
    engine: str,
    query: str = "laptop gaming",
) -> dict[str, Any]:
    """
    Run preflight for the given engine.
    Uses a simple search URL (no pmin/pmax) per the spec.
    """
    from src.scraper.url_builder import build_tokopedia_search_url
    url = build_tokopedia_search_url(query)

    if engine == "puppeteer":
        return await preflight_puppeteer(search_id, url)

    if engine in ("rollback", "selenium"):
        return await asyncio.to_thread(preflight_selenium, search_id, url)

    # For "auto" or "compare", try both and return the first success or both failures.
    pup = await preflight_puppeteer(search_id, url)
    if pup["opened_real_page"]:
        return pup
    roll = await asyncio.to_thread(preflight_selenium, search_id, url)
    # Return whichever is better; if both fail, return rollback with combined error.
    if roll["opened_real_page"]:
        return roll
    roll["puppeteer_preflight"] = pup
    return roll
