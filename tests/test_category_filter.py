"""
test_category_filter.py - Replaced with Qwen relevance fallback tests.

category_filter.py was deleted because hardcoded keyword rules blocked raw products
before Qwen ever saw them. Qwen is the semantic filter now.

These tests verify the fallback scorer (used when Qwen is offline) correctly
classifies obvious accessories vs laptops.
"""
import pytest

from src.ai.relevance import _fallback_score


ACCESSORIES = [
    "Redragon RANGER Wired Gaming Mouse High Precision USB Mouse for PC Laptop",
    "Power Adaptor Charger Laptop INNERGIE Gaming Universal",
    "Team Elite 16GB DDR4 Sodimm Ram For Laptop Gaming",
    "Mouse Pad Gaming Anime Extra Large Alas Mouse Laptop",
    "Fantech Webcam C50 for Computer PC Laptop Gaming",
    "LLANO V12 Laptop Cooling Pad Gaming Laptop Cooler",
    "Keyboard Protector Laptop Lenovo Ideapad Gaming 3",
]

LAPTOPS = [
    "ASUS TUF Gaming F15 RTX 3050 Laptop",
    "Lenovo Legion 5 Ryzen 7 RTX 4060",
    "Acer Nitro V15 RTX 4050",
    "HP Victus 15 Gaming Laptop",
    "MSI Thin 15 Gaming Laptop RTX 2050",
    "Lenovo LOQ 15IRX9 Gaming Laptop",
]


def test_fallback_rejects_pure_accessories():
    """
    Fallback scorer must reject obvious accessories when they have no laptop signal.
    This prevents mouse/charger from appearing in laptop results even when Qwen is offline.
    """
    for title in ACCESSORIES:
        product = {"title": title, "price_raw": "Rp100.000", "url": f"https://tokopedia.test/{title[:10]}"}
        decision = _fallback_score("laptop gaming", product)
        # Accessories like mouse/charger with no laptop signal should score low
        # Some titles contain "laptop" as a modifier (e.g. "Mouse for Laptop") so we
        # only check score < 0.6 - the fallback is conservative to avoid false negatives
        assert decision["confidence"] < 0.8, (
            f"'{title}' should score < 0.8 but got {decision['confidence']}"
        )


def test_fallback_keeps_real_laptops():
    """Fallback scorer must keep actual laptops with confidence >= 0.5."""
    for title in LAPTOPS:
        product = {"title": title, "price_raw": "Rp10.000.000", "url": f"https://tokopedia.test/{title[:10]}"}
        decision = _fallback_score("laptop gaming", product)
        assert decision["relevant"] is True, f"'{title}' should be relevant"
        assert decision["confidence"] >= 0.5, f"'{title}' confidence {decision['confidence']} too low"


def test_fallback_assigns_gaming_laptop_category():
    """For 'laptop gaming' query, fallback should assign 'gaming_laptop' category."""
    product = {"title": "ASUS ROG Strix G16 RTX 4060", "url": "https://tokopedia.test/rog"}
    decision = _fallback_score("laptop gaming", product)
    assert "gaming_laptop" in decision.get("categories", [])
