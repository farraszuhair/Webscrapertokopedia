"""
normalizer.py - Converts every scraper output into one product schema.

Old engines used mixed names like harga, price_val, price_text, link, and url.
Budget and AI filters now read one schema, while compatibility aliases remain
for the existing frontend and AI code.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable

from src.utils.currency import format_rupiah, parse_rupiah


def _first_text(data: dict[str, Any], keys: Iterable[str]) -> str:
    """Return the first non-empty string-ish field from a product dict."""
    for key in keys:
        value = data.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _first_value(data: dict[str, Any], keys: Iterable[str]) -> Any:
    """Return the first non-empty raw field without forcing it to text."""
    for key in keys:
        value = data.get(key)
        if value is not None and value != "":
            return value
    return None


def _clean_url(url: str) -> str:
    """Remove noisy query/hash fragments so dedupe works across engines."""
    if not url:
        return ""
    return re.split(r"[?#]", url.strip(), maxsplit=1)[0]


def _product_id(title: str, url: str, price_value: int | None) -> str:
    """Create a stable frontend id from fields that do not change per render."""
    raw = f"{title}|{url}|{price_value or ''}".encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()[:16]


def normalize_product(raw: dict[str, Any], source_engine: str | None = None) -> dict[str, Any] | None:
    """Normalize one raw product. Return None only when the card has no identity."""
    if not isinstance(raw, dict):
        return None

    title = _first_text(raw, ("title", "nama", "nama_produk", "name", "product_name"))
    url = _clean_url(_first_text(raw, ("url", "link", "href", "url_produk", "product_url")))
    if not title and not url:
        return None
    if not title:
        title = "Produk Tokopedia"

    price_raw = _first_value(
        raw,
        ("price_raw", "price_text", "harga_display", "price_display", "price", "harga"),
    )
    price_value = _first_value(raw, ("price_value", "price_val", "harga_value", "harga"))

    parsed_price = parse_rupiah(price_value)
    if parsed_price is None:
        parsed_price = parse_rupiah(price_raw)

    price_text = str(price_raw).strip() if price_raw not in (None, "") else ""
    if not price_text and parsed_price is not None:
        price_text = format_rupiah(parsed_price)

    engine = source_engine or _first_text(raw, ("source_engine", "source", "engine")) or "unknown"

    normalized = {
        "id": raw.get("id") or _product_id(title, url, parsed_price),
        "title": title,
        "price_raw": price_text,
        "price_value": parsed_price,
        "shop": _first_text(raw, ("shop", "toko", "nama_toko", "store")),
        "location": _first_text(raw, ("location", "lokasi")),
        "rating": _first_text(raw, ("rating", "rating_toko", "rating_text")),
        "sold": _first_text(raw, ("sold", "terjual", "sold_text")),
        "url": url,
        "image": _first_text(raw, ("image", "image_url", "url_gambar", "thumbnail")),
        "source_engine": engine,
    }

    # Compatibility aliases for old frontend/AI code. Old logic trash. Replaced.
    normalized["link"] = normalized["url"]
    normalized["price_text"] = normalized["price_raw"]
    normalized["price_val"] = normalized["price_value"]
    normalized["source"] = normalized["source_engine"]
    return normalized


def normalize_products(products: Iterable[dict[str, Any]], source_engine: str | None = None) -> list[dict[str, Any]]:
    """Normalize a batch and drop only completely broken product records."""
    normalized: list[dict[str, Any]] = []
    for item in products or []:
        product = normalize_product(item, source_engine)
        if product:
            normalized.append(product)
    return normalized
