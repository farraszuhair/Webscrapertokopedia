"""
progress.py - In-memory progress state for polling.
"""
from __future__ import annotations

import time
from typing import Any, Dict


_progress_store: Dict[str, Dict[str, Any]] = {}

MAX_ETA_SECONDS = 3600


def _epoch_ms() -> int:
    return int(time.time() * 1000)


def _coerce_percent(value: Any) -> float:
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _format_eta(seconds: Any) -> str:
    if seconds is None:
        return "ETA: calculating..."
    try:
        seconds_int = max(0, int(round(float(seconds))))
    except (TypeError, ValueError):
        return "ETA: calculating..."
    minutes, secs = divmod(seconds_int, 60)
    return f"{minutes:02d}:{secs:02d}"


def _refresh_time_fields(record: Dict[str, Any], touch_updated: bool = False) -> Dict[str, Any]:
    now_epoch = _epoch_ms()
    started_monotonic = float(record.get("started_at_monotonic") or time.perf_counter())
    elapsed = max(0.0, time.perf_counter() - started_monotonic)
    percent = _coerce_percent(record.get("progress_percent", record.get("percent", 0)))

    record["server_now_epoch_ms"] = now_epoch
    if touch_updated:
        record["updated_at_epoch_ms"] = now_epoch
    record["elapsed_seconds"] = round(elapsed, 1)
    record["progress_percent"] = percent
    record["percent"] = percent

    if record.get("done"):
        record["eta_seconds"] = 0 if record.get("stage") == "done" else None
    elif record.get("eta_seconds") is None and percent > 2:
        eta = elapsed / (percent / 100.0) - elapsed
        record["eta_seconds"] = int(max(0, min(MAX_ETA_SECONDS, eta)))

    record["eta_label"] = _format_eta(record.get("eta_seconds"))
    record["phase"] = record.get("phase") or record.get("stage") or "initializing"
    return record


def init_progress(search_id: str, target: int, raw_target: int, engine_mode: str = "auto") -> None:
    """Initialize a progress record with all fields the frontend expects."""
    now_epoch = _epoch_ms()
    started_monotonic = time.perf_counter()
    _progress_store[search_id] = {
        "search_id": search_id,
        "engine_mode": engine_mode,
        "active_engine": "none",
        "percent": 0.0,
        "progress_percent": 0.0,
        "stage": "initializing",
        "phase": "initializing",
        "message": "Initializing...",
        "found": 0,
        "valid": 0,
        "target": target,
        "raw_target": raw_target,
        "started_at_epoch_ms": now_epoch,
        "started_at_monotonic": started_monotonic,
        "updated_at_epoch_ms": now_epoch,
        "server_now_epoch_ms": now_epoch,
        "elapsed_seconds": 0.0,
        "eta_seconds": None,
        "eta_label": "ETA: calculating...",
        "engine": "none",
        "attempt": 1,
        "max_attempts": 1,
        "done": False,
        "error": None,
    }


def update_progress(search_id: str, **kwargs: Any) -> None:
    """Patch a progress record in place."""
    if search_id not in _progress_store:
        return

    eta_explicit = "eta_seconds" in kwargs
    if "active_engine" in kwargs and "engine" not in kwargs:
        kwargs["engine"] = kwargs["active_engine"]
    if "stage" in kwargs and "phase" not in kwargs:
        kwargs["phase"] = kwargs["stage"]
    if "phase" in kwargs and "stage" not in kwargs:
        kwargs["stage"] = kwargs["phase"]
    if "percent" in kwargs and "progress_percent" not in kwargs:
        kwargs["progress_percent"] = _coerce_percent(kwargs["percent"])
    if "progress_percent" in kwargs and "percent" not in kwargs:
        kwargs["percent"] = _coerce_percent(kwargs["progress_percent"])
    if "percent" in kwargs:
        kwargs["percent"] = _coerce_percent(kwargs["percent"])
    if "progress_percent" in kwargs:
        kwargs["progress_percent"] = _coerce_percent(kwargs["progress_percent"])

    # Let the store compute live elapsed from monotonic time instead of trusting
    # stale caller snapshots.
    kwargs.pop("elapsed_seconds", None)
    if "eta_seconds" in kwargs and kwargs["eta_seconds"] is not None:
        try:
            kwargs["eta_seconds"] = int(max(0, min(MAX_ETA_SECONDS, float(kwargs["eta_seconds"]))))
        except (TypeError, ValueError):
            kwargs["eta_seconds"] = None

    _progress_store[search_id].update(kwargs)
    if not eta_explicit and not _progress_store[search_id].get("done"):
        _progress_store[search_id]["eta_seconds"] = None
    _refresh_time_fields(_progress_store[search_id], touch_updated=True)


def get_progress(search_id: str) -> Dict[str, Any] | None:
    """Return current progress for a search id."""
    record = _progress_store.get(search_id)
    if not record:
        return None
    return dict(_refresh_time_fields(record, touch_updated=False))


def complete_progress(search_id: str) -> None:
    """Mark a search as complete."""
    update_progress(
        search_id,
        percent=100.0,
        stage="done",
        phase="done",
        message="Selesai!",
        eta_seconds=0,
        done=True,
    )


def fail_progress(search_id: str, error_msg: str) -> None:
    """Mark a search as failed with a specific visible error."""
    update_progress(
        search_id,
        stage="error",
        phase="error",
        message=error_msg,
        error=error_msg,
        done=True,
        eta_seconds=None,
    )
