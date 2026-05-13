# crawler/util/scrape_links.py

import asyncio

from app.utils.logger_util import get_logger
from crawler.parser import parse_contacts
from crawler.pipeline import normalize_record
from crawler.util.fetch_fast import fetch_fast
from crawler.util.fetch_with_retries import fetch_with_retries

logger = get_logger()

from urllib.parse import urlparse


def _is_same_domain(url: str, base_domain: str) -> bool:
    """
    Return True only if url belongs to the same domain.
    """
    if not url:
        return False

    url = url.strip().lower()

    # Must be http(s)
    if not (url.startswith("http://") or url.startswith("https://")):
        return False

    host = urlparse(url).netloc.lower()

    # Strip www.
    if host.startswith("www."):
        host = host[4:]

    domain_name = urlparse(base_domain).netloc.lower()
    return host == domain_name


async def scrape_links(session, links, timeout, concurrency, base_domain):
    if not links:
        return None

    # Filter out mailto:, tel:, javascript:, anchors, etc.
    links = [u for u in links if _is_same_domain(u, base_domain)]
    if not links:
        return None

    sem = asyncio.Semaphore(concurrency)

    async def fetch_and_parse(url: str):
        async with sem:
            # --- FAST PATH ---
            ok, status, html = await fetch_fast(session, url, timeout)

            if ok and status < 400:
                return parse_and_normalize(url, html)

            # --- RETRY ONLY ON 403 ---
            if status == 403:
                retry = await fetch_with_retries(session, url, timeout)
                if retry["ok"]:
                    return parse_and_normalize(url, retry["html"])

            return None

    def parse_and_normalize(url, html):
        parsed = parse_contacts(html or "")
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
