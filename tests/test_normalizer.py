from src.scraper.normalizer import normalize_products_with_report


def test_raw_product_with_title_and_url_is_kept():
    report = normalize_products_with_report(
        [{"title": "ASUS TUF Gaming F15 RTX 3050 Laptop", "url": "https://tokopedia.test/store/tuf"}],
        "puppeteer",
    )

    assert report.input_count == 1
    assert report.output_count == 1
    assert report.dropped_count == 0


def test_missing_shop_location_image_does_not_drop_product():
    report = normalize_products_with_report(
        [{"title": "Lenovo LOQ 15IRX9 Gaming Laptop", "url": "https://tokopedia.test/store/loq"}],
        "rollback",
    )

    product = report.output[0]
    assert product["shop"] == ""
    assert product["location"] == ""
    assert product["image"] == ""


def test_missing_price_does_not_drop_raw_product():
    report = normalize_products_with_report(
        [{"title": "Acer Nitro V15 RTX 4050", "url": "https://tokopedia.test/store/nitro"}],
        "puppeteer",
    )

    assert report.output_count == 1
    assert report.output[0]["price_value"] is None


def test_missing_title_is_dropped_with_reason():
    report = normalize_products_with_report([{"url": "https://tokopedia.test/store/no-title"}], "rollback")

    assert report.output_count == 0
    assert report.drop_reasons["missing_title"] == 1
