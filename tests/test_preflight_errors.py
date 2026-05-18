"""
test_preflight_errors.py - Test Chrome error page detection.

Coverage:
- ERR_HTTP2_PROTOCOL_ERROR detected
- ERR_CONNECTION_RESET detected
- This site can't be reached detected
- Situs ini tidak dapat dijangkau detected
- about:blank detected
- Chrome error page stops extraction
- Real Tokopedia page allows extraction
"""
from __future__ import annotations

import pytest

from src.scraper.preflight import _detect_error_type, _is_real_tokopedia_page, build_preflight_result


class TestErrorTypeDetection:
    """Test detection of known Chrome network error signals."""

    def test_http2_protocol_error(self):
        """Detect ERR_HTTP2_PROTOCOL_ERROR."""
        title = "ERR_HTTP2_PROTOCOL_ERROR"
        body = "The server reset the connection before page could load."
        url = "https://www.tokopedia.com/search?q=laptop"
        assert _detect_error_type(title, body, url) == "http2_protocol_error"

    def test_connection_reset(self):
        """Detect ERR_CONNECTION_RESET."""
        title = "ERR_CONNECTION_RESET"
        body = "The connection was reset."
        url = "https://www.tokopedia.com/search?q=laptop"
        assert _detect_error_type(title, body, url) == "connection_reset"

    def test_site_cant_be_reached_en(self):
        """Detect 'This site can't be reached'."""
        title = "This site can't be reached"
        body = "Check the spelling or try searching."
        url = "about:blank"
        assert _detect_error_type(title, body, url) == "site_unreachable"

    def test_site_cant_be_reached_id(self):
        """Detect 'Situs ini tidak dapat dijangkau'."""
        title = "Situs ini tidak dapat dijangkau"
        body = "Periksa ejaan atau coba mencari."
        url = "about:blank"
        assert _detect_error_type(title, body, url) == "site_unreachable_id"

    def test_blank_page(self):
        """Detect about:blank."""
        title = ""
        body = ""
        url = "about:blank"
        assert _detect_error_type(title, body, url) == "blank_page"

    def test_blank_page_from_chrome_newtab(self):
        """Detect chrome://newtab/ as blank page."""
        title = ""
        body = ""
        url = "chrome://newtab/"
        assert _detect_error_type(title, body, url) == "blank_page"

    def test_no_error_on_real_tokopedia_page(self):
        """No error detected on real Tokopedia page."""
        title = "Tokopedia - Jual Beli Online Terpercaya"
        body = "Laptop Gaming ROG ASUS..."
        url = "https://www.tokopedia.com/search?q=laptop"
        assert _detect_error_type(title, body, url) is None

    def test_unknown_non_tokopedia_page(self):
        """Detect non-Tokopedia page as error."""
        title = "Some Random Site"
        body = "This is not Tokopedia"
        url = "https://example.com"
        # Should be detected as unknown_non_tokopedia_page by build_preflight_result
        # (not by _detect_error_type which returns None)
        assert _detect_error_type(title, body, url) is None


class TestRealPageDetection:
    """Test detection of real Tokopedia pages."""

    def test_tokopedia_in_title(self):
        """Detect 'tokopedia' in title."""
        assert _is_real_tokopedia_page("Tokopedia - Laptop Gaming", "", "")

    def test_tokopedia_in_url(self):
        """Detect 'tokopedia' in URL."""
        assert _is_real_tokopedia_page("", "", "https://www.tokopedia.com/search?q=laptop")

    def test_tokopedia_in_body(self):
        """Detect 'tokopedia' in body."""
        assert _is_real_tokopedia_page("", "Tokopedia adalah marketplace terpercaya", "")

    def test_toped_shorthand(self):
        """Detect 'toped' shorthand."""
        assert _is_real_tokopedia_page("Toped - Jual Beli", "", "")

    def test_not_tokopedia(self):
        """Not Tokopedia page detected."""
        assert not _is_real_tokopedia_page("Some Store", "Random stuff", "https://example.com")


class TestPreflightResult:
    """Test the full preflight result building."""

    def test_real_page_result(self):
        """Preflight result for real Tokopedia page."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="Tokopedia - Laptop Gaming",
            body_sample="ROG ASUS TUF...",
            current_url="https://www.tokopedia.com/search?q=laptop",
            load_time_ms=2500.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is True
        assert result["error_type"] is None
        assert "tokopedia" in result["message"].lower()

    def test_error_page_result(self):
        """Preflight result for Chrome error page."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="ERR_HTTP2_PROTOCOL_ERROR",
            body_sample="The server reset the connection.",
            current_url="https://www.tokopedia.com/search?q=laptop",
            load_time_ms=5000.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "http2_protocol_error"
        assert "error" in result["message"].lower() or "page" in result["message"].lower()

    def test_blank_page_result(self):
        """Preflight result for blank page."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="",
            body_sample="",
            current_url="about:blank",
            load_time_ms=100.0,
            engine="puppeteer",
        )
        assert result["opened_real_page"] is False
        assert result["error_type"] == "blank_page"

    def test_rollback_engine_preflight(self):
        """Preflight result for Rollback/Selenium engine."""
        result = build_preflight_result(
            url="https://www.tokopedia.com/search?q=laptop",
            title="Tokopedia",
            body_sample="Tokopedia - Jual Beli",
            current_url="https://www.tokopedia.com/search?q=laptop",
            load_time_ms=3000.0,
            engine="rollback",
        )
        assert result["opened_real_page"] is True
        assert result["error_type"] is None
        assert result["engine"] == "rollback"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
