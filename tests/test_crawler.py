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

    def test_parser_extracts_phone(self):
        html = "<a href='tel:+40123456789'>Call</a>"
        result = parse_contacts(html)
        assert "+40123456789" in result["phones"]

    def test_parser_extracts_email(self):
        html = "<a href='mailto:test@example.com'>Email</a>"
        result = parse_contacts(html)
        assert "test@example.com" in result["emails"]

    def test_parser_extracts_socials(self):
        html = "<a href='https://facebook.com/test'>FB</a>"
        result = parse_contacts(html)
        assert any("facebook.com" in s for s in result["socials"])
