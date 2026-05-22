"""
progress.py - In-memory progress state for polling.
"""
from __future__ import annotations

import math
import os
import threading
import time
from typing import Any, Dict


_progress_store: Dict[str, Dict[str, Any]] = {}
_progress_lock = threading.RLock()

MAX_ETA_SECONDS = 3600
AI_PROGRESS_START = 70.0
AI_PROGRESS_SPAN = 18.0
AI_DEFAULT_BATCH_SECONDS = int(os.getenv("AI_DEFAULT_BATCH_SECONDS", "75"))
AI_MIN_BATCH_SECONDS = int(os.getenv("AI_MIN_BATCH_SECONDS", "30"))
AI_MAX_BATCH_SECONDS = int(os.getenv("AI_MAX_BATCH_SECONDS", "180"))


def _epoch_ms() -> int:
    return int(time.time() * 1000)


def _coerce_percent(value: Any) -> float:
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _coerce_eta_seconds(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(max(0, min(MAX_ETA_SECONDS, math.ceil(float(value)))))
    except (TypeError, ValueError, OverflowError):
        return None


def _coerce_epoch_ms(value: Any) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if parsed > 0 else None


def _bounded_batch_seconds(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = float(AI_DEFAULT_BATCH_SECONDS)
    return max(float(AI_MIN_BATCH_SECONDS), min(float(AI_MAX_BATCH_SECONDS), parsed))


def _average_batch_seconds(completed_ai_batch_durations: list[float] | tuple[float, ...] | None) -> float:
    durations: list[float] = []
    for item in completed_ai_batch_durations or []:
        try:
            parsed = float(item)
        except (TypeError, ValueError, OverflowError):
            continue
        if parsed > 0:
            durations.append(parsed)
    if not durations:
        return _bounded_batch_seconds(AI_DEFAULT_BATCH_SECONDS)
    return _bounded_batch_seconds(sum(durations) / len(durations))


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
    now_monotonic = time.perf_counter()
    started_monotonic = float(record.get("started_at_monotonic") or now_monotonic)
    elapsed = max(0.0, now_monotonic - started_monotonic)
    percent = _coerce_percent(record.get("progress_percent", record.get("percent", 0)))

    record["server_now_epoch_ms"] = now_epoch
    if touch_updated:
        record["updated_at_epoch_ms"] = now_epoch
    record["elapsed_seconds"] = round(elapsed, 1)
    record["progress_percent"] = percent
    record["percent"] = percent

    if record.get("done"):
        if record.get("stage") == "done":
            record["eta_seconds"] = 0
            record["estimated_completion_epoch_ms"] = now_epoch
            record["eta_is_reliable"] = True
        else:
            record["eta_seconds"] = None
            record["estimated_completion_epoch_ms"] = None
            record["eta_is_reliable"] = False
    elif record.get("estimated_completion_epoch_ms") is not None:
        deadline = _coerce_epoch_ms(record.get("estimated_completion_epoch_ms"))
        if deadline is None:
            record["eta_seconds"] = None
            record["estimated_completion_epoch_ms"] = None
        else:
            remaining = math.ceil((deadline - now_epoch) / 1000)
            record["eta_seconds"] = int(max(0, min(MAX_ETA_SECONDS, remaining)))
            record["estimated_completion_epoch_ms"] = deadline
    elif record.get("eta_seconds") is None and percent > 2:
        eta = elapsed / (percent / 100.0) - elapsed
        record["eta_seconds"] = _coerce_eta_seconds(eta)
        if record["eta_seconds"] is not None:
            record["estimated_completion_epoch_ms"] = now_epoch + int(record["eta_seconds"] * 1000)
        record["eta_is_reliable"] = False
    elif record.get("eta_seconds") is not None:
        eta_seconds = _coerce_eta_seconds(record.get("eta_seconds"))
        record["eta_seconds"] = eta_seconds
        record["estimated_completion_epoch_ms"] = (
            now_epoch + int(eta_seconds * 1000) if eta_seconds is not None else None
        )

    record["eta_label"] = _format_eta(record.get("eta_seconds"))
    record["phase"] = record.get("phase") or record.get("stage") or "initializing"
    return record


def init_progress(search_id: str, target: int, raw_target: int, engine_mode: str = "auto") -> None:
    """Initialize a progress record with all fields the frontend expects."""
    now_epoch = _epoch_ms()
    started_monotonic = time.perf_counter()
    with _progress_lock:
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
            "estimated_completion_epoch_ms": None,
            "eta_label": "ETA: calculating...",
            "eta_is_reliable": False,
            "ai_batch_current": None,
            "ai_batch_total": None,
            "ai_batch_started_at_epoch_ms": None,
            "ai_avg_batch_seconds": None,
            "ai_current_batch_elapsed_seconds": None,
            "ai_completed_batches": None,
            "ai_orchestrator": None,
            "engine": "none",
            "attempt": 1,
            "max_attempts": 1,
            "done": False,
            "error": None,
        }


def update_progress(search_id: str, **kwargs: Any) -> None:
    """Patch a progress record in place."""
    eta_explicit = "eta_seconds" in kwargs
    deadline_explicit = "estimated_completion_epoch_ms" in kwargs
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
    if eta_explicit:
        kwargs["eta_seconds"] = _coerce_eta_seconds(kwargs.get("eta_seconds"))
        if not deadline_explicit:
            eta_seconds = kwargs.get("eta_seconds")
            kwargs["estimated_completion_epoch_ms"] = (
                _epoch_ms() + int(eta_seconds * 1000) if eta_seconds is not None else None
            )
    if deadline_explicit:
        kwargs["estimated_completion_epoch_ms"] = _coerce_epoch_ms(kwargs.get("estimated_completion_epoch_ms"))

    with _progress_lock:
        if search_id not in _progress_store:
            return

        _progress_store[search_id].update(kwargs)
        if not eta_explicit and not deadline_explicit and not _progress_store[search_id].get("done"):
            _progress_store[search_id]["eta_seconds"] = None
            _progress_store[search_id]["estimated_completion_epoch_ms"] = None
            _progress_store[search_id]["eta_is_reliable"] = False
        _refresh_time_fields(_progress_store[search_id], touch_updated=True)


def get_progress(search_id: str) -> Dict[str, Any] | None:
    """Return current progress for a search id."""
    with _progress_lock:
        record = _progress_store.get(search_id)
        if not record:
            return None
        return dict(_refresh_time_fields(record, touch_updated=False))


def calculate_ai_eta_snapshot(
    batch_current: int,
    batch_total: int,
    batch_started_at_monotonic: float,
    completed_ai_batch_durations: list[float] | tuple[float, ...] | None = None,
    batch_done: bool = False,
) -> dict[str, Any]:
    """Build a live ETA/progress snapshot for the AI filter phase."""
    now_monotonic = time.perf_counter()
    now_epoch_ms = _epoch_ms()
    total = max(1, int(batch_total or 1))
    current = max(1, min(int(batch_current or 1), total))
    avg_batch_seconds = _average_batch_seconds(completed_ai_batch_durations)
    current_batch_elapsed = max(0.0, now_monotonic - float(batch_started_at_monotonic))

    if batch_done:
        completed_batches = current
        remaining_after_current = max(0, total - current)
        eta_seconds_float = remaining_after_current * avg_batch_seconds
        overall_ai_ratio = completed_batches / total
        current_batch_ratio = 1.0
    else:
        completed_batches = current - 1
        current_batch_ratio = min(current_batch_elapsed / avg_batch_seconds, 0.95)
        current_batch_remaining = max(avg_batch_seconds - current_batch_elapsed, 5.0)
        eta_seconds_float = current_batch_remaining + max(0, total - current) * avg_batch_seconds
        overall_ai_ratio = (completed_batches + current_batch_ratio) / total

    eta_seconds = _coerce_eta_seconds(eta_seconds_float)
    progress_percent = AI_PROGRESS_START + AI_PROGRESS_SPAN * max(0.0, min(1.0, overall_ai_ratio))

    return {
        "eta_seconds": eta_seconds,
        "estimated_completion_epoch_ms": (
            now_epoch_ms + int(eta_seconds * 1000) if eta_seconds is not None else None
        ),
        "progress_percent": round(progress_percent, 2),
        "percent": round(progress_percent, 2),
        "ai_batch_current": current,
        "ai_batch_total": total,
        "ai_avg_batch_seconds": round(avg_batch_seconds, 1),
        "ai_current_batch_elapsed_seconds": round(current_batch_elapsed, 1),
        "ai_completed_batches": completed_batches,
        "eta_is_reliable": True,
    }


def update_ai_eta_progress(
    search_id: str,
    batch_current: int,
    batch_total: int,
    batch_started_at_monotonic: float,
    batch_started_at_epoch_ms: int,
    completed_ai_batch_durations: list[float] | tuple[float, ...] | None = None,
    message: str | None = None,
    found: int | None = None,
    valid: int | None = None,
    batch_done: bool = False,
) -> dict[str, Any]:
    """Refresh progress while an Ollama classifier batch is running."""
    snapshot = calculate_ai_eta_snapshot(
        batch_current=batch_current,
        batch_total=batch_total,
        batch_started_at_monotonic=batch_started_at_monotonic,
        completed_ai_batch_durations=completed_ai_batch_durations,
        batch_done=batch_done,
    )
    payload: dict[str, Any] = {
        **snapshot,
        "stage": "ai_filtering",
        "phase": "ai_filtering",
        "message": message or f"AI filtering batch {batch_current}/{batch_total}",
        "ai_batch_started_at_epoch_ms": batch_started_at_epoch_ms,
    }
    if found is not None:
        payload["found"] = found
    if valid is not None:
        payload["valid"] = valid

    update_progress(search_id, **payload)
    return snapshot


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
