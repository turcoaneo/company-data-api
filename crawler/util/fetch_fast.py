# crawler/util/fetch_fast.py

import aiohttp
from app.utils.logger_util import get_logger

logger = get_logger()


async def fetch_fast(session, url: str, timeout: int):
    """
    Very fast fetch: single GET, no retries, no heavy headers.
    Returns (ok, status, html)
    """
    try:
        async with session.get(url, ssl=False, timeout=timeout) as resp:
            html = await resp.text(errors="ignore")
            return True, resp.status, html
    except Exception as e:
        logger.debug(f"Fast fetch failed for {url}: {e}")
        return False, None, None
