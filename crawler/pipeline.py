# crawler/pipeline.py

from urllib.parse import urlparse


def normalize_record(record: dict) -> dict:
    """
    Ensure scraper output always contains phones, emails, socials as lists.
    """
    return {
        "url": record.get("url"),
        "phones": record.get("phones") or [],
        "emails": record.get("emails") or [],
        "socials": record.get("socials") or [],
    }


def normalize_domain(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.strip().lower()

    if "://" not in url:
        return url.rstrip("/")

    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    host = host.lstrip("/")  # <— strip leading slash for path-only cases
    return host.rstrip("/")
