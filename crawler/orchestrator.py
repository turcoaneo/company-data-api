# crawler/orchestrator.py

import asyncio
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

import aiohttp

from app.utils.env_vars import SCRAPER_CONFIG
from app.utils.logger_util import get_logger
from app.utils.timing_util import elapsed_time
from .fetcher import Fetcher
from .parser import parse_contacts
from .pipeline import normalize_record

logger = get_logger()

PRIORITY_PATHS = [
    "/", "/about", "/about-us", "/about_us", "/aboutus",
    "/contact", "/contact-us", "/contact_us", "/contactus",
]

SEMANTIC_KEYWORDS = [
    "about", "contact", "team", "leadership", "staff",
    "who-we-are", "company", "info", "support",
]

GARBAGE_EXT = [
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".zip", ".rar", ".mp4", ".avi", ".mov", ".docx", ".xlsx",
]

LOW_SIGNAL = [
    "calendar", "events", "blog", "news", "feed",
    "wp-json", "tag", "category", "product", "shop",
    "portfolio", "gallery", "media", "uploads",
]


def is_semantic_link(href: str) -> bool:
    href_lower = href.lower()
    return any(key in href_lower for key in SEMANTIC_KEYWORDS)


def is_garbage(href: str) -> bool:
    href_lower = href.lower()
    return any(href_lower.endswith(ext) for ext in GARBAGE_EXT)


def is_low_signal(href: str) -> bool:
    href_lower = href.lower()
    return any(bad in href_lower for bad in LOW_SIGNAL)


class CrawlerOrchestrator:
    def __init__(
        self,
        per_domain_concurrency: int = 5,
        timeout: int = 10,
        max_domains_in_parallel: int = 20,
    ):
        self.per_domain_concurrency = per_domain_concurrency
        self.max_domains_in_parallel = max_domains_in_parallel
        self.fetcher = Fetcher(timeout=timeout)

    # -------------------------
    # Fetch only
    # -------------------------
    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> str:
        html = await self.fetcher.fetch_url(session, url)
        return html or ""

    # -------------------------
    # Parse only (emails removed)
    # -------------------------
    @staticmethod
    def parse_html(url: str, html: str) -> Dict:
        if not html:
            return {"url": url, "phones": [], "socials": []}

        parsed = parse_contacts(html)
        return {
            "url": url,
            "phones": parsed.get("phones") or [],
            "socials": parsed.get("socials") or [],
        }

    # -------------------------
    # Fetch + parse
    # -------------------------
    async def fetch_and_parse(self, session: aiohttp.ClientSession, url: str) -> Dict:
        html = await self.fetch_html(session, url)
        return self.parse_html(url, html)

    # -------------------------
    # Phase 0: homepage check
    # -------------------------
    async def ensure_homepage(self, session: aiohttp.ClientSession, base: str) -> Optional[str]:
        html = await self.fetch_html(session, base)
        if not html:
            logger.error(f"Homepage unreachable, skipping domain: {base}")
            return None
        return html

    # -------------------------
    # Phase 1: priority pages (parallel)
    # -------------------------
    async def try_priority_pages(self, session: aiohttp.ClientSession, base: str) -> Optional[Dict]:
        tasks = [self.fetch_and_parse(session, urljoin(base, p)) for p in PRIORITY_PATHS]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result["phones"] or result["socials"]:
                logger.debug(f"Contacts found on PRIORITY page: {result['url']}")
                return normalize_record(result)

        return None

    # -------------------------
    # Phase 2: semantic link discovery (homepage only)
    # -------------------------
    @elapsed_time("semantic_discovery")
    async def discover_semantic_links(
        self,
        base: str,
        homepage_html: str,
    ) -> List[str]:
        from selectolax.parser import HTMLParser

        tree = HTMLParser(homepage_html)
        links = set()

        for a in tree.css("a"):
            href = a.attributes.get("href")
            if not href:
                continue

            full = urljoin(base, href)

            # internal only
            if urlparse(full).netloc != urlparse(base).netloc:
                continue

            if is_garbage(full):
                continue

            if is_low_signal(full):
                continue

            if is_semantic_link(full):
                links.add(full)

        return list(links)

    # -------------------------
    # Phase 3: scrape semantic links (parallel)
    # -------------------------
    async def scrape_semantic_links(
        self,
        session: aiohttp.ClientSession,
        links: List[str],
    ) -> Optional[Dict]:
        if not links:
            return None

        sem = asyncio.Semaphore(self.per_domain_concurrency)

        async def guarded_fetch(url: str) -> Dict:
            async with sem:
                return await self.fetch_and_parse(session, url)

        tasks = [guarded_fetch(url) for url in links]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result["phones"] or result["socials"]:
                logger.debug(f"Contacts found on SEMANTIC link: {result['url']}")
                return normalize_record(result)

        return None

    # -------------------------
    # Crawl a single domain
    # -------------------------
    async def crawl_domain(self, session: aiohttp.ClientSession, domain: str) -> Optional[Dict]:
        logger.info(f"Starting crawl for domain: {domain}")

        base = domain.rstrip("/") if domain.startswith(("http://", "https://")) else f"https://{domain}".rstrip("/")

        # Phase 0: homepage must be reachable
        homepage_html = await self.ensure_homepage(session, base)
        if homepage_html is None:
            return None

        # Phase 1: priority pages
        result = await self.try_priority_pages(session, base)
        if result:
            return result

        # Phase 2: semantic links from homepage
        semantic_links = await self.discover_semantic_links(base, homepage_html)

        # Phase 3: scrape semantic links (only if shallow_crawl enabled)
        if SCRAPER_CONFIG["shallow_crawl"]:
            result = await self.scrape_semantic_links(session, semantic_links)
            if result:
                return result

        return None

    # -------------------------
    # Crawl many domains (parallel)
    # -------------------------
    async def crawl(self, domains: List[str]) -> List[Dict]:
        good: List[Dict] = []
        bad: List[str] = []

        sem = asyncio.Semaphore(self.max_domains_in_parallel)

        async def crawl_guarded(domain: str) -> Optional[Dict]:
            async with sem:
                async with aiohttp.ClientSession() as session:
                    return await self.crawl_domain(session, domain)

        tasks = {domain: asyncio.create_task(crawl_guarded(domain)) for domain in domains}

        for domain, task in tasks.items():
            try:
                result = await task
            except Exception as e:
                logger.error(f"Unhandled error while crawling {domain}: {e}")
                result = None

            if result:
                good.append(result)
            else:
                bad.append(domain)

        if bad:
            with open("bad_urls.txt", "w", encoding="utf-8") as f:
                for b in bad:
                    f.write(b + "\n")

        return good
