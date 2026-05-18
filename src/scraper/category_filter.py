"""
category_filter.py - Reject accessories before budget filtering.

Budget filter should only see real laptop candidates. Otherwise cheap mouse,
charger, RAM, and cooler listings get counted as "below budget", which is
technically true but useless.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


ACCESSORY_KEYWORDS = [
    "mouse",
    "mice",
    "keyboard protector",
    "keyboard",
    "charger",
    "adaptor",
    "adapter",
    "power adapter",
    "cooling pad",
    "cooler",
    "kipas",
    "pendingin",
    "speaker",
    "headset",
    "earphone",
    "headphone",
    "ram",
    "sodimm",
    "ssd",
    "mousepad",
    "mouse pad",
    "kabel",
    "cable",
    "webcam",
    "tas",
    "sleeve",
    "stand",
    "skin",
    "case",
    "protector",
]

GAMING_LAPTOP_KEYWORDS = [
    "laptop",
    "notebook",
    "rog",
    "tuf gaming",
    "legion",
    "loq",
    "nitro",
    "predator",
    "victus",
    "msi",
    "katana",
    "thin",
    "cyborg",
    "omen",
    "alienware",
    "rtx",
    "gtx",
    "geforce",
    "ryzen",
    "intel",
    "core i5",
    "core i7",
    "core i9",
]

SERIES_KEYWORDS = [
    "rog",
    "tuf gaming",
    "legion",
    "loq",
    "nitro",
    "predator",
    "victus",
    "katana",
    "cyborg",
    "omen",
    "alienware",
]

GPU_KEYWORDS = ["rtx", "gtx", "geforce"]
CPU_KEYWORDS = ["ryzen", "intel", "core i5", "core i7", "core i9"]
SPEC_ACCESSORIES = {"ram", "ssd"}

# These are strong enough to override generic words like "case" inside a model
# title only when the listing also looks like an actual laptop.
STRONG_LAPTOP_SIGNALS = SERIES_KEYWORDS + GPU_KEYWORDS + ["gaming laptop", "laptop gaming"]


@dataclass
class CategoryFilterResult:
    query: str
    total_products: int
    candidates: list[dict[str, Any]] = field(default_factory=list)
    rejected_accessories: list[dict[str, Any]] = field(default_factory=list)
    reasons: dict[str, int] = field(default_factory=dict)
    samples_rejected: list[dict[str, Any]] = field(default_factory=list)
    samples_kept: list[dict[str, Any]] = field(default_factory=list)
    debug_path: str | None = None

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)

    @property
    def rejected_accessory_count(self) -> int:
        return len(self.rejected_accessories)

    def debug_payload(self) -> dict[str, Any]:
        """Return compact JSON for category debug artifacts."""
        return {
            "query": self.query,
            "total_products": self.total_products,
            "candidates": len(self.candidates),
            "rejected_accessories": len(self.rejected_accessories),
            "reasons": self.reasons,
            "samples_rejected": self.samples_rejected[:30],
            "samples_kept": self.samples_kept[:30],
        }


def _normalize_text(value: Any) -> str:
    """Lowercase and space-normalize title/URL before keyword matching."""
    text = str(value or "").lower()
    text = re.sub(r"[_\-/+.,:;()\[\]{}|]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    """Match phrases on token boundaries so 'ram' does not hit random words."""
    phrase = _normalize_text(phrase)
    if not phrase:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) is not None


def _matches_any(text: str, keywords: list[str]) -> list[str]:
    """Return every keyword present in normalized text."""
    return [keyword for keyword in keywords if _contains_phrase(text, keyword)]


def classify_product_category(product: dict[str, Any], query: str) -> dict[str, Any]:
    """
    Add category_decision, category_reason, and category_score to one product.

    Rules:
    - "for laptop" accessories die.
    - Known gaming laptop series/GPU laptop titles live.
    - Generic accessories live only if they are clearly actual laptop products.
    """
    title = _normalize_text(product.get("title"))
    url = _normalize_text(product.get("url"))
    haystack = f"{title} {url}"

    accessory_hits = _matches_any(haystack, ACCESSORY_KEYWORDS)
    series_hits = _matches_any(haystack, SERIES_KEYWORDS)
    gpu_hits = _matches_any(haystack, GPU_KEYWORDS)
    cpu_hits = _matches_any(haystack, CPU_KEYWORDS)
    has_laptop_word = _contains_phrase(haystack, "laptop") or _contains_phrase(haystack, "notebook")
    has_gaming_word = _contains_phrase(haystack, "gaming")
    has_strong_laptop_signal = bool(series_hits or gpu_hits or _matches_any(haystack, STRONG_LAPTOP_SIGNALS))

    # Accessory + "for laptop" is still accessory. Old logic trash. Replaced.
    if accessory_hits:
        accessory = accessory_hits[0]
        spec_only = all(hit in SPEC_ACCESSORIES for hit in accessory_hits)
        looks_like_real_laptop = has_laptop_word and has_strong_laptop_signal and not _contains_phrase(haystack, "for laptop")

        # RAM/SSD words are allowed inside real laptop specs. Other accessory
        # words are products, not specs, so they die here.
        if not (spec_only and looks_like_real_laptop):
            product["category_decision"] = "accessory_not_laptop"
            product["category_reason"] = f"accessory keyword: {accessory}"
            product["category_score"] = 0.0
            return product

    if has_laptop_word and series_hits and gpu_hits:
        product["category_decision"] = "candidate_laptop"
        product["category_reason"] = "gaming laptop series + GPU keyword"
        product["category_score"] = 1.0
        return product

    if has_laptop_word and series_hits:
        product["category_decision"] = "candidate_laptop"
        product["category_reason"] = f"gaming laptop series: {series_hits[0]}"
        product["category_score"] = 0.95
        return product

    if has_laptop_word and gpu_hits:
        product["category_decision"] = "candidate_laptop"
        product["category_reason"] = f"GPU laptop match: {gpu_hits[0]}"
        product["category_score"] = 0.9
        return product

    if has_laptop_word and has_gaming_word and (cpu_hits or _contains_phrase(haystack, "intel")):
        product["category_decision"] = "candidate_laptop"
        product["category_reason"] = "gaming laptop + CPU keyword"
        product["category_score"] = 0.82
        return product

    if series_hits and not accessory_hits:
        product["category_decision"] = "candidate_laptop"
        product["category_reason"] = f"known gaming laptop series: {series_hits[0]}"
        product["category_score"] = 0.78
        return product

    product["category_decision"] = "accessory_not_laptop"
    product["category_reason"] = "missing gaming laptop signal"
    product["category_score"] = 0.0
    return product


def filter_laptop_candidates(products: list[dict[str, Any]], query: str) -> CategoryFilterResult:
    """Classify products and split real laptop candidates from accessories."""
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    samples_kept: list[dict[str, Any]] = []
    samples_rejected: list[dict[str, Any]] = []

    for product in products or []:
        classified = classify_product_category(dict(product), query)
        reason = classified.get("category_reason", "")

        if classified.get("category_decision") == "candidate_laptop":
            candidates.append(classified)
            reasons[reason] += 1
            samples_kept.append({"title": classified.get("title", ""), "reason": reason})
            continue

        rejected.append(classified)
        reasons["accessory_not_laptop"] += 1
        samples_rejected.append({"title": classified.get("title", ""), "reason": reason})

    return CategoryFilterResult(
        query=query,
        total_products=len(products or []),
        candidates=candidates,
        rejected_accessories=rejected,
        reasons=dict(reasons),
        samples_rejected=samples_rejected,
        samples_kept=samples_kept,
    )
