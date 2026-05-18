from src.scraper.budget_filter import filter_by_budget
from src.scraper.category_filter import filter_laptop_candidates
from src.scraper.engine_selector import EngineRunResult
from src.scraper.normalizer import normalize_products
from src.server.routes import _engine_run_payload


def test_engine_payload_raw_count_is_before_filters():
    run = EngineRunResult(
        engine="puppeteer",
        ok=True,
        products=[
            {"title": "Gaming Mouse for Laptop", "price_raw": "Rp100.000", "url": "https://tokopedia.test/mouse"},
            {"title": "ASUS TUF Gaming F15 RTX 3050 Laptop", "price_raw": "Rp10.000.000", "url": "https://tokopedia.test/tuf"},
        ],
        duration_seconds=1.25,
    )

    payload = _engine_run_payload(run)

    assert payload["raw_count"] == 2
    assert payload["raw_products_found"] == 2


def test_report_metric_order_raw_category_budget():
    raw_products = [
        {"title": "Gaming Mouse for Laptop", "price_raw": "Rp100.000", "url": "https://tokopedia.test/mouse"},
        {"title": "ASUS TUF Gaming F15 RTX 3050 Laptop", "price_raw": "Rp10.000.000", "url": "https://tokopedia.test/tuf"},
        {"title": "Lenovo LOQ 15IRX9 Gaming Laptop", "price_raw": "Rp13.000.000", "url": "https://tokopedia.test/loq"},
    ]

    normalized = normalize_products(raw_products, "rollback")
    category = filter_laptop_candidates(normalized, "laptop gaming")
    budget = filter_by_budget(category.candidates, "10.000.000", 10)

    assert len(raw_products) == 3
    assert category.candidate_count == 2
    assert category.rejected_accessory_count == 1
    assert len(budget.kept) == 1


def test_compare_reports_keep_both_engines_separate():
    puppeteer = EngineRunResult("puppeteer", True, [{"title": "ASUS TUF Gaming F15 RTX 3050 Laptop", "url": "https://x/tuf"}])
    rollback = EngineRunResult("rollback", False, [], "zero raw")

    assert _engine_run_payload(puppeteer)["engine"] == "puppeteer"
    assert _engine_run_payload(rollback)["engine"] == "rollback"
    assert _engine_run_payload(rollback)["status"] == "fail"
