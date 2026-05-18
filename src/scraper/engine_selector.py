"""
engine_selector.py - Explicit engine selection.

Modes:
- auto: Puppeteer first, rollback only when Puppeteer fails or finds nothing.
- puppeteer: Puppeteer only, no hidden fallback.
- rollback: Selenium rollback only.
- compare: Run both and return both raw result sets.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from src.scraper.category_filter import filter_laptop_candidates
from src.scraper.normalizer import normalize_products
from src.scraper.puppeteer_engine import PuppeteerEngine
from src.scraper.query_expander import budget_url_range, expand_query_variants
from src.scraper.rollback_engine import RollbackEngine
from src.scraper.url_builder import build_tokopedia_search_urls_for_variant
from src.server.progress import update_progress
from src.utils.debug import get_debug_dir, save_zero_raw_debug
from src.utils.logger import log


def _existing_zero_raw_debug(search_id: str, engine_name: str) -> str:
    """Return engine zero-raw debug file if the engine already wrote it."""
    path = get_debug_dir(search_id) / f"{engine_name}_zero_raw_debug.json"
    return str(path) if path.exists() else ""


@dataclass
class EngineRunResult:
    engine: str
    ok: bool
    products: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    duration_seconds: float = 0.0
    query_variants: list[str] = field(default_factory=list)
    urls_tried: list[str] = field(default_factory=list)
    debug_files: list[str] = field(default_factory=list)

    @property
    def raw_products_found(self) -> int:
        return len(self.products)

    def laptop_candidate_count(self, query: str) -> int:
        """Count category candidates without mutating the stored raw result."""
        normalized = normalize_products(self.products, self.engine)
        return filter_laptop_candidates(normalized, query).candidate_count


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
    """Create a scraper engine by name."""
    if name == "puppeteer":
        return PuppeteerEngine(search_id)
    if name == "rollback":
        return RollbackEngine(search_id)
    raise ValueError(f"Unknown scraper engine: {name}")


async def run_engine(
    search_id: str,
    engine_name: str,
    query: str,
    raw_target: int,
    eta_calc,
    budget: Any = None,
    tolerance: Any = 20,
) -> EngineRunResult:
    """Run one engine and return raw extracted products."""
    started = time.perf_counter()
    variants = expand_query_variants(query)
    min_price, max_price = budget_url_range(budget, tolerance)
    urls_to_try: list[str] = []
    log(f"[{search_id}]", f"[QUERY] variants={len(variants)}", "INFO")
    for index, variant in enumerate(variants, start=1):
        log(f"[{search_id}]", f"[QUERY] variant[{index}]={variant}", "INFO")
        for url in build_tokopedia_search_urls_for_variant(variant, min_price, max_price):
            urls_to_try.append(url)
            log(f"[{search_id}]", f"[QUERY] url={url}", "INFO")

    update_progress(
        search_id,
        active_engine=engine_name,
        stage=f"{engine_name}_starting",
        message=f"Menjalankan {engine_name} dengan {len(variants)} query variant...",
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    try:
        engine = _make_engine(engine_name, search_id)
        success, products, error = await engine.scrape(
            query,
            raw_target,
            eta_calc,
            query_variants=variants,
            min_price=min_price,
            max_price=max_price,
        )
        duration = time.perf_counter() - started

        if success and products:
            log(f"[{search_id}]", f"[ENGINE] {engine_name} raw products={len(products)}", "OK")
            return EngineRunResult(engine_name, True, products, "", duration, variants, urls_to_try)

        final_error = error or f"{engine_name} tidak menemukan produk."
        debug_path = _existing_zero_raw_debug(search_id, engine_name) or save_zero_raw_debug(
            search_id,
            engine_name,
            {
                "engine": engine_name,
                "query": query,
                "query_variants": variants,
                "urls_tried": urls_to_try,
                "errors": [final_error],
            },
        )
        log(f"[{search_id}]", f"[ENGINE] {engine_name} failed: {final_error}", "WARN")
        return EngineRunResult(engine_name, False, products or [], final_error, duration, variants, urls_to_try, [debug_path] if debug_path else [])
    except Exception as exc:
        duration = time.perf_counter() - started
        error = f"{engine_name} unhandled exception: {exc}"
        debug_path = save_zero_raw_debug(
            search_id,
            engine_name,
            {
                "engine": engine_name,
                "query": query,
                "query_variants": variants,
                "urls_tried": urls_to_try,
                "errors": [error],
            },
        )
        log(f"[{search_id}]", f"[ENGINE] {error}", "ERROR")
        return EngineRunResult(engine_name, False, [], error, duration, variants, urls_to_try, [debug_path] if debug_path else [])


async def run_scraper_engines(
    search_id: str,
    query: str,
    raw_target: int,
    eta_calc,
    engine_mode: str = "auto",
    budget: Any = None,
    tolerance: Any = 20,
) -> EngineSelectionResult:
    """Run scraper engines according to the requested mode."""
    mode = engine_mode if engine_mode in {"auto", "puppeteer", "rollback", "compare"} else "auto"
    update_progress(
        search_id,
        engine_mode=mode,
        stage="engine_selecting",
        percent=5,
        message=f"Memilih engine: {mode}",
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    if mode == "puppeteer":
        run = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc, budget, tolerance)
        return EngineSelectionResult(run.ok, mode, "puppeteer", run.products, run.error, runs=[run])

    if mode == "rollback":
        run = await run_engine(search_id, "rollback", query, raw_target, eta_calc, budget, tolerance)
        return EngineSelectionResult(run.ok, mode, "rollback", run.products, run.error, runs=[run])

    if mode == "compare":
        runs = [
            await run_engine(search_id, "puppeteer", query, raw_target, eta_calc, budget, tolerance),
            await run_engine(search_id, "rollback", query, raw_target, eta_calc, budget, tolerance),
        ]
        good_runs = [run for run in runs if run.ok and run.products]
        if not good_runs:
            error = "; ".join(f"{run.engine}: {run.error}" for run in runs)
            return EngineSelectionResult(False, mode, None, [], error, runs=runs)
        selected = max(good_runs, key=lambda run: len(run.products))
        return EngineSelectionResult(True, mode, selected.engine, selected.products, runs=runs)

    puppeteer = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc, budget, tolerance)
    if puppeteer.ok and puppeteer.products and puppeteer.laptop_candidate_count(query) > 0:
        return EngineSelectionResult(True, mode, "puppeteer", puppeteer.products, runs=[puppeteer])

    fallback_message = "Puppeteer tidak menghasilkan kandidat laptop valid, pindah ke Rollback/Selenium..."
    update_progress(
        search_id,
        active_engine="rollback",
        stage="switching_to_rollback",
        percent=45,
        message=fallback_message,
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    rollback = await run_engine(search_id, "rollback", query, raw_target, eta_calc, budget, tolerance)
    if rollback.ok and rollback.products:
        return EngineSelectionResult(
            True,
            mode,
            "rollback",
            rollback.products,
            fallback_message=fallback_message,
            runs=[puppeteer, rollback],
        )

    combined_error = f"Puppeteer gagal ({puppeteer.error}); Rollback/Selenium gagal ({rollback.error})."
    return EngineSelectionResult(False, mode, None, [], combined_error, fallback_message, [puppeteer, rollback])


async def run_scraper_chain(search_id: str, query: str, raw_target: int, eta_calc):
    """Backward compatible wrapper for old callers."""
    result = await run_scraper_engines(search_id, query, raw_target, eta_calc, "auto")
    return result.ok, result.products, result.error
