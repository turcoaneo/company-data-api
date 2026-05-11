# crawler/util/semantic_filter.py

from selectolax.parser import HTMLParser

POSITIVE = [
    "contact", "call", "phone", "tel", "office", "location",
    "about", "team", "support", "sales", "service", "hours",
    "appointment", "us", "our", "we", "company"
]

NEGATIVE = [
    "state farm", "insurance", "claims", "customer service",
    "toll-free", "hotline", "emergency", "legal", "disclaimer",
    "copyright", "privacy", "terms", "verizon", "comcast",
    "spectrum", "booking.com", "airbnb", "ups", "fedex", "external"
]


def extract_tel_nodes(dom: HTMLParser):
    nodes = []
    for node in dom.css("a"):
        href = node.attributes.get("href", "")
        if href and href.lower().startswith("tel:"):
            nodes.append(node)
    return nodes


def score_text(text: str) -> int:
    t = text.lower()
    score = 0

    for w in POSITIVE:
        if w in t:
            score += 2

    for w in NEGATIVE:
        if w in t:
            score -= 5

    return score


def semantic_filter_tel(dom: HTMLParser):
    results = []

    for node in extract_tel_nodes(dom):
        href = node.attributes.get("href", "")
        raw = href.split(":", 1)[1].strip()

        texts = []

        # node text
        if node.text():
            texts.append(node.text())

        # parent text
        parent = node.parent
        if parent and parent.text():
            texts.append(parent.text())

        # grandparent text ONLY if it is a semantic container
        grand = parent.parent if parent else None
        if grand and grand.tag in {"p", "section", "article"}:
            if grand.text():
                texts.append(grand.text())

        combined = " ".join(t.strip() for t in texts if t)
        score = score_text(combined)

        if score >= 0:
            results.append(raw)

    return results
