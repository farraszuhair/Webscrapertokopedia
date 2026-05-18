"""
progress.py - Global state manager for tracking scraping progress.
Allows real-time polling from the frontend.
"""
from typing import Dict, Any

# Global dictionary to store progress states by search_id
_progress_store: Dict[str, Dict[str, Any]] = {}

def init_progress(search_id: str, target: int, raw_target: int):
    """Initializes a new progress tracking entry."""
    _progress_store[search_id] = {
        "search_id": search_id,
        "percent": 0,
        "stage": "queued",
        "message": "Menunggu giliran...",
        "found": 0,
        "valid": 0,
        "target": target,
        "raw_target": raw_target,
        "elapsed_seconds": 0,
        "eta_seconds": None,
        "engine": "unknown",
        "attempt": 1,
        "max_attempts": 3,
        "done": False,
        "error": None
    }

def update_progress(search_id: str, **kwargs):
    """Updates specific fields in a progress entry."""
    if search_id in _progress_store:
        _progress_store[search_id].update(kwargs)

def get_progress(search_id: str) -> Dict[str, Any]:
    """Retrieves current progress entry."""
    return _progress_store.get(search_id)

def complete_progress(search_id: str):
    """Marks progress as done."""
    update_progress(search_id, percent=100, stage="done", message="Selesai!", done=True)

def fail_progress(search_id: str, error_msg: str):
    """Marks progress as failed with error."""
    update_progress(search_id, stage="failed", message=error_msg, error=error_msg, done=True)
