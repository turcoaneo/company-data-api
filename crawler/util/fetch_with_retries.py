# crawler/util/fetch_with_retries.py

import aiohttp
from app.utils.logger_util import get_logger

logger = get_logger()

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


# noinspection DuplicatedCode
async def fetch_with_retries(session, url, timeout):
    """
    Multi-strategy fetch to bypass non-Cloudflare 403 bot blocks.
    Returns dict:
    {
        "ok": bool,
        "status": int or None,
        "html": str or None
    }
    """

    # Strategy 1: GET with browser headers
    browser_header = "Browser-header"
    try:
        async with session.get(url, ssl=False, timeout=timeout, headers=BROWSER_HEADERS) as resp:
            html = await resp.text(errors="ignore")
            if resp.status < 400:
                return {"ok": True, "status": resp.status, "html": html}
            logger.debug(f"{browser_header} GET failed for {url}: {resp.status}")
    except Exception as e:
        logger.debug(f"{browser_header} GET exception for {url}: {e}")

    # Strategy 2: HEAD request
    try:
        async with session.head(url, ssl=False, timeout=timeout) as resp:
            if resp.status < 400:
                return {"ok": True, "status": resp.status, "html": ""}
            logger.debug(f"HEAD failed for {url}: {resp.status}")
    except Exception as e:
        logger.debug(f"HEAD exception for {url}: {e}")

    # Strategy 3: GET with cookie jar
    cookie_jar = "Cookie-jar"
    try:
        jar = aiohttp.CookieJar()
        async with aiohttp.ClientSession(cookie_jar=jar) as s2:
            async with s2.get(url, ssl=False, timeout=timeout, headers=BROWSER_HEADERS) as resp:
                html = await resp.text(errors="ignore")
                if resp.status < 400:
                    return {"ok": True, "status": resp.status, "html": html}
                logger.debug(f"{cookie_jar} GET failed for {url}: {resp.status}")
    except Exception as e:
        logger.debug(f"cookie_jar GET exception for {url}: {e}")

    # Strategy 4: POST fallback
    try:
        async with session.post(url, ssl=False, timeout=timeout, headers=BROWSER_HEADERS, data={}) as resp:
            html = await resp.text(errors="ignore")
            if resp.status < 400:
                return {"ok": True, "status": resp.status, "html": html}
            logger.debug(f"POST fallback failed for {url}: {resp.status}")
    except Exception as e:
        logger.debug(f"POST fallback exception for {url}: {e}")

    return {"ok": False, "status": None, "html": None}
