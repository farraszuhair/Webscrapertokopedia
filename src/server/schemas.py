"""
schemas.py - Pydantic models for the FastAPI server.
Defines input and output structures.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    query: str
    target_count: int = 25
    budget: Optional[int] = None
    tolerance: Optional[float] = 20.0
    use_ai: bool = True

class FeedbackRequest(BaseModel):
    query: str
    product: Dict[str, Any]
    feedback: str
    reason: Optional[str] = ""

class ProgressResponse(BaseModel):
    search_id: str
    percent: int
    stage: str
    message: str
    found: int
    valid: int
    target: int
    raw_target: int
    elapsed_seconds: int
    eta_seconds: Optional[int] = None
    engine: str = "unknown"
    attempt: int = 1
    max_attempts: int = 3
    done: bool
    error: Optional[str] = None
