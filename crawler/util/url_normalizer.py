# crawler/util/url_normalizer.py

from app.utils.logger_util import get_logger

logger = get_logger()


async def resolve_homepage(session, base: str):
    """
    Returns (html, working_base_url) or None.
    Tries HTTPS → HTTP.
    """
    domain = base.replace("https://", "").replace("http://", "").rstrip("/")

    https_url = f"https://{domain}"
    http_url = f"http://{domain}"

    # Try HTTPS first
    html = await _fetch(session, https_url)
    if html:
        return html, https_url

    # Log the fallback
    logger.warning(f"HTTPS failed for {domain}, retrying with HTTP: {http_url}")

    html = await _fetch(session, http_url)
    if html:
        logger.info(f"Using HTTP for crawling: {http_url}")
        return html, http_url

    return None


async def _fetch(session, url: str):
    try:
        async with session.get(url, ssl=False) as resp:
            if resp.status < 400:
                return await resp.text(errors="ignore")
    except Exception as e:
        logger.debug(f"Errors occurred while fetching {url}: {e.__cause__}")
        return ""
    return ""
