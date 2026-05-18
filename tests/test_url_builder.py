from src.scraper.url_builder import build_tokopedia_search_url


def test_build_tokopedia_search_url_encodes_query():
    url = build_tokopedia_search_url("laptop gaming")

    assert url == "https://www.tokopedia.com/search?st=product&q=laptop%20gaming"


def test_build_tokopedia_search_url_adds_optional_budget_params():
    url = build_tokopedia_search_url("laptop gaming", 9_000_000, 11_000_000)

    assert "pmin=9000000" in url
    assert "pmax=11000000" in url
