"""
schemas.py - API request and response models.

FeedbackRequest updated to support multi-category correction and ai_decision.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from src.config import TARGET_COUNT_DEFAULT


EngineMode = Literal["auto", "puppeteer", "rollback", "selenium", "compare", "compare_both"]
SortMode = Literal["terbaik", "termurah", "most_trusted"]
REQUESTED_COUNT_DEFAULT = max(1, int(TARGET_COUNT_DEFAULT))


class SearchRequest(BaseModel):
    """Accept both old frontend keys and new API keys."""
    model_config = ConfigDict(populate_by_name=True)

    query: str
    target_count: int = Field(default=REQUESTED_COUNT_DEFAULT, validation_alias=AliasChoices("target_count", "target"))
    budget: Optional[Any] = None
    tolerance: float = 20.0
    use_ai: bool = Field(default=True, validation_alias=AliasChoices("use_ai", "ai"))
    engine_mode: EngineMode = "auto"
    sort_mode: SortMode = "terbaik"


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_id: str = "unknown"
    product_id: str = ""
    product_title: str = ""
    user_action: str = ""
    selected_reasons: List[str] = Field(default_factory=list)
    custom_reason: str = ""
    corrected_label: str = ""
    ai_label: str = ""
    ai_confidence: float = 0.0
    query: str
    timestamp: str = ""
    query_intent: Optional[str] = None
    product: Optional[Dict[str, Any]] = None
    feedback_type: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    note: str = ""
    rule_score: float = 0.0
    sort_mode: str = "terbaik"


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
    estimated_completion_epoch_ms: Optional[int] = None
    eta_label: str = "Calculating..."
    eta_is_reliable: bool = False
    ai_batch_current: Optional[int] = None
    ai_batch_total: Optional[int] = None
    ai_batch_started_at_epoch_ms: Optional[int] = None
    ai_avg_batch_seconds: Optional[float] = None
    ai_current_batch_elapsed_seconds: Optional[float] = None
    ai_completed_batches: Optional[int] = None
    ai_orchestrator: Optional[Dict[str, Any]] = None
    engine: str = "none"
    attempt: int = 1
    max_attempts: int = 1
    done: bool
    error: Optional[str] = None
