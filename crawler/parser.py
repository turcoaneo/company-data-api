import re
from selectolax.parser import HTMLParser

PHONE_RE = re.compile(r"tel:([+0-9\- ]+)", re.I)
EMAIL_RE = re.compile(r"mailto:([^\"'>]+)", re.I)
SOCIAL_RE = re.compile(r"(facebook|linkedin|instagram|twitter|x\.com)", re.I)


def parse_contacts(html: str) -> dict:
    tree = HTMLParser(html)

    links = [n.attributes.get("href", "") for n in tree.css("a")]

    phones = [m.group(1).strip() for href in links if (m := PHONE_RE.search(href))]
    emails = [m.group(1).strip() for href in links if (m := EMAIL_RE.search(href))]
    socials = [href for href in links if SOCIAL_RE.search(href)]

    return {
        "phones": phones,
        "emails": emails,
        "socials": socials,
    }
