# crawler/util/url_normalizer.py

from typing import Optional, Tuple
import asyncio
import random

from app.utils.logger_util import get_logger
from crawler.util.fetch_fast import fetch_fast
from crawler.util.fetch_with_retries import fetch_with_retries

logger = get_logger()


# noinspection DuplicatedCode
async def resolve_homepage(
    session,
    base: str,
    timeout: int,
    headers: dict = None,
    slow_mode: bool = False
) -> Optional[Tuple[str, str]]:
    """
    Try HTTPS fast, retry on 403, then HTTP fast, retry on 403.
    Adds jitter, retry on tiny-body 200, and logging for suspicious HTML.
    Returns (html, working_base) or None.
    """
    headers = headers or {}

    domain = base.replace("https://", "").replace("http://", "").rstrip("/")

    https_url = f"https://{domain}"
    http_url = f"http://{domain}"

    # noinspection DuplicatedCode
    async def _attempt(url: str):
        # Slow-mode jitter
        if slow_mode:
            await asyncio.sleep(random.uniform(0.3, 0.6))
        else:
            await asyncio.sleep(random.uniform(0.05, 0.15))

        ok_attempt, status_attempt, html_attempt = await fetch_fast(session, url, timeout, headers=headers)
        html_len = len(html_attempt or "") if html_attempt is not None else 0

        logger.debug(
            f"resolve_homepage fast attempt for {url}: ok={ok_attempt}, status={status_attempt},html_len={html_len}")

        # Retry on tiny-body 200 (suspicious)
        if ok_attempt and status_attempt == 200 and 0 < html_len < 2000:
            logger.warning(f"Suspicious tiny-body 200 for {url} (len={html_len}), retrying once...")
            await asyncio.sleep(random.uniform(0.2, 0.5))
            ok2, status2, html2 = await fetch_fast(session, url, timeout, headers=headers)
            html_len2 = len(html2 or "") if html2 is not None else 0
            logger.debug(f"resolve_homepage retry for {url}: ok={ok2}, status={status2}, html_len={html_len2}")
            if ok2 and status2 == 200 and html_len2 >= 2000:
                return True, status2, html2

        return ok_attempt, status_attempt, html_attempt

    # --- Try HTTPS fast ---
    ok, status, html = await _attempt(https_url)
    if ok and status < 400:
        logger.debug(f"Resolved homepage via HTTPS: {https_url}, html_len={len(html or '')}")
        return html or "", https_url

    # --- Retry HTTPS only if 403 ---
    if status == 403:
        logger.debug(f"HTTPS 403 for {https_url}, entering fetch_with_retries")
        retry = await fetch_with_retries(session, https_url, timeout, headers=headers)
        if retry["ok"]:
            logger.debug(f"fetch_with_retries HTTPS success for {https_url}, html_len={len(retry['html'] or '')}")
            return retry["html"] or "", https_url

    # --- Try HTTP fast ---
    ok, status, html = await _attempt(http_url)
    if ok and status < 400:
        logger.debug(f"Resolved homepage via HTTP: {http_url}, html_len={len(html or '')}")
        return html or "", http_url

    # --- Retry HTTP only if 403 ---
    if status == 403:
        logger.debug(f"HTTP 403 for {http_url}, entering fetch_with_retries")
        retry = await fetch_with_retries(session, http_url, timeout, headers=headers)
        if retry["ok"]:
            logger.debug(f"fetch_with_retries HTTP success for {http_url}, html_len={len(retry['html'] or '')}")
            return retry["html"] or "", http_url

    logger.warning(f"Failed to resolve homepage for {base}")
    return None
