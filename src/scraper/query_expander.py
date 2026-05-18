"""
query_expander.py - Search variants for broad Tokopedia queries.

Tokopedia's first page for "laptop gaming" often mixes accessories. Query
variants force both engines to visit real gaming-laptop intent pages.
"""
from __future__ import annotations

from typing import Any

from src.utils.currency import calculate_budget_range, parse_rupiah


LAPTOP_GAMING_VARIANTS = [
    "laptop gaming",
    "notebook gaming",
    "asus rog laptop",
    "asus tuf gaming laptop",
    "lenovo legion laptop",
    "lenovo loq laptop",
    "acer nitro laptop",
    "hp victus laptop",
    "msi gaming laptop",
    "acer predator laptop",
    "laptop rtx 3050",
    "laptop rtx 4050",
]


def expand_query_variants(query: str) -> list[str]:
    """Return deduped query variants. Broad laptop gaming gets brand/GPU pages."""
    clean_query = " ".join((query or "").lower().split())
    variants: list[str] = []

    if "laptop" in clean_query and "gaming" in clean_query:
        variants.extend(LAPTOP_GAMING_VARIANTS)
    else:
        variants.append(query.strip())

    # Keep the user's exact query first when it differs by casing/spacing.
    if query and query.strip().lower() not in {variant.lower() for variant in variants}:
        variants.insert(0, query.strip())

    seen: set[str] = set()
    deduped: list[str] = []
    for variant in variants:
        key = variant.lower()
        if not variant or key in seen:
            continue
        seen.add(key)
        deduped.append(variant)
    return deduped


def budget_url_range(budget: Any, tolerance: Any) -> tuple[int | None, int | None]:
    """Calculate pmin/pmax URL params from the same budget rules as backend."""
    budget_value = parse_rupiah(budget)
    if budget_value is None or budget_value <= 0:
        return None, None
    min_price, max_price = calculate_budget_range(budget_value, tolerance)
    return min_price, max_price
