import aiohttp

from app.utils.logger_util import get_logger

logger = get_logger()


class Fetcher:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def fetch_url(self, session: aiohttp.ClientSession, url: str) -> str:
        try:
            async with session.get(url, timeout=self.timeout) as resp:
                resp.raise_for_status()
                return await resp.text()
        except Exception as e:
            logger.error(f"Fetcher error for {url}: {e}")
            return ""  # <--- SOLID fallback
