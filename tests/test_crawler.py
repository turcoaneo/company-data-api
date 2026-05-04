import pytest
import aiohttp
from crawler.fetcher import Fetcher
from crawler.parser import parse_contacts


class TestCrawler:

    @pytest.mark.asyncio
    async def test_fetcher_fetches_html(self):
        fetcher = Fetcher(timeout=5)
        async with aiohttp.ClientSession() as session:
            html = await fetcher.fetch(session, "https://example.com")
        assert "<html" in html.lower()

    # -----------------------------
    # Phones
    # -----------------------------
    @pytest.mark.parametrize("html,expected", [
        (
            "<a href='tel:+40123456789'></a>"
            "<a href='tel:+40222222222'></a>",
            ["+40123456789", "+40222222222"]
        ),
        (
            "<a href='tel:123'></a>"
            "<a href='tel:456'></a>"
            "<a href='tel:789'></a>",
            ["123", "456", "789"]
        ),
    ])
    def test_parser_multiple_phones(self, html, expected):
        result = parse_contacts(html)
        assert result["phones"] == expected

    # -----------------------------
    # Social media
    # -----------------------------
    @pytest.mark.parametrize("html,expected_substrings", [
        (
            "<a href='https://facebook.com/company'></a>"
            "<a href='https://linkedin.com/company/test'></a>",
            ["facebook.com", "linkedin.com"]
        ),
        (
            "<a href='https://instagram.com/test'></a>"
            "<a href='https://x.com/test'></a>",
            ["instagram.com", "x.com"]
        ),
    ])
    def test_parser_multiple_socials(self, html, expected_substrings):
        result = parse_contacts(html)
        socials = result["socials"]

        # Ensure each expected substring appears in at least one extracted link
        for expected in expected_substrings:
            assert any(expected in s for s in socials)
