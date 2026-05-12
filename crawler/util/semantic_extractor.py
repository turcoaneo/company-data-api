# crawler/util/semantic_extractor.py

from urllib.parse import urljoin, urlparse

from selectolax.parser import HTMLParser

from .link_filters import is_semantic, is_garbage, is_low_signal, is_semantic_by_ancestry


def same_domain(a, b):
    a = urlparse(a).netloc.lower().lstrip("www.")
    b = urlparse(b).netloc.lower().lstrip("www.")
    return a == b


def extract_semantic_links(base: str, homepage_html: str):
    tree = HTMLParser(homepage_html)
    links = set()

    for a in tree.css("a"):
        href = a.attributes.get("href")
        if not href:
            continue

        full = urljoin(base, href)

        if not same_domain(full, base):
            continue
        if is_garbage(full):
            continue
        if is_low_signal(full):
            continue
        if is_semantic(full) or is_semantic_by_ancestry(a):
            links.add(full)

    return list(links)
