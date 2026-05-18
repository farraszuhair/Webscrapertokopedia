"""
dedupe.py - Product deduplication shared by normal and compare modes.
"""
from __future__ import annotations

import re
from typing import Any


def _clean_url(url: str) -> str:
    """Remove tracking params so two engines agree on the same product URL."""
    return re.split(r"[?#]", (url or "").strip(), maxsplit=1)[0].lower()


def deduplicate_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate by URL first, then title+price for cards without URL."""
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []

    for product in products or []:
        url = _clean_url(product.get("url") or product.get("link") or "")
        fallback = f"{product.get('title', '').lower()}|{product.get('price_value') or product.get('price_raw')}"
        key = url or fallback
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(product)

    return deduped
