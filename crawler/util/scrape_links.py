# crawler/util/scrape_links.py

import asyncio
import random
from urllib.parse import urlparse

from app.utils.logger_util import get_logger
from crawler.parser import parse_contacts
from crawler.pipeline import normalize_record
from crawler.util.fetch_fast import fetch_fast
from crawler.util.fetch_with_retries import fetch_with_retries

logger = get_logger()


def _is_same_domain(url: str, base_domain: str) -> bool:
    if not url:
        return False

    url = url.strip().lower()
    if not (url.startswith("http://") or url.startswith("https://")):
        return False

    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    domain_name = urlparse(base_domain).netloc.lower()
    return host == domain_name


async def scrape_links(
    session,
    links,
    timeout,
    concurrency,
    base_domain,
    headers: dict = None,
    slow_mode: bool = False
):
    headers = headers or {}

    if not links:
        return None

    links = [u for u in links if _is_same_domain(u, base_domain)]
    if not links:
        return None

    sem = asyncio.Semaphore(concurrency)

    # noinspection DuplicatedCode
    async def fetch_and_parse(url: str):
        async with sem:

            # Jitter
            if slow_mode:
                await asyncio.sleep(random.uniform(0.3, 0.6))
            else:
                await asyncio.sleep(random.uniform(0.05, 0.15))

            # --- FAST PATH ---
            ok, status, html = await fetch_fast(session, url, timeout, headers=headers)
            html_len = len(html or "") if html is not None else 0
            logger.debug(f"scrape_links fast attempt for {url}: ok={ok}, status={status}, html_len={html_len}")

            # Retry on tiny-body 200
            if ok and status == 200 and 0 < html_len < 2000:
                logger.warning(f"Suspicious tiny-body 200 for {url} (len={html_len}), retrying once...")
                await asyncio.sleep(random.uniform(0.2, 0.5))
                ok2, status2, html2 = await fetch_fast(session, url, timeout, headers=headers)
                html_len2 = len(html2 or "") if html2 is not None else 0
                logger.debug(f"scrape_links retry for {url}: ok={ok2}, status={status2}, html_len={html_len2}")
                if ok2 and status2 == 200 and html_len2 >= 2000:
                    return parse_and_normalize(url, html2)

            if ok and status < 400:
                return parse_and_normalize(url, html)

            # --- RETRY ONLY ON 403 ---
            if status == 403:
                logger.debug(f"scrape_links 403 for {url}, entering fetch_with_retries")
                retry = await fetch_with_retries(session, url, timeout, headers=headers)
                if retry["ok"]:
                    html_r = retry["html"]
                    logger.debug(f"scrape_links fetch_with_retries success for {url}, html_len={len(html_r or '')}")
                    return parse_and_normalize(url, html_r)

            return None

    def parse_and_normalize(url, html):
        parsed = parse_contacts(html or "")
        phones = parsed.get("phones") or []
        socials = parsed.get("socials") or []

        if socials and not phones:
            logger.debug(f"Socials but no phones on {url} (html_len={len(html or '')})")

        if phones and not socials:
            logger.debug(f"Phones but no socials on {url} (html_len={len(html or '')})")

        if phones or socials:
            return normalize_record({
                "url": url,
                "phones": phones,
                "socials": socials,
            })
        return None

    tasks = [fetch_and_parse(url) for url in links]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        if result:
            return result

    return None
