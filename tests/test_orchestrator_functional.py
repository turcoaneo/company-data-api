import pytest
from aiohttp import web
import aiohttp
import os

from crawler.orchestrator import CrawlerOrchestrator


class TestCrawlerOrchestrator:

    # ---------------------------------------------------------
    # Fixture: local aiohttp server factory
    # ---------------------------------------------------------
    @pytest.fixture
    def server_factory(self, aiohttp_server):
        async def create(app):
            return await aiohttp_server(app)
        return create

    # ---------------------------------------------------------
    # Test 1: priority page returns contacts immediately
    # ---------------------------------------------------------
    @pytest.mark.asyncio
    async def test_priority_page_success(self, server_factory):
        async def handler_about(request):
            return web.Response(text="""
                <html>
                    <body>
                        <a href="tel:+40123456789">Call</a>
                        <a href="https://facebook.com/test">FB</a>
                    </body>
                </html>
            """)

        app = web.Application()
        app.router.add_get("/about", handler_about)
        server = await server_factory(app)

        orch = CrawlerOrchestrator(concurrency=2, timeout=5)
        domain = str(server.make_url(""))

        async with aiohttp.ClientSession() as session:
            result = await orch.crawl_domain(session, domain)

        assert result is not None
        assert "+40123456789" in result["phones"]
        assert any("facebook.com" in s for s in result["socials"])

    # ---------------------------------------------------------
    # Test 2: fallback full crawl finds contacts on subpage
    # ---------------------------------------------------------
    @pytest.mark.asyncio
    async def test_fallback_full_crawl(self, server_factory):
        async def handler_home(request):
            return web.Response(text="""
                <html>
                    <body>
                        <a href="/contact">Contact</a>
                    </body>
                </html>
            """)

        async def handler_contact(request):
            return web.Response(text="""
                <html>
                    <body>
                        <a href="tel:+40222222222">Phone</a>
                    </body>
                </html>
            """)

        app = web.Application()
        app.router.add_get("/", handler_home)
        app.router.add_get("/contact", handler_contact)
        server = await server_factory(app)

        orch = CrawlerOrchestrator(concurrency=2, timeout=5)
        domain = str(server.make_url(""))

        async with aiohttp.ClientSession() as session:
            result = await orch.crawl_domain(session, domain)

        assert result is not None
        assert "+40222222222" in result["phones"]

    # ---------------------------------------------------------
    # Test 3: domain with no contacts returns None
    # ---------------------------------------------------------
    @pytest.mark.asyncio
    async def test_no_contacts(self, server_factory):
        async def handler_home(request):
            return web.Response(text="<html><body>No contacts here</body></html>")

        app = web.Application()
        app.router.add_get("/", handler_home)
        server = await server_factory(app)

        orch = CrawlerOrchestrator(concurrency=2, timeout=5)
        domain = str(server.make_url(""))

        async with aiohttp.ClientSession() as session:
            result = await orch.crawl_domain(session, domain)

        assert result is None

    # ---------------------------------------------------------
    # Test 4: fetch exceptions are handled gracefully
    # ---------------------------------------------------------
    @pytest.mark.asyncio
    async def test_fetch_exception(self, server_factory, monkeypatch):
        async def handler_home(request):
            return web.Response(text="<html><body>OK</body></html>")

        app = web.Application()
        app.router.add_get("/", handler_home)
        server = await server_factory(app)

        # Force fetcher.fetch to raise
        async def fake_fetch(*args, **kwargs):
            raise RuntimeError("boom")

        from crawler.fetcher import Fetcher
        monkeypatch.setattr(Fetcher, "fetch", fake_fetch)

        orch = CrawlerOrchestrator(concurrency=2, timeout=5)
        domain = str(server.make_url(""))

        async with aiohttp.ClientSession() as session:
            result = await orch.crawl_domain(session, domain)

        assert result is None

    # ---------------------------------------------------------
    # Test 5: crawl() writes bad_urls.txt
    # ---------------------------------------------------------
    @pytest.mark.asyncio
    async def test_bad_urls_written(self, server_factory, tmp_path):
        # Good domain
        async def handler_contact(request):
            return web.Response(text="""
                <a href="tel:+401234">Call</a>
            """)

        app = web.Application()
        app.router.add_get("/", handler_contact)
        server = await server_factory(app)

        good_domain = str(server.make_url(""))
        bad_domain = "nonexistent-domain-xyz123.com"

        orch = CrawlerOrchestrator(concurrency=2, timeout=5)

        # Run crawl
        results = await orch.crawl([good_domain, bad_domain])

        # Validate good result
        assert len(results) == 1
        assert "+401234" in results[0]["phones"]

        # Validate bad_urls.txt
        bad_file = tmp_path / "bad_urls.txt"
        # Monkeypatch working directory
        os.chdir(tmp_path)

        await orch.crawl([good_domain, bad_domain])

        assert bad_file.exists()
        assert bad_domain in bad_file.read_text()
