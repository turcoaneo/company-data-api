# tests/utils/test_url_normalizer.py

import pytest
from aiohttp import web
import aiohttp

from crawler.util.url_normalizer import resolve_homepage


class TestUrlNormalizer:

    @pytest.mark.asyncio
    async def test_resolve_homepage_http_fallback(self, aiohttp_server):
        async def handler(request):
            return web.Response(text="OK")

        app = web.Application()
        app.router.add_get("/", handler)
        server = await aiohttp_server(app)

        # Convert URL object → string
        base_url = str(server.make_url(""))

        # Strip protocol for testing fallback
        domain = base_url.replace("http://", "").rstrip("/")

        async with aiohttp.ClientSession() as session:
            html, resolved_base = await resolve_homepage(session, f"https://{domain}")

        assert html == "OK"
        assert resolved_base.startswith("http://")

