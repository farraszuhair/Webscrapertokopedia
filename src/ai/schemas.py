"""
Small shared schemas for AI product filtering.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProductDecision:
    accepted: bool
    confidence: float
    reason: str
    category_match: str
    source: str = "rule"
    product_category: str = "unknown"
    rule_score: float = 0.0
    ai_confidence: float = 0.0
    fallback_used: bool = False
    raw: dict[str, Any] = field(default_factory=dict)
