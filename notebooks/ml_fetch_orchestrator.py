# ============================================
# Orchestrator-based homepage fetcher for ML
# ============================================

import asyncio
import aiohttp
import random

from crawler.util.url_normalizer import resolve_homepage
from crawler.util.user_agents import USER_AGENTS


# -----------------------------------------
# Fetch homepage HTML using production logic
# -----------------------------------------

async def fetch_html_orchestrator(session, domain, timeout=10):
    """
    Fetch homepage HTML using the same logic as crawl_domain():
    - random User-Agent
    - slow-mode for Google Business Sites
    - resolve_homepage() fallback logic
    - SSL ignore, HTTP/HTTPS fallback
    - jitter
    """
    # Random UA like production
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    # Slow-mode for Google Business Sites
    slow_mode = (
            domain.endswith(".business.site")
            or "googleusercontent" in domain
    )

    # Jitter (same pattern as orchestrator)
    if slow_mode:
        await asyncio.sleep(random.uniform(0.3, 0.6))
    else:
        await asyncio.sleep(random.uniform(0.05, 0.15))

    # Normalize base URL
    base = (
        domain.rstrip("/")
        if domain.startswith(("http://", "https://"))
        else f"https://{domain}".rstrip("/")
    )

    try:
        homepage_info = await resolve_homepage(session, base, timeout, headers)
        if homepage_info is None:
            return ""

        homepage_html, working_base = homepage_info
        return homepage_html

    except Exception as e:
        print(f"[fetch_html_orchestrator] {domain} failed: {e}")
        return ""


# -----------------------------------------
# Fetch many domains in parallel
# -----------------------------------------

async def fetch_all_html_orchestrator(domains, timeout=10):
    connector = aiohttp.TCPConnector(
        limit=50,
        limit_per_host=5,
        ttl_dns_cache=600,
        ssl=False,  # orchestrator ignores SSL
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_html_orchestrator(session, d, timeout) for d in domains]
        return await asyncio.gather(*tasks)
