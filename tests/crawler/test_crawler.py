import pytest
import aiohttp
from crawler.fetcher import Fetcher
from crawler.parser import parse_contacts


class TestCrawler:

    @pytest.mark.asyncio
    async def test_fetcher_fetches_html(self):
        fetcher = Fetcher(timeout=5)
        async with aiohttp.ClientSession() as session:
            html = await fetcher.fetch_url(session, "https://example.com")
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
                "<a href='tel:(+40) 123 - 456 789'></a>"
                "<a href='tel:(+40)-123-456 789'></a>"
                "<a href='tel:0722 456 789''></a>",
                ["+40123456789", "0722456789"]
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
                """
                <div class="sqs-block-button-container">
                    <a href='https://facebook.com/company'>Facebook</a>
                </div>
                <div class="social">
                    <a href='https://linkedin.com/company/test'>LinkedIn</a>
                </div>
                """,
                ["facebook.com", "linkedin.com"]
        ),
        (
                """
                <div class="social-links">
                    <a href='https://instagram.com/test'>Instagram</a>
                </div>
                <a href='https://x.com/test' aria-label="Social media link to X"></a>
                """,
                ["instagram.com", "x.com"]
        ),
    ])
    def test_parser_multiple_socials(self, html, expected_substrings):
        result = parse_contacts(html)
        socials = result["socials"]

        for expected in expected_substrings:
            assert any(expected in s for s in socials)
