"""
schemas.py - API request and response models.

FeedbackRequest updated to support multi-category correction and ai_decision.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


EngineMode = Literal["auto", "puppeteer", "rollback", "compare"]
REQUESTED_COUNT_DEFAULT = max(1, int(os.getenv("REQUESTED_COUNT_DEFAULT", "25")))


class SearchRequest(BaseModel):
    """Accept both old frontend keys and new API keys."""
    model_config = ConfigDict(populate_by_name=True)

    query: str
    target_count: int = Field(default=REQUESTED_COUNT_DEFAULT, validation_alias=AliasChoices("target_count", "target"))
    budget: Optional[Any] = None
    tolerance: float = 20.0
    use_ai: bool = Field(default=True, validation_alias=AliasChoices("use_ai", "ai"))
    engine_mode: EngineMode = "auto"


class FeedbackRequest(BaseModel):
    search_id: str
    product_id: str
    product_title: str
    user_action: str
    selected_reasons: List[str]
    custom_reason: str
    corrected_label: str
    ai_label: str
    ai_confidence: float
    query: str
    timestamp: str


class ProgressResponse(BaseModel):
    search_id: str
    engine_mode: str = "auto"
    active_engine: str = "none"
    percent: float
    progress_percent: float = 0.0
    stage: str
    phase: str = "initializing"
    message: str
    found: int
    valid: int
    target: int
    raw_target: int
    started_at_epoch_ms: int = 0
    started_at_monotonic: float = 0.0
    updated_at_epoch_ms: int = 0
    server_now_epoch_ms: int = 0
    elapsed_seconds: float
    eta_seconds: Optional[int] = None
    eta_label: str = "Calculating..."
    engine: str = "none"
    attempt: int = 1
    max_attempts: int = 1
    done: bool
    error: Optional[str] = None
