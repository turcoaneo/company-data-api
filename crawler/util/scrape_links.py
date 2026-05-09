# crawler/util/scrape_links.py

import asyncio

from crawler.parser import parse_contacts
from crawler.pipeline import normalize_record


async def scrape_links(session, links, timeout, concurrency):
    if not links:
        return None

    sem = asyncio.Semaphore(concurrency)

    async def fetch_and_parse(url: str):
        async with sem:
            try:
                async with session.get(url, ssl=False, timeout=timeout) as resp:
                    html = await resp.text(errors="ignore")
            except Exception as e:
                from app.utils.logger_util import get_logger
                logger = get_logger()
                logger.debug(f"Errors occurred while fetching and parse {url}: {e.__cause__}")
                return None

            parsed = parse_contacts(html)
            if parsed.get("phones") or parsed.get("socials"):
                return normalize_record({
                    "url": url,
                    "phones": parsed.get("phones") or [],
                    "socials": parsed.get("socials") or [],
                })
            return None

    tasks = [fetch_and_parse(url) for url in links]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        if result:
            return result

    return None
