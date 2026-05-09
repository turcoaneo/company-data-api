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
has_shallow_crawl = SCRAPER_CONFIG["shallow_crawl"]

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
    ".zip", ".rar", ".mp4", ".avi", ".mov", ".docx", ".xlsx"
]

LOW_SIGNAL = [
    "calendar", "events", "blog", "news", "feed",
    "wp-json", "tag", "category", "product", "shop",
    "portfolio", "gallery", "media", "uploads"
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
    def __init__(self, concurrency: int = 10, timeout: int = 10):
        self.concurrency = concurrency
        self.fetcher = Fetcher(timeout=timeout)

    # -------------------------
    # Fetch only
    # -------------------------
    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> str:
        try:
            html = await self.fetcher.fetch_url(session, url)
            return html or ""
        except Exception as e:
            logger.error(f"Fetch error for {url}: {e}")
            return ""

    # -------------------------
    # Parse only
    # -------------------------
    @staticmethod
    def parse_html(url: str, html: str) -> Dict:
        if not html:
            return {"url": url, "phones": [], "emails": [], "socials": []}

        parsed = parse_contacts(html)
        return {
            "url": url,
            "phones": parsed.get("phones") or [],
            "emails": parsed.get("emails") or [],
            "socials": parsed.get("socials") or [],
        }

    # -------------------------
    # Fetch + parse
    # -------------------------
    async def fetch_and_parse(self, session: aiohttp.ClientSession, url: str) -> Dict:
        html = await self.fetch_html(session, url)
        return self.parse_html(url, html)

    # -------------------------
    # Phase 1: priority pages (parallel)
    # -------------------------
    @elapsed_time("priority-pages")
    async def try_priority_pages(self, session, base: str) -> Optional[Dict]:
        tasks = [self.fetch_and_parse(session, urljoin(base, p)) for p in PRIORITY_PATHS]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result["phones"] or result["socials"]:
                return normalize_record(result)

        return None

    # -------------------------
    # Phase 2: semantic link discovery
    # -------------------------
    @elapsed_time("semantic_discovery")
    async def discover_semantic_links(self, session, base: str) -> List[str]:
        html = await self.fetch_html(session, base)
        if not html:
            return []

        from selectolax.parser import HTMLParser
        tree = HTMLParser(html)

        links = set()

        for a in tree.css("a"):
            href = a.attributes.get("href", "")
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
    async def scrape_semantic_links(self, session, links: List[str]) -> Optional[Dict]:
        tasks = [self.fetch_and_parse(session, url) for url in links]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result["phones"] or result["socials"]:
                return normalize_record(result)

        return None

    # -------------------------
    # Crawl a single domain
    # -------------------------
    async def crawl_domain(self, session, domain: str) -> Optional[Dict]:
        logger.info(f"Starting crawl for domain: {domain}")

        base = domain.rstrip("/") if domain.startswith(("http://", "https://")) else f"https://{domain}".rstrip("/")

        # Phase 1: priority pages
        result = await self.try_priority_pages(session, base)
        if result:
            return result

        # Phase 2: semantic link discovery
        if has_shallow_crawl:
            semantic_links = await self.discover_semantic_links(session, base)

            # Phase 3: scrape semantic links
            if semantic_links:
                result = await self.scrape_semantic_links(session, semantic_links)
                if result:
                    return result

        return None

    # -------------------------
    # Crawl many domains
    # -------------------------
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

        if bad:
            with open("bad_urls.txt", "w", encoding="utf-8") as f:
                for b in bad:
                    f.write(b + "\n")

        return good
