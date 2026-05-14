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
            domain_concurrency: int = None,
            domains_in_parallel: int = None,
            timeout: int = 10,
    ):
        self.domain_concurrency = domain_concurrency if domain_concurrency else SCRAPER_CONFIG["domain_concurrency"]
        self.domains_in_parallel = domains_in_parallel if domains_in_parallel else SCRAPER_CONFIG["domains_in_parallel"]
        self.timeout = timeout

    async def crawl_domain(
            self,
            session: aiohttp.ClientSession,
            domain: str,
            headers: dict = None,
            slow_mode: bool = False
    ) -> Dict:

        headers = headers or {}

        import random
        if slow_mode:
            await asyncio.sleep(random.uniform(0.3, 0.6))
        else:
            await asyncio.sleep(random.uniform(0.05, 0.15))

        logger.info(f"Starting crawl for domain: {domain}")

        # Normalize base
        base = domain.rstrip("/") if domain.startswith(("http://", "https://")) else f"https://{domain}".rstrip("/")

        # Phase 0: homepage must be reachable (with fallback)
        homepage_info = await resolve_homepage(session, base, self.timeout, headers)
        if homepage_info is None:
            return {"result": None, "homepage_ok": False}

        homepage_html, working_base = homepage_info

        # Phase 1: parse homepage itself
        homepage_result = parse_homepage(working_base, homepage_html)
        initial = homepage_result

        semantic_links = extract_semantic_links(working_base, homepage_html)
        result = await scrape_links(session, semantic_links, self.timeout, self.domain_concurrency, working_base,
                                    headers)

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
    # Crawl a single domain
    # -------------------------

    async def crawl(self, domains: List[str]) -> List[Dict]:
        import random
        from crawler.util.user_agents import USER_AGENTS

        good: List[Dict] = []
        unreachable: List[str] = []
        missing_contacts: List[str] = []

        sem = asyncio.Semaphore(self.domains_in_parallel)

        # Shared connector for connection reuse
        connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)

        async with aiohttp.ClientSession(connector=connector) as shared_session:

            async def crawl_guarded(domain: str):
                async with sem:
                    # Pick UA per domain
                    headers = {"User-Agent": random.choice(USER_AGENTS)}

                    # Slow-mode for Google Business Sites
                    slow_mode = (
                            domain.endswith(".business.site")
                            or "googleusercontent" in domain
                    )

                    return domain, await self.crawl_domain(
                        shared_session,
                        domain,
                        headers=headers,
                        slow_mode=slow_mode
                    )

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

        # Append unreachable
        if SCRAPER_CONFIG["write_files"]:
            with open("bad_urls.txt", "a", encoding="utf-8") as f:
                for b in unreachable:
                    f.write(b + "\n")

        # Append missing contacts
        if SCRAPER_CONFIG["write_files"]:
            with open("missing_contacts.txt", "a", encoding="utf-8") as f:
                for b in missing_contacts:
                    f.write(b + "\n")

        return good
    # -------------------------
    # Crawl many domains (parallel)
    # -------------------------
