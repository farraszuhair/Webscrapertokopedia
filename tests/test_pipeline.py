from src.scraper.budget_filter import filter_by_budget
from src.scraper.category_filter import filter_laptop_candidates
from src.scraper.normalizer import normalize_products


def test_accessories_die_before_budget():
    raw_products = [
        {
            "title": "Redragon RANGER Wired Gaming Mouse High Precision USB Mouse for PC Laptop",
            "price_raw": "Rp210.200",
            "url": "https://tokopedia.test/mouse",
        },
        {
            "title": "Power Adaptor Charger Laptop INNERGIE Gaming Universal",
            "price_raw": "Rp1.563.500",
            "url": "https://tokopedia.test/charger",
        },
        {
            "title": "LLANO V12 Laptop Cooling Pad Gaming Laptop Cooler",
            "price_raw": "Rp1.489.999",
            "url": "https://tokopedia.test/cooler",
        },
        {
            "title": "ASUS TUF Gaming F15 RTX 3050 Laptop",
            "price_raw": "Rp10.500.000",
            "url": "https://tokopedia.test/tuf",
        },
        {
            "title": "Lenovo Legion 5 Ryzen 7 RTX 4060",
            "price_raw": "Rp15.500.000",
            "url": "https://tokopedia.test/legion",
        },
    ]

    normalized = normalize_products(raw_products, "puppeteer")
    category = filter_laptop_candidates(normalized, "laptop gaming")
    budget = filter_by_budget(category.candidates, "10.000.000", 10)

    assert category.total_products == 5
    assert category.candidate_count == 2
    assert category.rejected_accessory_count == 3
    assert budget.total_products == 2
    assert len(budget.kept) == 1
    assert budget.reasons.get("below_budget_range", 0) == 0
    assert budget.reasons.get("above_budget_range", 0) == 1


def test_budget_debug_counts_category_candidates_only():
    normalized = normalize_products(
        [
            {
                "title": "Mouse Pad Gaming Anime Extra Large Alas Mouse Laptop",
                "price_raw": "Rp53.900",
                "url": "https://tokopedia.test/mousepad",
            },
            {
                "title": "HP Victus 15 Gaming Laptop",
                "price_raw": "Rp9.999.000",
                "url": "https://tokopedia.test/victus",
            },
        ],
        "rollback",
    )
    category = filter_laptop_candidates(normalized, "laptop gaming")
    budget = filter_by_budget(category.candidates, "10.000.000", 10)
    payload = budget.debug_payload()

    assert payload["total_category_candidates"] == 1
    assert payload["kept"] == 1
    assert payload["below_budget_range"] == 0
    assert category.rejected_accessory_count == 1
