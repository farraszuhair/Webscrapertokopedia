from src.scraper.query_expander import budget_url_range, expand_query_variants


def test_laptop_gaming_expands_to_brand_and_gpu_queries():
    variants = expand_query_variants("laptop gaming")

    assert variants[:3] == ["laptop gaming", "notebook gaming", "asus rog laptop"]
    assert "lenovo legion laptop" in variants
    assert "laptop rtx 4050" in variants


def test_budget_url_range_matches_filter_math():
    assert budget_url_range("10.000.000", 10) == (9_000_000, 11_000_000)
