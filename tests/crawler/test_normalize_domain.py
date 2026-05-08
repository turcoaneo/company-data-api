import pytest
from crawler.pipeline import normalize_domain


class TestNormalizeDomain:

    # ---------------------------------------------------------
    # 1. Bare domains should remain unchanged (except lowercase)
    # ---------------------------------------------------------
    def test_bare_domain(self):
        assert normalize_domain("Example.COM") == "example.com"
        assert normalize_domain("mazautoglass.com") == "mazautoglass.com"

    # ---------------------------------------------------------
    # 2. Domains with trailing slashes
    # ---------------------------------------------------------
    def test_trailing_slash(self):
        assert normalize_domain("mazautoglass.com/") == "mazautoglass.com"
        assert normalize_domain("example.com////") == "example.com"

    # ---------------------------------------------------------
    # 3. Full URLs with protocol
    # ---------------------------------------------------------
    def test_full_url(self):
        assert normalize_domain("https://mazautoglass.com") == "mazautoglass.com"
        assert normalize_domain("http://example.com/") == "example.com"

    # ---------------------------------------------------------
    # 4. URLs with paths
    # ---------------------------------------------------------
    def test_url_with_path(self):
        assert normalize_domain("https://example.com/contact") == "example.com"
        assert normalize_domain("http://mazautoglass.com/about/") == "mazautoglass.com"

    # ---------------------------------------------------------
    # 5. URLs with www
    # ---------------------------------------------------------
    def test_www(self):
        assert normalize_domain("https://www.example.com") == "www.example.com"
        assert normalize_domain("www.example.com/") == "www.example.com"

    # ---------------------------------------------------------
    # 6. Whitespace handling
    # ---------------------------------------------------------
    def test_whitespace(self):
        assert normalize_domain("   example.com   ") == "example.com"
        assert normalize_domain("   https://example.com  ") == "example.com"

    # ---------------------------------------------------------
    # 7. Invalid inputs
    # ---------------------------------------------------------
    def test_invalid_inputs(self):
        assert normalize_domain(None) == ""
        assert normalize_domain(123) == ""
        assert normalize_domain("") == ""
        assert normalize_domain("   ") == ""

    # ---------------------------------------------------------
    # 8. Edge case: protocol but no netloc
    # ---------------------------------------------------------
    def test_protocol_no_netloc(self):
        # urlparse("https://example.com") → netloc="example.com"
        # urlparse("https:///path") → netloc="" and path="/path"
        assert normalize_domain("https:///path") == "path"
