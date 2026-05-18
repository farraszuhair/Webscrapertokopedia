"""
budget_filter.py - Budget filtering with explicit reject reasons.

This module never treats empty budget as zero. It also separates invalid price
from budget rejection so failures are debuggable.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from src.scraper.normalizer import normalize_products
from src.utils.currency import calculate_budget_range, format_rupiah, parse_rupiah


@dataclass
class FilterResult:
    budget_input: Any
    budget_value: int | None
    tolerance: float
    min_price: int | None
    max_price: int | None
    total_products: int
    kept: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)
    reasons: dict[str, int] = field(default_factory=dict)
    samples: list[dict[str, Any]] = field(default_factory=list)
    debug_path: str | None = None

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)

    def debug_payload(self) -> dict[str, Any]:
        """Return JSON-serializable payload for data/debug/<search_id>."""
        return {
            "budget_input": "" if self.budget_input is None else str(self.budget_input),
            "budget_value": self.budget_value,
            "tolerance": self.tolerance,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "total_products": self.total_products,
            "kept": len(self.kept),
            "rejected": len(self.rejected),
            "reasons": self.reasons,
            "samples": self.samples,
        }

    def failure_message(self) -> str:
        """Build a specific user-facing message when zero products pass budget."""
        below = self.reasons.get("below_budget_range", 0)
        above = self.reasons.get("above_budget_range", 0)
        invalid = self.reasons.get("invalid_price", 0)
        message = (
            f"Produk ditemukan {self.total_products}, tapi {above} di atas budget, "
            f"{below} di bawah budget, {invalid} harga tidak valid. "
            "Coba naikkan budget/tolerance."
        )
        if self.debug_path:
            message += f" Debug: {self.debug_path}"
        return message


def _safe_tolerance(tolerance: Any) -> float:
    """Clamp frontend tolerance into a sane percentage."""
    try:
        return max(0.0, min(float(tolerance), 100.0))
    except (TypeError, ValueError):
        return 20.0


def _decision_sample(
    product: dict[str, Any],
    decision: str,
    reason: str | None,
    min_price: int | None,
    max_price: int | None,
) -> dict[str, Any]:
    """Keep each decision compact but useful for JSON debug files."""
    return {
        "title": product.get("title", ""),
        "url": product.get("url", ""),
        "price_raw": product.get("price_raw"),
        "price_value": product.get("price_value"),
        "min_price": min_price,
        "max_price": max_price,
        "decision": decision,
        "reason": reason,
    }


def filter_by_budget(products: list[dict[str, Any]], budget: Any, tolerance: Any = 20) -> FilterResult:
    """
    Filter products by inclusive budget range.

    Rules:
    - Empty/invalid budget disables budget filtering.
    - Invalid product price is rejected as invalid_price only when budget is active.
    - Every rejected product gets price_raw, price_value, min_price, max_price,
      and reject_reason.
    """
    normalized = normalize_products(products)
    budget_value = parse_rupiah(budget)
    if budget_value is not None and budget_value <= 0:
        budget_value = None

    tolerance_value = _safe_tolerance(tolerance)

    if budget_value is None:
        return FilterResult(
            budget_input=budget,
            budget_value=None,
            tolerance=tolerance_value,
            min_price=None,
            max_price=None,
            total_products=len(normalized),
            kept=normalized,
            rejected=[],
            reasons={},
            samples=[
                _decision_sample(product, "kept", "budget_disabled", None, None)
                for product in normalized
            ],
        )

    min_price, max_price = calculate_budget_range(budget_value, tolerance_value)
    reasons: Counter[str] = Counter()
    kept: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []

    for product in normalized:
        price_value = parse_rupiah(product.get("price_value"))
        if price_value is None:
            price_value = parse_rupiah(product.get("price_raw"))

        product["price_value"] = price_value
        product["price_val"] = price_value
        if not product.get("price_raw") and price_value is not None:
            product["price_raw"] = format_rupiah(price_value)
            product["price_text"] = product["price_raw"]

        if price_value is None or price_value <= 0:
            reason = "invalid_price"
        elif price_value < min_price:
            reason = "below_budget_range"
        elif price_value > max_price:
            reason = "above_budget_range"
        else:
            reason = None

        if reason is None:
            kept.append(product)
            samples.append(_decision_sample(product, "kept", "within_budget_range", min_price, max_price))
            continue

        reasons[reason] += 1
        rejected_product = dict(product)
        rejected_product["price_raw"] = product.get("price_raw")
        rejected_product["price_value"] = price_value
        rejected_product["price_val"] = price_value
        rejected_product["min_price"] = min_price
        rejected_product["max_price"] = max_price
        rejected_product["reject_reason"] = reason
        rejected.append(rejected_product)
        samples.append(_decision_sample(rejected_product, "rejected", reason, min_price, max_price))

    return FilterResult(
        budget_input=budget,
        budget_value=budget_value,
        tolerance=tolerance_value,
        min_price=min_price,
        max_price=max_price,
        total_products=len(normalized),
        kept=kept,
        rejected=rejected,
        reasons=dict(reasons),
        samples=samples,
    )
