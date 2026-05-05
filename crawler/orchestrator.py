import asyncio
from urllib.parse import urljoin, urlparse
import aiohttp
import logging

from typing import List, Dict, Optional, Set

from .fetcher import Fetcher
from .parser import parse_contacts
from .pipeline import normalize_record

logger = logging.getLogger(__name__)

PRIORITY_PATHS = [
    "/", "/about", "/about-us", "/about us",
    "/contact", "/contact-us", "/contact us",
]


class CrawlerOrchestrator:
    def __init__(self, concurrency: int = 10, timeout: int = 10, max_pages: int = 30):
        self.concurrency = concurrency
        self.fetcher = Fetcher(timeout=timeout)
        self.max_pages = max_pages

    async def fetch_and_parse(self, session, url: str) -> Optional[Dict]:
        try:
            html = await self.fetcher.fetch(session, url)
            parsed = parse_contacts(html)
            return {"url": url, **parsed}
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    async def crawl_domain(self, session, domain: str) -> Optional[Dict]:
        logger.info(f"Starting crawl for domain: {domain}")
        if domain.startswith("http://") or domain.startswith("https://"):
            base = domain.rstrip("/")
        else:
            base = f"https://{domain}".rstrip("/")

        # -------------------------
        # Phase 1: priority pages
        # -------------------------
        for path in PRIORITY_PATHS:
            priority_url = urljoin(base, path)
            result = await self.fetch_and_parse(session, priority_url)
            if result and (result["phones"] or result["socials"]):
                return normalize_record(result)
            else:
                logger.warning(f"No contacts found in priority pages for {domain}")

        # -------------------------
        # Phase 2: full crawl
        # -------------------------
        to_visit: asyncio.Queue[str] = asyncio.Queue()
        visited: Set[str] = set()

        # seed with homepage
        await to_visit.put(base)

        results = []

        # FIX: we need HTML to extract links
        async def worker_with_links():
            while True:
                try:
                    url = await to_visit.get()
                except asyncio.CancelledError:
                    return

                if url in visited:
                    to_visit.task_done()
                    continue

                visited.add(url)

                try:
                    html = await self.fetcher.fetch(session, url)
                except Exception as e:
                    logging.error(f"Error fetching page {url}", exc_info=e)
                    to_visit.task_done()
                    continue

                parsed = parse_contacts(html)
                record = normalize_record({"url": url, **parsed})
                results.append(record)

                if record["phones"] or record["socials"]:
                    to_visit.task_done()
                    return

                # extract internal links
                from selectolax.parser import HTMLParser
                tree = HTMLParser(html)
                for a in tree.css("a"):
                    href = a.attributes.get("href", "")
                    if not href:
                        continue
                    full = urljoin(url, href)
                    if urlparse(full).netloc == urlparse(base).netloc:
                        if full not in visited and len(visited) < self.max_pages:
                            await to_visit.put(full)

                to_visit.task_done()

        workers = [asyncio.create_task(worker_with_links()) for _ in range(self.concurrency)]

        await to_visit.join()

        for w in workers:
            w.cancel()

        # return first good result
        for r in results:
            if r["phones"] or r["socials"]:
                return r

        return None

    async def crawl(self, domains: List[str]) -> List[Dict]:
        good = []
        bad = []

        async with aiohttp.ClientSession() as session:
            for domain in domains:
                result = await self.crawl_domain(session, domain)
                if result:
                    good.append(result)
                else:
                    bad.append(domain)

        # write bad URLs
        if bad:
            with open("bad_urls.txt", "w", encoding="utf-8") as f:
                for b in bad:
                    f.write(b + "\n")

        return good
