"""
progress.py - In-memory progress state for polling.
"""
from __future__ import annotations

from typing import Any, Dict


_progress_store: Dict[str, Dict[str, Any]] = {}


def init_progress(search_id: str, target: int, raw_target: int, engine_mode: str = "auto") -> None:
    """Initialize a progress record with all fields the frontend expects."""
    _progress_store[search_id] = {
        "search_id": search_id,
        "engine_mode": engine_mode,
        "active_engine": "none",
        "percent": 0,
        "stage": "initializing",
        "message": "Initializing...",
        "found": 0,
        "valid": 0,
        "target": target,
        "raw_target": raw_target,
        "elapsed_seconds": 0,
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

    if "active_engine" in kwargs and "engine" not in kwargs:
        kwargs["engine"] = kwargs["active_engine"]
    if "eta_seconds" in kwargs and kwargs["eta_seconds"] is not None:
        kwargs["eta_label"] = f"{kwargs['eta_seconds']}s"

    _progress_store[search_id].update(kwargs)


def get_progress(search_id: str) -> Dict[str, Any] | None:
    """Return current progress for a search id."""
    return _progress_store.get(search_id)


def complete_progress(search_id: str) -> None:
    """Mark a search as complete."""
    update_progress(
        search_id,
        percent=100,
        stage="done",
        message="Selesai!",
        eta_seconds=0,
        eta_label="0s",
        done=True,
    )


def fail_progress(search_id: str, error_msg: str) -> None:
    """Mark a search as failed with a specific visible error."""
    update_progress(
        search_id,
        stage="error",
        message=error_msg,
        error=error_msg,
        done=True,
    )
