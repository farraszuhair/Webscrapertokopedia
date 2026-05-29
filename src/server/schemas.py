"""
schemas.py - API request and response models.

FeedbackRequest updated to support multi-category correction and ai_decision.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator
from src.config import TARGET_COUNT_DEFAULT, TARGET_FIRST_MODE


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
    target_first_mode: bool = Field(
        default=TARGET_FIRST_MODE,
        validation_alias=AliasChoices("target_first_mode", "target_first"),
    )


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="allow", protected_namespaces=())

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
    semantic_score: float = 0.0
    combined_score: float = 0.0
    learned_adjustment: float = 0.0
    confidence: float = 0.0
    learning_scope_hint: Optional[str] = None
    model_used: Optional[str] = None
    ai_reason: Optional[str] = None
    sort_mode: str = "terbaik"

    @field_validator("selected_reasons", "reasons", mode="before")
    @classmethod
    def _coerce_reason_list(cls, value: Any) -> List[str]:
        if value in (None, ""):
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if item not in (None, "")]
        return [str(value)]

    def normalized_product(self) -> Dict[str, Any]:
        product = dict(self.product or {})
        if self.product_id and not product.get("id"):
            product["id"] = self.product_id
        if self.product_title and not product.get("title"):
            product["title"] = self.product_title
        return product

    def normalized_product_id(self) -> str:
        product = self.normalized_product()
        return str(self.product_id or product.get("id") or product.get("url") or "unknown")

    def normalized_product_title(self) -> str:
        product = self.normalized_product()
        return str(self.product_title or product.get("title") or "")

    def normalized_reasons(self) -> List[str]:
        return list(self.reasons or self.selected_reasons or [])

    def normalized_note(self) -> str:
        return str(self.note or self.custom_reason or "")

    def normalized_feedback_type(self) -> str:
        value = str(self.feedback_type or "").strip().lower()
        if value in {"positive", "negative"}:
            return value
        action = str(self.user_action or "").strip().lower()
        return "positive" if action == "benar" else "negative"

    def normalized_user_action(self) -> str:
        action = str(self.user_action or "").strip().lower()
        if action in {"benar", "salah"}:
            return action
        return "benar" if self.normalized_feedback_type() == "positive" else "salah"

    def normalized_corrected_label(self) -> str:
        label = str(self.corrected_label or "").strip()
        if label:
            return label
        return "relevan" if self.normalized_feedback_type() == "positive" else "tidak_relevan"


class ProgressResponse(BaseModel):
    search_id: str
    engine_mode: str = "auto"
    active_engine: str = "none"
    percent: float
    progress_percent: float = 0.0
    stage: str
    phase: str = "initializing"
    message: str
    status_text: str = ""
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
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    searchId: str = ""
    statusText: str = ""
    percentage: float = 0.0
    elapsedSeconds: float = 0.0
    etaSeconds: Optional[int] = None
    foundCount: int = 0
    targetCount: int = 0
