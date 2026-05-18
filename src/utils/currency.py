"""
currency.py - Shared Rupiah parsing and formatting.

The scraper receives prices from the browser as messy UI text. Keep all price
parsing here so the backend, filters, and tests use one truth.
"""
from __future__ import annotations

import math
import re
import unicodedata
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


INVALID_PRICE_WORDS = (
    "hubungi penjual",
    "hubungi",
    "nego",
    "tanya",
    "gratis",
    "free",
)


def _normalize_text(value: Any) -> str:
    """Normalize browser text, hidden spaces, and mixed case before parsing."""
    if value is None or isinstance(value, bool):
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def _decimal_from_text(number_text: str) -> Decimal | None:
    """Parse decimal text used with units like jt/juta/rb."""
    cleaned = number_text.strip().replace(",", ".")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def parse_rupiah(value: Any) -> int | None:
    """
    Convert Indonesian Rupiah text into an integer.

    Examples:
    - "Rp10.000.000" -> 10000000
    - "Rp10,5 juta" -> 10500000
    - "Rp999 rb" -> 999000
    - "" / None / "Hubungi Penjual" -> None
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value if value >= 0 else None

    if isinstance(value, float):
        if not math.isfinite(value) or value < 0:
            return None
        return int(round(value))

    text = _normalize_text(value)
    if not text or any(word in text for word in INVALID_PRICE_WORDS):
        return None

    # Unit prices need decimal support: "10,5 juta", "10.5 jt", "999 rb".
    unit_match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(juta|jt|mio|million|rb|ribu|k)\b",
        text,
        flags=re.IGNORECASE,
    )
    if unit_match:
        number = _decimal_from_text(unit_match.group(1))
        if number is None:
            return None
        unit = unit_match.group(2).lower()
        multiplier = 1_000_000 if unit in {"juta", "jt", "mio", "million"} else 1_000
        parsed = (number * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(parsed)

    # Plain prices on Tokopedia are integer money. Drop Rp, dots, commas, spaces.
    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return None

    try:
        return int(digits)
    except ValueError:
        return None


def format_rupiah(value: Any) -> str:
    """Format an integer as compact Indonesian Rupiah text: 10000000 -> Rp10.000.000."""
    parsed = parse_rupiah(value)
    if parsed is None:
        return "Rp0"
    return "Rp" + f"{parsed:,}".replace(",", ".")


def calculate_budget_range(budget: Any, tolerance: Any = 20) -> tuple[int, int]:
    """
    Calculate inclusive min/max range for a budget and percentage tolerance.

    Empty/invalid budget returns (0, 0). Callers use parse_rupiah(budget) is None
    to decide that the budget filter is disabled.
    """
    budget_value = parse_rupiah(budget)
    if budget_value is None or budget_value <= 0:
        return 0, 0

    try:
        tolerance_value = float(tolerance)
    except (TypeError, ValueError):
        tolerance_value = 20.0

    tolerance_value = max(0.0, min(tolerance_value, 100.0))
    fraction = tolerance_value / 100.0
    return int(budget_value * (1.0 - fraction)), int(budget_value * (1.0 + fraction))
