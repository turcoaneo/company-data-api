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
    "/about.html", "/contact.html", "/contact_us.html", "/contactus.html",
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
        try:
            html = await self.fetcher.fetch_url(session, url)
            return html or ""
        except Exception as e:
            logger.error(f"Fetch error for {url}: {e}")
            return ""

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
    # Phase 0: homepage check WITH HTTP FALLBACK
    # -------------------------
    async def ensure_homepage(self, session: aiohttp.ClientSession, base: str) -> Optional[tuple]:
        domain = base.replace("https://", "").replace("http://", "").rstrip("/")

        https_url = f"https://{domain}"
        http_url = f"http://{domain}"

        # Try HTTPS first
        html = await self.fetch_html(session, https_url)
        if html:
            return html, https_url

        # Fallback to HTTP
        logger.warning(f"HTTPS failed for {domain}, retrying with HTTP: {http_url}")
        html = await self.fetch_html(session, http_url)
        if html:
            return html, http_url

        logger.error(f"Homepage unreachable via HTTPS and HTTP: {domain}")
        return None

    # -------------------------
    # Phase 1: priority pages WITH HTTP FALLBACK
    # -------------------------
    async def try_priority_pages(self, session: aiohttp.ClientSession, base: str) -> Optional[Dict]:
        # Try HTTPS/HTTP based on base
        tasks = [self.fetch_and_parse(session, urljoin(base, p)) for p in PRIORITY_PATHS]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result["phones"] or result["socials"]:
                logger.debug(f"Contacts found on PRIORITY page: {result['url']}")
                return normalize_record(result)

        return None

    # -------------------------
    # Phase 2: semantic link discovery
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
    # Phase 3: scrape semantic links WITH HTTP FALLBACK
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
    async def crawl_domain(
        self,
        session: aiohttp.ClientSession,
        domain: str
    ) -> Dict:

        logger.info(f"Starting crawl for domain: {domain}")

        base = domain.rstrip("/") if domain.startswith(("http://", "https://")) else f"https://{domain}".rstrip("/")

        # Phase 0: homepage must be reachable (with fallback)
        homepage_info = await self.ensure_homepage(session, base)
        homepage_ok = homepage_info is not None

        if not homepage_ok:
            return {"result": None, "homepage_ok": False}

        homepage_html, working_base = homepage_info

        # Phase 1: priority pages (using working_base)
        result = await self.try_priority_pages(session, working_base)
        if result:
            return {"result": result, "homepage_ok": True}

        # Phase 2: semantic links
        semantic_links = await self.discover_semantic_links(working_base, homepage_html)

        # Phase 3: scrape semantic links
        if SCRAPER_CONFIG["shallow_crawl"]:
            result = await self.scrape_semantic_links(session, semantic_links)
            if result:
                return {"result": result, "homepage_ok": True}

        return {"result": None, "homepage_ok": True}

    # -------------------------
    # Crawl many domains (parallel)
    # -------------------------
    async def crawl(self, domains: List[str]) -> List[Dict]:
        good: List[Dict] = []
        unreachable: List[str] = []
        missing_contacts: List[str] = []

        sem = asyncio.Semaphore(self.max_domains_in_parallel)

        async def crawl_guarded(domain: str):
            async with sem:
                async with aiohttp.ClientSession() as session:
                    return domain, await self.crawl_domain(session, domain)

        tasks = [asyncio.create_task(crawl_guarded(domain)) for domain in domains]

        for task in tasks:
            domain, info = await task
            result = info["result"]
            homepage_ok = info["homepage_ok"]

            if result:
                good.append(result)
            else:
                if not homepage_ok:
                    unreachable.append(domain)
                else:
                    missing_contacts.append(domain)

        # Write unreachable domains
        is_writable = SCRAPER_CONFIG["write_files"]
        if is_writable and unreachable:
            with open("bad_urls.txt", "w", encoding="utf-8") as f:
                for b in unreachable:
                    f.write(b + "\n")

        # Write reachable but missing contacts
        if is_writable and missing_contacts:
            with open("missing_contacts.txt", "w", encoding="utf-8") as f:
                for b in missing_contacts:
                    f.write(b + "\n")

        return good
