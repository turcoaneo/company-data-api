# crawler/util/url_normalizer.py

from typing import Optional, Tuple

from app.utils.logger_util import get_logger
from crawler.util.fetch_fast import fetch_fast
from crawler.util.fetch_with_retries import fetch_with_retries

logger = get_logger()


async def resolve_homepage(session, base: str, timeout: int) -> Optional[Tuple[str, str]]:
    """
    Try HTTPS fast, retry on 403, then HTTP fast, retry on 403.
    Returns (html, working_base) or None.
    """

    domain = base.replace("https://", "").replace("http://", "").rstrip("/")

    https_url = f"https://{domain}"
    http_url = f"http://{domain}"

    # --- Try HTTPS fast ---
    ok, status, html = await fetch_fast(session, https_url, timeout)
    if ok and status < 400:
        return html or "", https_url

    # --- Retry HTTPS only if 403 ---
    if status == 403:
        retry = await fetch_with_retries(session, https_url, timeout)
        if retry["ok"]:
            return retry["html"] or "", https_url

    # --- Try HTTP fast ---
    ok, status, html = await fetch_fast(session, http_url, timeout)
    if ok and status < 400:
        return html or "", http_url

    # --- Retry HTTP only if 403 ---
    if status == 403:
        retry = await fetch_with_retries(session, http_url, timeout)
        if retry["ok"]:
            return retry["html"] or "", http_url

    return None
