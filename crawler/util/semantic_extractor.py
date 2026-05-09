# crawler/util/semantic_extractor.py

from urllib.parse import urljoin, urlparse
from selectolax.parser import HTMLParser
from .link_filters import is_semantic, is_garbage, is_low_signal


def extract_semantic_links(base: str, homepage_html: str):
    tree = HTMLParser(homepage_html)
    links = set()

    for a in tree.css("a"):
        href = a.attributes.get("href")
        if not href:
            continue

        full = urljoin(base, href)

        if urlparse(full).netloc != urlparse(base).netloc:
            continue
        if is_garbage(full):
            continue
        if is_low_signal(full):
            continue
        if is_semantic(full):
            links.add(full)

    return list(links)
