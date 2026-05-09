# crawler/util/homepage_parser.py

from crawler.parser import parse_contacts


def parse_homepage(url: str, html: str):
    parsed = parse_contacts(html)
    return {
        "url": url,
        "phones": parsed.get("phones") or [],
        "socials": parsed.get("socials") or [],
    }
