"""
url_builder.py - Tokopedia public search URL builder.

Engines use one URL builder so Puppeteer and Selenium compare the same pages.
"""
from __future__ import annotations

from urllib.parse import quote, urlencode


def build_tokopedia_search_url(
    query: str,
    min_price: int | None = None,
    max_price: int | None = None,
    page: int | None = None,
) -> str:
    """
    Build a Tokopedia product search URL with safe query encoding.

    Price params are optional. Engines may still choose to try no-price URLs
    first and rely on local budget filtering when the site ignores filters.
    """
    params: dict[str, str] = {
        "st": "product",
        "q": query,
    }
    if min_price is not None:
        params["pmin"] = str(int(min_price))
    if max_price is not None:
        params["pmax"] = str(int(max_price))
    if page is not None:
        params["page"] = str(int(page))
    return "https://www.tokopedia.com/search?" + urlencode(params, quote_via=quote)


def build_tokopedia_search_urls_for_variant(
    query: str,
    min_price: int | None = None,
    max_price: int | None = None,
) -> list[str]:
    """
    Return URLs to try for one query variant.

    First URL has no price params. If product extraction works, local filters
    handle budget. Second URL tries site price params for diagnostics/backup.
    """
    urls = [build_tokopedia_search_url(query)]
    if min_price is not None or max_price is not None:
        priced_url = build_tokopedia_search_url(query, min_price, max_price)
        if priced_url not in urls:
            urls.append(priced_url)
    return urls
