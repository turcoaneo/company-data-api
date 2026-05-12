# crawler/util/text_phone_extractor.py

from selectolax.parser import HTMLParser

from crawler.util.phone_normalizer import dedupe_and_normalize_phones
from crawler.util.phone_re import TEXT_PHONE_RE

ALLOWED_TAGS = {
    "p", "span", "div", "li", "a",
    "strong", "em", "b", "i", "small",
    "h1", "h2", "h3", "h4", "h5", "h6"
}


def extract_visible_text(dom: HTMLParser):
    texts = []

    for node in dom.root.traverse():
        # Only extract from allowed content tags
        if node.tag not in ALLOWED_TAGS:
            continue

        # 1. Text directly inside this node
        if node.text():
            for part in node.text().split("\n"):
                part = part.strip()
                if part:
                    texts.append(part)

        # 2. Handle <br> inside this node
        # Selectolax does not expose children list, so we scan siblings
        child = node.child
        while child:
            if child.tag == "br":
                # text immediately after <br> is in next sibling
                nxt = child.next
                if nxt and nxt.text():
                    for part in nxt.text().split("\n"):
                        part = part.strip()
                        if part:
                            texts.append(part)
            child = child.next

    return texts


def extract_text_phones(dom: HTMLParser):
    texts = extract_visible_text(dom)
    candidates = []

    for t in texts:
        for match in TEXT_PHONE_RE.findall(t):
            candidates.append(match.strip())

    return dedupe_and_normalize_phones(candidates)
