import aiohttp

class Fetcher:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url, timeout=self.timeout) as resp:
            resp.raise_for_status()
            return await resp.text()
