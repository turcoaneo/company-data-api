# crawler/util/url_normalizer.py

from typing import Optional, Tuple
import asyncio
import random

from app.utils.logger_util import get_logger
from crawler.util.fetch_fast import fetch_fast
from crawler.util.fetch_with_retries import fetch_with_retries

logger = get_logger()


async def resolve_homepage(
    session,
    base: str,
    timeout: int,
    headers: dict = None,
    slow_mode: bool = False
):

    """
    Try HTTPS fast, retry on 403, then HTTP fast, retry on 403.
    Adds jitter, retry on tiny-body 200, and slow-mode support.
    Returns (html, working_base) or None.
    """

    domain = base.replace("https://", "").replace("http://", "").rstrip("/")

    https_url = f"https://{domain}"
    http_url = f"http://{domain}"

    async def _attempt(url: str):
        # Slow-mode jitter
        if slow_mode:
            await asyncio.sleep(random.uniform(0.3, 0.6))
        else:
            await asyncio.sleep(random.uniform(0.05, 0.15))

        ok, status, html = await fetch_fast(session, url, timeout, headers=headers)

        # Retry on tiny-body 200 (Google Business Sites throttling)
        if ok and status == 200 and html and len(html) < 2000:
            await asyncio.sleep(random.uniform(0.2, 0.5))
            ok2, status2, html2 = await fetch_fast(session, url, timeout, headers=headers)
            if ok2 and status2 == 200 and html2 and len(html2) >= 2000:
                return True, status2, html2

        return ok, status, html

    # --- Try HTTPS fast ---
    ok, status, html = await _attempt(https_url)
    if ok and status < 400:
        return html or "", https_url

    # --- Retry HTTPS only if 403 ---
    if status == 403:
        retry = await fetch_with_retries(session, https_url, timeout, headers=headers)
        if retry["ok"]:
            return retry["html"] or "", https_url

    # --- Try HTTP fast ---
    ok, status, html = await _attempt(http_url)
    if ok and status < 400:
        return html or "", http_url

    # --- Retry HTTP only if 403 ---
    if status == 403:
        retry = await fetch_with_retries(session, http_url, timeout, headers=headers)
        if retry["ok"]:
            return retry["html"] or "", http_url

    return None
