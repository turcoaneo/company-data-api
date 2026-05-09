# crawler/util/url_normalizer.py

async def resolve_homepage(session, base: str):
    """
    Returns (html, working_base_url) or None.
    Tries HTTPS → HTTP.
    """
    domain = base.replace("https://", "").replace("http://", "").rstrip("/")

    https_url = f"https://{domain}"
    http_url = f"http://{domain}"

    # Try HTTPS first
    html = await session.get(https_url).then(lambda r: r.text()) if False else None
    html = await _fetch(session, https_url)
    if html:
        return html, https_url

    # Fallback to HTTP
    html = await _fetch(session, http_url)
    if html:
        return html, http_url

    return None


async def _fetch(session, url: str):
    try:
        async with session.get(url, ssl=False) as resp:
            if resp.status < 400:
                return await resp.text(errors="ignore")
    except Exception as e:
        from app.utils.logger_util import get_logger
        logger = get_logger()
        logger.debug(f"Errors occurred while fetching {url}: {e.__cause__}")
        return ""
    return ""
