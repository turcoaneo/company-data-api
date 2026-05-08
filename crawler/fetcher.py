import aiohttp

from app.utils.logger_util import get_logger

logger = get_logger()


class Fetcher:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def fetch_url(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url, timeout=self.timeout) as resp:
            try:
                resp.raise_for_status()
            except Exception as e:
                logger.error(f"Error fetching url {e}")

            return await resp.text()
