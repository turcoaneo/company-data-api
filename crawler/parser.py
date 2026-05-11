# /crawler/parser.py

import logging

from selectolax.parser import HTMLParser

from .socials import extract_social_links
from .util.phone_normalizer import dedupe_and_normalize_phones
from .util.text_phone_extractor import extract_text_phones

logger = logging.getLogger(__name__)


class Parser:

    @staticmethod
    def parse_tel_links(hrefs):
        phones = []
        for href in hrefs:
            if not href:
                continue
            h = href.lower()
            if h.startswith("tel:"):
                phones.append(h.split(":", 1)[1].strip())
        return dedupe_and_normalize_phones(phones)

    @staticmethod
    def parse_text_phones(html: str):
        tree = HTMLParser(html)
        phones = extract_text_phones(tree)
        logger.debug(f"Text phones extracted: {phones}")
        return dedupe_and_normalize_phones(phones)

    @staticmethod
    def parse_socials(tree):
        socials = extract_social_links(tree)
        logger.debug(f"Social links extracted: {socials}")
        return socials

    @staticmethod
    def merge_unique(values):
        seen = set()
        result = []
        for v in values:
            if v not in seen:
                seen.add(v)
                result.append(v)
        return result


def parse_contacts(html: str) -> dict:
    tree = HTMLParser(html)

    hrefs = [
        (n.attributes.get("href") or "").strip()
        for n in tree.css("a")
        if n.attributes.get("href") is not None
    ]

    logger.debug(f"Found {len(hrefs)} hrefs")

    tel_phones = Parser.parse_tel_links(hrefs)
    text_phones = []
    if not tel_phones:
        text_phones = Parser.parse_text_phones(html)
    phones = Parser.merge_unique(tel_phones + text_phones)

    socials = Parser.parse_socials(tree)

    result = {
        "phones": phones,
        "socials": socials,
    }

    logger.info(f"Parsed contacts: {result}")
    return result
