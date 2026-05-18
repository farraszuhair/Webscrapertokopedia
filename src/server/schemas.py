"""
schemas.py - API request and response models.

FeedbackRequest updated to support multi-category correction and ai_decision.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


EngineMode = Literal["auto", "puppeteer", "rollback", "compare"]


class SearchRequest(BaseModel):
    """Accept both old frontend keys and new API keys."""
    model_config = ConfigDict(populate_by_name=True)

    query: str
    target_count: int = Field(default=25, validation_alias=AliasChoices("target_count", "target"))
    budget: Optional[Any] = None
    tolerance: float = 20.0
    use_ai: bool = Field(default=True, validation_alias=AliasChoices("use_ai", "ai"))
    engine_mode: EngineMode = "auto"


class FeedbackRequest(BaseModel):
    """
    Multi-category feedback request.
    Supports Benar/Salah/Relevan/Tidak Relevan/Ajarkan AI flows.
    """
    query: str
    product: Dict[str, Any]
    ai_decision: Optional[Dict[str, Any]] = None   # what Qwen said originally
    correction: str                                  # "should_include", "should_exclude", "benar", etc.
    categories: Optional[List[str]] = None           # multi-select category tags
    note: Optional[str] = ""                         # user note from popup
    search_id: Optional[str] = None                  # for debug artifact


class ProgressResponse(BaseModel):
    search_id: str
    engine_mode: str = "auto"
    active_engine: str = "none"
    percent: int
    stage: str
    message: str
    found: int
    valid: int
    target: int
    raw_target: int
    elapsed_seconds: int
    eta_seconds: Optional[int] = None
    eta_label: str = "Calculating..."
    engine: str = "none"
    attempt: int = 1
    max_attempts: int = 1
    done: bool
    error: Optional[str] = None
