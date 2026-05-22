"""
normalizer.py - Convert scraper output into one product schema.

Raw extraction should be counted before normalization. This module keeps weak
but usable raw products and reports every drop reason for diagnostics.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Iterable

from src.utils.currency import format_rupiah, parse_rupiah
from src.utils.debug import save_json_debug


@dataclass
class NormalizerReport:
    engine: str
    input_count: int
    output: list[dict[str, Any]] = field(default_factory=list)
    drop_reasons: dict[str, int] = field(default_factory=dict)
    dropped_samples: list[dict[str, Any]] = field(default_factory=list)
    images_extracted_count: int = 0
    images_missing_count: int = 0
    debug_path: str | None = None

    @property
    def output_count(self) -> int:
        return len(self.output)

    @property
    def dropped_count(self) -> int:
        return self.input_count - len(self.output)

    def debug_payload(self) -> dict[str, Any]:
        """Return compact JSON diagnostic for normalizer behavior."""
        return {
            "engine": self.engine,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "dropped_count": self.dropped_count,
            "drop_reasons": self.drop_reasons,
            "images_extracted_count": self.images_extracted_count,
            "images_missing_count": self.images_missing_count,
            "dropped_samples": self.dropped_samples[:30],
        }


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


def normalize_image(raw: dict[str, Any]) -> str | None:
    """Return the first valid http(s) image URL from common scraper fields."""
    candidates = [
        raw.get("image"),
        raw.get("image_url"),
        raw.get("thumbnail"),
        raw.get("img"),
        raw.get("picture"),
        raw.get("url_gambar"),
    ]
    for url in candidates:
        if not isinstance(url, str):
            continue
        cleaned = url.strip().strip('"').strip("'")
        lowered = cleaned.lower()
        if (
            (cleaned.startswith("http://") or cleaned.startswith("https://"))
            and not cleaned.startswith("data:image")
            and "base64" not in lowered
            and "svg" not in lowered
            and lowered.replace(" ", "") not in {"undefined", "null", "noimage"}
        ):
            return cleaned
    return None


def _product_id(title: str, url: str, price_value: int | None) -> str:
    """Create a stable frontend id from fields that do not change per render."""
    raw = f"{title}|{url}|{price_value or ''}".encode("utf-8", errors="ignore")
    return hashlib.sha1(raw).hexdigest()[:16]


def _normalize_product_with_reason(raw: dict[str, Any], source_engine: str | None = None) -> tuple[dict[str, Any] | None, str | None]:
    """Normalize one product and return a drop reason when unusable."""
    if not isinstance(raw, dict):
        return None, "not_dict"

    title = _first_text(raw, ("title", "nama", "nama_produk", "name", "product_name"))
    if not title:
        return None, "missing_title"

    url = _clean_url(_first_text(raw, ("url", "link", "href", "url_produk", "product_url")))
    price_raw = _first_value(
        raw,
        ("price_raw", "price_text", "harga_display", "price_display", "price", "harga"),
    )
    if not url and price_raw in (None, ""):
        return None, "missing_url_and_price"

    price_value = _first_value(raw, ("price_value", "price_val", "harga_value", "harga"))
    parsed_price = parse_rupiah(price_value)
    if parsed_price is None:
        parsed_price = parse_rupiah(price_raw)

    price_text = str(price_raw).strip() if price_raw not in (None, "") else ""
    if not price_text and parsed_price is not None:
        price_text = format_rupiah(parsed_price)

    engine = source_engine or _first_text(raw, ("source_engine", "source", "engine")) or "unknown"
    
    # Parse rating to float if possible
    rating_text = _first_text(raw, ("rating", "rating_toko", "rating_text"))
    rating_val = None
    try:
        rating_val = float(rating_text.replace(',', '.'))
    except ValueError:
        pass

    # Parse sold count to int if possible
    sold_text = _first_text(raw, ("sold", "terjual", "sold_text"))
    sold_count = None
    sold_lower = sold_text.lower()
    match = re.search(r'(\d+(?:[.,]\d+)?)\s*(rb|ribu|k|jt|juta)?', sold_lower)
    if match:
        num_str = match.group(1).replace(',', '.')
        try:
            num = float(num_str)
            unit = match.group(2)
            if unit in ('rb', 'ribu', 'k'):
                num *= 1000
            elif unit in ('jt', 'juta'):
                num *= 1000000
            sold_count = int(num)
        except ValueError:
            pass

    image_url = normalize_image(raw)

    normalized = {
        "id": raw.get("id") or _product_id(title, url, parsed_price),
        "title": title,
        "price": parsed_price or 0,
        "price_text": price_text,
        "price_raw": price_text, # backward compat
        "price_value": parsed_price, # backward compat
        "shop_name": _first_text(raw, ("shop", "toko", "nama_toko", "store", "shop_name")),
        "shop": _first_text(raw, ("shop", "toko", "nama_toko", "store", "shop_name")), # backward compat
        "store": _first_text(raw, ("shop", "toko", "nama_toko", "store", "shop_name")),
        "shop_location": _first_text(raw, ("location", "lokasi", "shop_location")),
        "location": _first_text(raw, ("location", "lokasi", "shop_location")), # backward compat
        "rating": rating_val if rating_val is not None else rating_text,
        "rating_text": rating_text,
        "sold_count": sold_count,
        "sold_text": sold_text,
        "sold": sold_text, # backward compat
        "product_url": url,
        "url": url, # backward compat
        "image_url": image_url,
        "image": image_url, # backward compat
        "source_engine": engine,
        "source_query": _first_text(raw, ("source_query", "query_variant")),
        "category_decision": raw.get("category_decision", ""),
        "category_reason": raw.get("category_reason", ""),
        "budget_decision": raw.get("budget_decision", ""),
        "ai_decision": raw.get("ai_decision", None),
        "ai_reason": raw.get("ai_reason", ""),
        "confidence": raw.get("confidence", 0) or 0,
        "decision_source": raw.get("decision_source", ""),
    }

    # Compatibility aliases for old frontend/AI code. Old logic bad. Replaced.
    normalized["link"] = normalized["url"]
    normalized["price_text"] = normalized["price_raw"]
    normalized["price_val"] = normalized["price_value"]
    normalized["source"] = normalized["source_engine"]
    return normalized, None


def normalize_product(raw: dict[str, Any], source_engine: str | None = None) -> dict[str, Any] | None:
    """Normalize one raw product. Missing shop/location/image is allowed."""
    product, _ = _normalize_product_with_reason(raw, source_engine)
    return product


def normalize_products_with_report(
    products: Iterable[dict[str, Any]],
    source_engine: str | None = None,
    search_id: str | None = None,
) -> NormalizerReport:
    """Normalize a batch and optionally write normalizer_debug_<engine>.json."""
    raw_products = list(products or [])
    engine = source_engine or "unknown"
    output: list[dict[str, Any]] = []
    drop_reasons: Counter[str] = Counter()
    dropped_samples: list[dict[str, Any]] = []

    for item in raw_products:
        product, reason = _normalize_product_with_reason(item, source_engine)
        if product:
            output.append(product)
            continue
        drop_reasons[reason or "unknown"] += 1
        dropped_samples.append({
            "reason": reason or "unknown",
            "raw": item if isinstance(item, dict) else str(item),
        })

    report = NormalizerReport(
        engine=engine,
        input_count=len(raw_products),
        output=output,
        drop_reasons=dict(drop_reasons),
        dropped_samples=dropped_samples,
        images_extracted_count=sum(1 for product in output if product.get("image")),
        images_missing_count=sum(1 for product in output if not product.get("image")),
    )

    if search_id:
        report.debug_path = save_json_debug(search_id, f"normalizer_debug_{engine}.json", report.debug_payload())
    return report


def normalize_products(products: Iterable[dict[str, Any]], source_engine: str | None = None) -> list[dict[str, Any]]:
    """Backward-compatible normalizer returning only product list."""
    return normalize_products_with_report(products, source_engine).output
