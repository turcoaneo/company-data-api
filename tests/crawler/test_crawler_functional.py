import aiohttp
import pytest
from aiohttp import web

from crawler.fetcher import Fetcher
from crawler.parser import parse_contacts


class TestCrawlerFunctional:

    # ---------------------------------------------------------
    # FIXED: sync fixture returning an async server factory
    # ---------------------------------------------------------
    @pytest.fixture
    def test_server(self, aiohttp_server):
        async def handler_contact(request):
            html = """
            <html>
              <body>
                <p>Call us at +40 123 456 789</p>
                <a href="tel:+40222222222">Phone</a>
                <a href="https://facebook.com/company">FB</a>
                <a href="https://linkedin.com/company/test">LI</a>
              </body>
            </html>
            """
            return web.Response(text=html, content_type="text/html")

        async def create():
            app = web.Application()
            app.router.add_get("/contact", handler_contact)
            return await aiohttp_server(app)

        return create

    # ---------------------------------------------------------
    # Functional test: fetch → parse → validate
    # ---------------------------------------------------------
    @pytest.mark.asyncio
    async def test_full_crawl_and_parse(self, test_server):
        server = await test_server()
        url = f"{server.make_url('/contact')}"

        fetcher = Fetcher(timeout=5)

        async with aiohttp.ClientSession() as session:
            html = await fetcher.fetch_url(session, url)

        result = parse_contacts(html)

        # Phones
        assert any("+40 123 456 789" in p for p in result["phones"])
        assert any("+40222222222" in p for p in result["phones"])

        # Socials
        assert any("facebook.com" in s for s in result["socials"])
        assert any("linkedin.com" in s for s in result["socials"])
