"""
test_preflight.py - Tests for preflight Chrome error page detection.
"""
import pytest
from src.scraper.preflight import (
    _detect_error_type,
    _is_real_tokopedia_page,
    build_preflight_result,
)


class TestDetectErrorType:
    def test_http2_protocol_error(self):
        assert _detect_error_type("ERR_HTTP2_PROTOCOL_ERROR", "", "") == "http2_protocol_error"

    def test_connection_reset(self):
        assert _detect_error_type("ERR_CONNECTION_RESET", "", "") == "connection_reset"

    def test_site_unreachable_english(self):
        assert _detect_error_type("This site can't be reached", "", "") == "site_unreachable"

    def test_site_unreachable_indonesian(self):
        assert _detect_error_type("", "Situs ini tidak dapat dijangkau", "") == "site_unreachable_id"

    def test_about_blank(self):
        assert _detect_error_type("", "", "about:blank") == "blank_page"

    def test_no_error(self):
        assert _detect_error_type("Tokopedia", "laptop gaming", "https://www.tokopedia.com/search") is None

    def test_err_in_body(self):
        assert _detect_error_type("", "ERR_NAME_NOT_RESOLVED", "") == "name_not_resolved"


class TestIsRealTokopediaPage:
    def test_tokopedia_in_title(self):
        assert _is_real_tokopedia_page("Tokopedia", "", "") is True

    def test_tokopedia_in_url(self):
        assert _is_real_tokopedia_page("", "", "https://www.tokopedia.com/search") is True

    def test_chrome_error_page(self):
        assert _is_real_tokopedia_page("This site can't be reached", "ERR_HTTP2_PROTOCOL_ERROR", "") is False

    def test_empty_page(self):
        assert _is_real_tokopedia_page("", "", "") is False


class TestBuildPreflightResult:
    def test_real_page(self):
        result = build_preflight_result(
            url="https://tokopedia.com/search",
            title="Tokopedia - laptop gaming",
            body_sample="laptop gaming result",
            current_url="https://tokopedia.com/search?st=product&q=laptop",
            load_time_ms=1200.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is True
        assert result["error_type"] is None

    def test_error_page(self):
        result = build_preflight_result(
            url="https://tokopedia.com/search",
            title="ERR_HTTP2_PROTOCOL_ERROR",
            body_sample="This site can't be reached",
            current_url="https://tokopedia.com/search",
            load_time_ms=500.0,
            engine="rollback",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "http2_protocol_error"

    def test_blank_page(self):
        result = build_preflight_result(
            url="https://tokopedia.com/search",
            title="",
            body_sample="",
            current_url="about:blank",
            load_time_ms=100.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "blank_page"
