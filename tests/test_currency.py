from src.scraper.budget_filter import filter_by_budget
from src.utils.currency import parse_rupiah


def product(title, price_raw):
    return {"title": title, "price_raw": price_raw, "url": f"https://tokopedia.test/{title}"}


def test_parse_rupiah_plain_values():
    assert parse_rupiah("Rp10.000.000") == 10_000_000
    assert parse_rupiah("10.000.000") == 10_000_000
    assert parse_rupiah("Rp 10.000.000") == 10_000_000


def test_parse_rupiah_units():
    assert parse_rupiah("Rp10,5 juta") == 10_500_000
    assert parse_rupiah("Rp10.5 juta") == 10_500_000
    assert parse_rupiah("Rp10 jt") == 10_000_000
    assert parse_rupiah("Rp999 rb") == 999_000


def test_parse_rupiah_invalid_values():
    assert parse_rupiah("") is None
    assert parse_rupiah(None) is None
    assert parse_rupiah("Hubungi Penjual") is None


def test_empty_budget_keeps_products():
    result = filter_by_budget(
        [product("valid", "Rp10.000.000"), product("invalid price", "Hubungi Penjual")],
        "",
        20,
    )

    assert result.budget_value is None
    assert len(result.kept) == 2
    assert result.reasons == {}


def test_budget_range_keeps_8jt_to_12jt():
    result = filter_by_budget(
        [
            product("eight", "Rp8.000.000"),
            product("ten", "Rp10.000.000"),
            product("twelve", "Rp12.000.000"),
        ],
        "10.000.000",
        20,
    )

    assert result.min_price == 8_000_000
    assert result.max_price == 12_000_000
    assert len(result.kept) == 3


def test_budget_reject_reasons():
    result = filter_by_budget(
        [
            product("above", "Rp15.000.000"),
            product("below", "Rp5.000.000"),
            product("invalid", "Hubungi Penjual"),
        ],
        "10.000.000",
        20,
    )

    assert len(result.kept) == 1
    assert result.reasons["above_budget_range"] == 1
    assert result.reasons["below_budget_range"] == 1
    assert result.reasons["invalid_price_kept"] == 1
    assert {item["reject_reason"] for item in result.rejected} == {
        "above_budget_range",
        "below_budget_range",
    }
    assert result.kept[0]["price_parse_failed"] is True
    for rejected in result.rejected:
        assert "price_raw" in rejected
        assert "price_value" in rejected
        assert rejected["min_price"] == 8_000_000
        assert rejected["max_price"] == 12_000_000
