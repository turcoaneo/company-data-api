# crawler/orchestrator.py

import asyncio
from typing import List, Dict

import aiohttp

from app.utils.env_vars import SCRAPER_CONFIG
from app.utils.logger_util import get_logger
from crawler.util.homepage_parser import parse_homepage
from crawler.util.scrape_links import scrape_links
from crawler.util.semantic_extractor import extract_semantic_links
from crawler.util.url_normalizer import resolve_homepage

logger = get_logger()


class CrawlerOrchestrator:
    def __init__(
        self,
        per_domain_concurrency: int = 5,
        timeout: int = 10,
        max_domains_in_parallel: int = 20,
    ):
        self.per_domain_concurrency = per_domain_concurrency
        self.max_domains_in_parallel = max_domains_in_parallel
        self.timeout = timeout

    # -------------------------
    # Crawl a single domain
    # -------------------------
    async def crawl_domain(
        self,
        session: aiohttp.ClientSession,
        domain: str
    ) -> Dict:

        logger.info(f"Starting crawl for domain: {domain}")

        # Normalize base
        base = domain.rstrip("/") if domain.startswith(("http://", "https://")) else f"https://{domain}".rstrip("/")

        # Phase 0: homepage must be reachable (with fallback)
        homepage_info = await resolve_homepage(session, base, self.timeout)
        if homepage_info is None:
            return {"result": None, "homepage_ok": False}

        homepage_html, working_base = homepage_info

        # Phase 1: parse homepage itself
        homepage_result = parse_homepage(working_base, homepage_html)
        initial = homepage_result

        semantic_links = extract_semantic_links(working_base, homepage_html)
        result = await scrape_links(session, semantic_links, self.timeout, self.per_domain_concurrency, working_base)

        if result:
            # merge homepage + semantic
            merged = {
                "url": result["url"],
                "phones": list({*initial["phones"], *result["phones"]}),
                "socials": list({*initial["socials"], *result["socials"]}),
            }
            return {"result": merged, "homepage_ok": True}

        # fallback to homepage-only if semantic pages fail
        if initial["phones"] or initial["socials"]:
            return {"result": initial, "homepage_ok": True}

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
        if SCRAPER_CONFIG["write_files"]:
            with open("bad_urls.txt", "w", encoding="utf-8") as f:
                for b in unreachable:
                    f.write(b + "\n")

        # Write reachable but missing contacts
        if SCRAPER_CONFIG["write_files"]:
            with open("missing_contacts.txt", "w", encoding="utf-8") as f:
                for b in missing_contacts:
                    f.write(b + "\n")

        return good
