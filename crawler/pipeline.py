# crawler/pipeline.py

from urllib.parse import urlparse

from crawler.util.phone_normalizer import dedupe_and_normalize_phones


def normalize_record(record):
    """
    Ensure phones, socials are normalized and always lists.
    """

    # Phones
    raw_phones = record.get("phones") or []
    record["phones"] = dedupe_and_normalize_phones(raw_phones, default_country="+1")

    # Socials
    raw_socials = record.get("socials") or []
    record["socials"] = list({s.strip() for s in raw_socials})

    return record


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
