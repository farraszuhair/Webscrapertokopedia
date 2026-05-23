from __future__ import annotations

import asyncio

import pytest

import src.ai.learning as learning
import src.ai.feedback_store as feedback_store
import src.ai.memory_store as memory_store
from src.ai.learning import save_feedback
from src.ai.relevance import (
    compute_rule_score,
    detect_query_intent,
    filter_relevance,
    has_gaming_laptop_evidence,
    is_obvious_junk_for_intent,
)


def _p(title: str) -> dict:
    return {"title": title, "price_raw": "Rp1.000.000", "url": f"https://tokopedia.com/{title.replace(' ', '-')}"}


def _filter_sync(query: str, titles: list[str]) -> list[dict]:
    products, status = asyncio.run(filter_relevance(query, [_p(t) for t in titles], use_ai=False))
    assert status == "disabled"
    return products


def test_laptop_gaming_intent_accepts_semantic_laptops_and_rejects_accessories():
    assert detect_query_intent("laptop gaming") == "main_product"
    accepted = _filter_sync("laptop gaming", [
        "ASUS ROG Strix G16",
        "Lenovo Legion 5",
        "Acer Nitro V15",
        "ASUS TUF RTX 4060",
        "HP Victus Gaming",
        "Charger laptop ASUS",
        "Tas laptop gaming",
        "Mouse gaming RGB",
        "RAM DDR4 laptop",
    ])
    titles = {p["title"] for p in accepted}
    assert "ASUS ROG Strix G16" in titles
    assert "Lenovo Legion 5" in titles
    assert "Acer Nitro V15" in titles
    assert "ASUS TUF RTX 4060" in titles
    assert "HP Victus Gaming" in titles
    assert "Mouse gaming RGB" not in titles
    assert "RAM DDR4 laptop" not in titles


@pytest.mark.parametrize("title", [
    "Laptop Lenovo LOQ 15 Intel Core i7 13650HX RTX4050",
    "HP VICTUS 15 RYZEN 5 RTX4050",
    "ASUS TUF A15 RYZEN 7 RTX2050",
    "Acer Nitro V 15 RTX3050",
    "ASUS TUF GAMING A15 RTX2050",
    "Lenovo LOQ RTX3050",
    "HP Victus RTX3050",
    "MSI THIN 15 RTX2050",
    "ROG STRIX G513RC RTX3050",
])
def test_laptop_gaming_positive_evidence_is_never_obvious_junk(title):
    product = _p(title)
    assert has_gaming_laptop_evidence(title) is True
    assert is_obvious_junk_for_intent("laptop gaming", product, "main_product") is False
    assert compute_rule_score("laptop gaming", product, "main_product") >= 0.72


@pytest.mark.parametrize("title", [
    "Mouse gaming RGB",
    "Keyboard gaming",
    "Cooling pad laptop",
    "Tas laptop gaming",
    "Charger laptop Asus",
    "LCD laptop",
    "Baterai laptop",
    "Skin sticker laptop",
])
def test_laptop_gaming_accessories_are_obvious_junk(title):
    assert is_obvious_junk_for_intent("laptop gaming", _p(title), "main_product") is True


def test_iphone_case_intent_obvious_junk_boundaries():
    assert is_obvious_junk_for_intent("casing iphone 13", _p("casing iphone 13"), "accessory") is False
    assert is_obvious_junk_for_intent("iphone 13", _p("casing iphone 13"), "main_product") is True
    assert is_obvious_junk_for_intent("iphone 13", _p("iphone 13 128gb"), "main_product") is False


def test_iphone_13_main_product_rejects_cases_and_chargers():
    assert detect_query_intent("iphone 13") == "main_product"
    accepted = _filter_sync("iphone 13", [
        "iPhone 13 128GB",
        "iPhone 13 Pro",
        "Casing iPhone 13",
        "Case iPhone 13",
        "Charger iPhone",
        "Tempered glass iPhone",
    ])
    titles = {p["title"] for p in accepted}
    assert "iPhone 13 128GB" in titles
    assert "iPhone 13 Pro" in titles
    assert "Casing iPhone 13" not in titles
    assert "Case iPhone 13" not in titles
    assert "Charger iPhone" not in titles
    assert "Tempered glass iPhone" not in titles


def test_casing_iphone_13_accessory_accepts_cases_only():
    assert detect_query_intent("casing iphone 13") == "accessory"
    accepted = _filter_sync("casing iphone 13", [
        "Casing iPhone 13",
        "Softcase iPhone 13",
        "Hardcase iPhone 13",
        "Case iPhone 13 MagSafe",
        "iPhone 13 128GB",
        "Charger iPhone",
        "Tempered glass iPhone",
    ])
    titles = {p["title"] for p in accepted}
    assert "Casing iPhone 13" in titles
    assert "Softcase iPhone 13" in titles
    assert "Hardcase iPhone 13" in titles
    assert "Case iPhone 13 MagSafe" in titles
    assert "iPhone 13 128GB" not in titles
    assert "Charger iPhone" not in titles


def test_charger_iphone_and_tas_laptop_intents():
    charger_titles = {p["title"] for p in _filter_sync("charger iphone", [
        "Charger iPhone original",
        "Kabel charger iPhone",
        "Adapter iPhone 20W",
        "Casing iPhone",
        "iPhone 13 128GB",
    ])}
    assert {"Charger iPhone original", "Kabel charger iPhone", "Adapter iPhone 20W"} <= charger_titles
    assert "Casing iPhone" not in charger_titles
    assert "iPhone 13 128GB" not in charger_titles

    bag_titles = {p["title"] for p in _filter_sync("tas laptop", [
        "Tas laptop 14 inch",
        "Sleeve laptop",
        "Backpack laptop",
        "Laptop Lenovo Ideapad",
    ])}
    assert {"Tas laptop 14 inch", "Sleeve laptop", "Backpack laptop"} <= bag_titles
    assert "Laptop Lenovo Ideapad" not in bag_titles


def test_feedback_is_scoped_by_query_intent(tmp_path, monkeypatch):
    monkeypatch.setattr(memory_store, "MEMORY_DIR", tmp_path)
    monkeypatch.setattr(memory_store, "FEEDBACK_FILE", tmp_path / "feedback.jsonl")
    monkeypatch.setattr(memory_store, "EXAMPLES_FILE", tmp_path / "examples.jsonl")
    monkeypatch.setattr(memory_store, "CATEGORY_RULES_FILE", tmp_path / "category_rules.json")
    monkeypatch.setattr(learning, "PRODUCT_FEEDBACK_FILE", tmp_path / "product_feedback.json")
    monkeypatch.setattr(feedback_store, "FEEDBACK_DB_PATH", tmp_path / "marketspy_feedback.db")

    product = {"title": "Casing iPhone 13", "url": "https://tokopedia.com/case", "product_category": "accessory"}
    before_main = compute_rule_score("iphone 13", product, "main_product")
    before_accessory = compute_rule_score("casing iphone 13", product, "accessory")

    save_feedback(
        query="iphone 13",
        query_intent="main_product",
        product=product,
        user_action="salah",
        selected_reasons=["Produk tidak relevan", "Bukan produk utama / cuma aksesoris"],
        feedback_type="negative",
        rule_score=before_main,
    )

    after_main = compute_rule_score("iphone 13", product, "main_product")
    after_accessory = compute_rule_score("casing iphone 13", product, "accessory")
    assert after_main <= before_main
    assert after_accessory >= before_accessory - 0.01
