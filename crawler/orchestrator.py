# crawler/orchestrator.py

import asyncio
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse

import aiohttp

from app.utils.logger_util import get_logger
from .fetcher import Fetcher
from .parser import parse_contacts
from .pipeline import normalize_record

logger = get_logger()

PRIORITY_PATHS = [
    "/", "/about", "/about-us", "/about_us", "/aboutus",
    "/contact", "/contact-us", "/contact_us", "/contactus",
]


class CrawlerOrchestrator:
    def __init__(self, concurrency: int = 10, timeout: int = 10, max_pages: int = 30):
        self.concurrency = concurrency
        self.fetcher = Fetcher(timeout=timeout)
        self.max_pages = max_pages

    async def fetch_and_parse(self, session, url: str) -> Optional[Dict]:
        try:
            html = await self.fetcher.fetch_url(session, url)

            # If fetch failed → html = "" → safe fallback
            if not html:
                return {
                    "url": url,
                    "phones": [],
                    "emails": [],
                    "socials": [],
                }

            parsed = parse_contacts(html)

            # Ensure parsed fields exist and are lists
            return {
                "url": url,
                "phones": parsed.get("phones") or [],
                "emails": parsed.get("emails") or [],
                "socials": parsed.get("socials") or [],
            }

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return {
                "url": url,
                "phones": [],
                "emails": [],
                "socials": [],
            }

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

                # Fetch HTML safely
                html = await self.fetcher.fetch_url(session, url)

                if not html:
                    record = normalize_record({"url": url, "phones": [], "emails": [], "socials": []})
                else:
                    parsed = parse_contacts(html)
                    record = normalize_record({
                        "url": url,
                        "phones": parsed.get("phones") or [],
                        "emails": parsed.get("emails") or [],
                        "socials": parsed.get("socials") or [],
                    })

                results.append(record)

                # EARLY STOP: if we found contacts, stop all workers
                if record["phones"] or record["socials"]:
                    to_visit.task_done()
                    # Clear queue so join() finishes immediately
                    while not to_visit.empty():
                        try:
                            to_visit.get_nowait()
                            to_visit.task_done()
                        except Exception as e:
                            logger.debug(e)
                            break
                    return

                # No contacts → extract internal links (filtered)
                if html:
                    from selectolax.parser import HTMLParser
                    tree = HTMLParser(html)

                    links_added = 0
                    for a in tree.css("a"):
                        if links_added >= 10:  # limit links per page
                            break

                        href = a.attributes.get("href", "")
                        if not href:
                            continue

                        # FILTER GARBAGE LINKS
                        if any(href.lower().endswith(ext) for ext in [
                            ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
                            ".zip", ".rar", ".mp4", ".avi", ".mov", ".docx", ".xlsx"
                        ]):
                            continue

                        if any(bad in href.lower() for bad in [
                            "calendar", "events", "blog", "news", "feed",
                            "wp-json", "tag", "category", "product", "shop",
                            "portfolio", "gallery", "media", "uploads"
                        ]):
                            continue

                        full = urljoin(url, href)

                        # Only internal links
                        if urlparse(full).netloc != urlparse(base).netloc:
                            continue

                        if full not in visited and len(visited) < self.max_pages:
                            await to_visit.put(full)
                            links_added += 1

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
