from src.scraper.budget_filter import filter_by_budget


def test_budget_10jt_tolerance_10_keeps_9jt_to_11jt():
    result = filter_by_budget(
        [
            {"title": "low", "price_raw": "Rp8.999.999", "url": "https://x/low"},
            {"title": "min", "price_raw": "Rp9.000.000", "url": "https://x/min"},
            {"title": "mid", "price_raw": "Rp10.000.000", "url": "https://x/mid"},
            {"title": "max", "price_raw": "Rp11.000.000", "url": "https://x/max"},
            {"title": "high", "price_raw": "Rp11.000.001", "url": "https://x/high"},
        ],
        "10.000.000",
        10,
    )

    assert result.min_price == 9_000_000
    assert result.max_price == 11_000_000
    assert [product["title"] for product in result.kept] == ["min", "mid", "max"]
    assert result.reasons["below_budget_range"] == 1
    assert result.reasons["above_budget_range"] == 1


def test_empty_budget_keeps_valid_pipeline_candidates():
    result = filter_by_budget(
        [{"title": "ASUS TUF Gaming F15 RTX 3050 Laptop", "price_raw": "Rp15.000.000", "url": "https://x/tuf"}],
        None,
        10,
    )

    assert result.budget_value is None
    assert len(result.kept) == 1
    assert result.kept[0]["budget_decision"] == "kept"
