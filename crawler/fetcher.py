# crawler/fetcher.py

import asyncio
from typing import Optional

import aiohttp

from app.utils.logger_util import get_logger

logger = get_logger()

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class Fetcher:
    def __init__(
            self,
            timeout: int = 10,
            max_retries: int = 2,
            backoff_factor: float = 0.5,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def fetch_url(
            self,
            session: aiohttp.ClientSession,
            url: str,
            *,
            allow_insecure: bool = True,
    ) -> str:
        """
        Robust fetch:
        - custom UA
        - retries
        - timeout
        - optional SSL relax
        - always returns str ("" on failure)
        """
        last_exc: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with session.get(
                        url,
                        timeout=timeout,
                        headers=DEFAULT_HEADERS,
                        ssl=False if allow_insecure else None,
                        allow_redirects=True,
                ) as resp:
                    # Raise for HTTP errors
                    resp.raise_for_status()
                    text = await resp.text(errors="ignore")
                    return text or ""
            except Exception as e:
                last_exc = e
                logger.error(
                    f"Fetcher error for {url} (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                # simple backoff
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_factor * (2 ** attempt))

        logger.error(f"Fetcher giving up on {url} after {self.max_retries + 1} attempts: {last_exc}")
        return ""
