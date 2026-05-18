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

from src.scraper.normalizer import normalize_products
from src.scraper.puppeteer_engine import PuppeteerEngine
from src.scraper.rollback_engine import RollbackEngine
from src.server.progress import update_progress
from src.utils.logger import log


@dataclass
class EngineRunResult:
    engine: str
    ok: bool
    products: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""
    duration_seconds: float = 0.0

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
    """Create a scraper engine by name."""
    if name == "puppeteer":
        return PuppeteerEngine(search_id)
    if name == "rollback":
        return RollbackEngine(search_id)
    raise ValueError(f"Unknown scraper engine: {name}")


async def run_engine(search_id: str, engine_name: str, query: str, raw_target: int, eta_calc) -> EngineRunResult:
    """Run one engine and normalize its output schema."""
    started = time.perf_counter()
    update_progress(
        search_id,
        active_engine=engine_name,
        stage=f"{engine_name}_starting",
        message=f"Menjalankan engine {engine_name}...",
        elapsed_seconds=eta_calc.get_elapsed(),
    )

    try:
        engine = _make_engine(engine_name, search_id)
        success, products, error = await engine.scrape(query, raw_target, eta_calc)
        normalized = normalize_products(products, engine_name)
        duration = time.perf_counter() - started

        if success and normalized:
            log(f"[{search_id}]", f"[ENGINE] {engine_name} found {len(normalized)} products", "OK")
            return EngineRunResult(engine_name, True, normalized, "", duration)

        final_error = error or f"{engine_name} tidak menemukan produk."
        log(f"[{search_id}]", f"[ENGINE] {engine_name} failed: {final_error}", "WARN")
        return EngineRunResult(engine_name, False, normalized, final_error, duration)
    except Exception as exc:
        duration = time.perf_counter() - started
        error = f"{engine_name} unhandled exception: {exc}"
        log(f"[{search_id}]", f"[ENGINE] {error}", "ERROR")
        return EngineRunResult(engine_name, False, [], error, duration)


async def run_scraper_engines(
    search_id: str,
    query: str,
    raw_target: int,
    eta_calc,
    engine_mode: str = "auto",
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
        run = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
        return EngineSelectionResult(run.ok, mode, "puppeteer", run.products, run.error, runs=[run])

    if mode == "rollback":
        run = await run_engine(search_id, "rollback", query, raw_target, eta_calc)
        return EngineSelectionResult(run.ok, mode, "rollback", run.products, run.error, runs=[run])

    if mode == "compare":
        runs = [
            await run_engine(search_id, "puppeteer", query, raw_target, eta_calc),
            await run_engine(search_id, "rollback", query, raw_target, eta_calc),
        ]
        good_runs = [run for run in runs if run.ok and run.products]
        if not good_runs:
            error = "; ".join(f"{run.engine}: {run.error}" for run in runs)
            return EngineSelectionResult(False, mode, None, [], error, runs=runs)
        selected = max(good_runs, key=lambda run: len(run.products))
        return EngineSelectionResult(True, mode, selected.engine, selected.products, runs=runs)

    puppeteer = await run_engine(search_id, "puppeteer", query, raw_target, eta_calc)
    if puppeteer.ok and puppeteer.products:
        return EngineSelectionResult(True, mode, "puppeteer", puppeteer.products, runs=[puppeteer])

    fallback_message = "Puppeteer gagal, pindah ke Rollback/Selenium..."
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
