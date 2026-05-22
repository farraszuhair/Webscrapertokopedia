"""
engine_selector.py - Run scraper engines in the requested mode.

Clean pipeline per spec:
  preflight -> scrape raw -> normalize -> optional budget filter -> AI Orchestrator -> result

Modes:
- auto:      Puppeteer first, rollback if Puppeteer fails.
- puppeteer: Puppeteer only.
- rollback:  Selenium only.
- selenium:  Selenium only alias.
- compare_both: Both engines, show comparison table with opened_real_page status.

Removed: category_filter import. AI Orchestrator is the semantic filter. Not hardcoded keywords.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from src.scraper.normalizer import normalize_products
from src.scraper.puppeteer_engine import PuppeteerEngine
from src.scraper.query_expander import expand_query_variants
from src.scraper.rollback_engine import RollbackEngine
from src.server.progress import update_progress
from src.utils.debug import get_debug_dir, save_json_debug
from src.utils.logger import log


@dataclass
class EngineRunResult:
    engine: str
    ok: bool
    opened_real_page: bool = False   # did the browser open a real Tokopedia page?
    error_type: str = ""             # http2_protocol_error, blank_page, etc.
    products: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    duration_seconds: float = 0.0
    query_variants: list[str] = field(default_factory=list)
    urls_tried: list[str] = field(default_factory=list)
    debug_files: list[str] = field(default_factory=list)

    @property
    def raw_products_found(self) -> int:
        return len(self.products)


@dataclass
class EngineSelectionResult:
    ok: bool
    mode: str
    selected_engine: str | None = None
    products: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    fallback_message: str | None = None
    runs: list[EngineRunResult] = field(default_factory=list)


def _make_engine(name: str, search_id: str):
    if name == "puppeteer":
        return PuppeteerEngine(search_id)
    if name == "rollback":
        return RollbackEngine(search_id)
    raise ValueError(f"Unknown scraper engine: {name}")


def _existing_zero_raw_debug(search_id: str, engine_name: str) -> str:
    """Return existing engine error debug file path if it exists."""
    for filename in (f"{engine_name}_engine_error.json", f"{engine_name}_zero_raw_debug.json"):
        path = get_debug_dir(search_id) / filename
        if path.exists():
            return str(path)
    return ""


async def run_engine(
    search_id: str,
    engine_name: str,
    query: str,
    raw_target: int,
    eta_calc,
) -> EngineRunResult:
    """
    Run one engine and return raw extracted products.
    No budget passed to engine. Budget filter runs locally after raw products exist.
    No category filter. AI Orchestrator handles semantic relevance.
    """
    started = time.perf_counter()
    variants = expand_query_variants(query)
    urls_to_try: list[str] = []

    log(f"[{search_id}]", f"[QUERY] {engine_name} variants={len(variants)}", "INFO")
    for i, variant in enumerate(variants, 1):
        log(f"[{search_id}]", f"[QUERY] variant[{i}]={variant}", "INFO")

    update_progress(
        search_id,
        active_engine=engine_name,
        stage=f"{engine_name}_starting",
        message=f"Menjalankan {engine_name} dengan {len(variants)} query variant...",
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    try:
        engine = _make_engine(engine_name, search_id)
        # Pass query variants. No min/max price - budget filter runs locally.
        success, products, error = await engine.scrape(
            query,
            raw_target,
            eta_calc,
            query_variants=variants,
            min_price=None,
            max_price=None,
        )
        duration = time.perf_counter() - started

        # Determine if the engine reported a preflight failure
        opened_real_page = True
        error_type = ""
        if not success and error:
            # Parse error_type from error message if present
            if "opened_real_page=false" in error or "error_type=" in error:
                opened_real_page = False
                # Extract error_type from message like "error_type=http2_protocol_error"
                import re
                match = re.search(r"error_type[=:](\w+)", error)
                error_type = match.group(1) if match else "unknown"
            else:
                # Page may have opened but extraction failed
                opened_real_page = bool(products) or success

        if success and products:
            log(f"[{search_id}]", f"[ENGINE] {engine_name} raw={len(products)}", "OK")
            return EngineRunResult(
                engine_name, True, opened_real_page=True,
                products=products, duration_seconds=duration,
                query_variants=variants, urls_tried=urls_to_try,
            )

        # Failed - get debug file path if engine wrote one
        debug_path = _existing_zero_raw_debug(search_id, engine_name)
        log(f"[{search_id}]", f"[ENGINE] {engine_name} failed: {error}", "WARN")
        return EngineRunResult(
            engine_name, False,
            opened_real_page=opened_real_page,
            error_type=error_type,
            products=[],
            error=error or f"{engine_name} did not find products.",
            duration_seconds=duration,
            query_variants=variants,
            urls_tried=urls_to_try,
            debug_files=[debug_path] if debug_path else [],
        )

    except Exception as exc:
        duration = time.perf_counter() - started
        error = f"{engine_name} unhandled exception: {exc}"
        log(f"[{search_id}]", f"[ENGINE] {error}", "ERROR")
        debug_path = _existing_zero_raw_debug(search_id, engine_name)
        return EngineRunResult(
            engine_name, False,
            error=error, duration_seconds=duration,
            query_variants=variants, urls_tried=urls_to_try,
            debug_files=[debug_path] if debug_path else [],
        )


async def run_scraper_engines(
    search_id: str,
    query: str,
    raw_target: int,
    eta_calc,
    engine_mode: str = "auto",
    budget: Any = None,       # kept for API compat, not used here
    tolerance: Any = 20,      # kept for API compat, not used here
) -> EngineSelectionResult:
    """Run scraper engines according to the requested mode."""
    aliases = {"selenium": "rollback", "compare": "compare_both"}
    requested_mode = aliases.get(engine_mode, engine_mode)
    mode = requested_mode if requested_mode in {"auto", "puppeteer", "rollback", "compare_both"} else "auto"
    update_progress(
        search_id,
        engine_mode=mode,
        stage="engine_selecting",
        percent=5,
        message=f"Memilih engine: {mode}",
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    if mode == "puppeteer":
        run = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
        return EngineSelectionResult(run.ok, mode, "puppeteer", run.products, run.error, runs=[run])

    if mode == "rollback":
        run = await run_engine(search_id, "rollback", query, raw_target, eta_calc)
        return EngineSelectionResult(run.ok, mode, "rollback", run.products, run.error, runs=[run])

    if mode == "compare_both":
        # Run both and keep both results for the comparison table
        pup = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
        roll = await run_engine(search_id, "rollback", query, raw_target, eta_calc)
        runs = [pup, roll]
        good_runs = [r for r in runs if r.ok and r.products]
        if not good_runs:
            error = "; ".join(f"{r.engine}: {r.error}" for r in runs)
            return EngineSelectionResult(False, mode, None, [], error, runs=runs)
        selected = max(good_runs, key=lambda r: len(r.products))
        return EngineSelectionResult(True, mode, selected.engine, selected.products, runs=runs)

    # Auto mode: Puppeteer first, rollback if Puppeteer fails
    puppeteer = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
    if puppeteer.ok and puppeteer.products:
        return EngineSelectionResult(True, mode, "puppeteer", puppeteer.products, runs=[puppeteer])

    fallback_message = "Puppeteer gagal atau tidak menemukan produk. Beralih ke Rollback/Selenium..."
    update_progress(
        search_id,
        active_engine="rollback",
        stage="switching_to_rollback",
        percent=45,
        message=fallback_message,
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    rollback = await run_engine(search_id, "rollback", query, raw_target, eta_calc)
    if rollback.ok and rollback.products:
        return EngineSelectionResult(
            True, mode, "rollback", rollback.products,
            fallback_message=fallback_message, runs=[puppeteer, rollback],
        )

    combined_error = (
        f"Puppeteer: {puppeteer.error or 'no products'}; "
        f"Rollback: {rollback.error or 'no products'}."
    )
    return EngineSelectionResult(
        False, mode, None, [], combined_error, fallback_message, [puppeteer, rollback]
    )


async def run_scraper_chain(search_id: str, query: str, raw_target: int, eta_calc):
    """Backward compatible wrapper for old callers."""
    result = await run_scraper_engines(search_id, query, raw_target, eta_calc, "auto")
    return result.ok, result.products, result.error
