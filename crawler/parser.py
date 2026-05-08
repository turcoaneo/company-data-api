import logging
from selectolax.parser import HTMLParser
from .phone_extractor import extract_phones
from .socials import extract_social_links

logger = logging.getLogger(__name__)


class Parser:

    @staticmethod
    def parse_tel_links(hrefs):
        phones = []
        for href in hrefs:
            if href.lower().startswith("tel:"):
                number = href.split(":", 1)[1].strip()
                phones.append(number)
        logger.debug(f"TEL phones extracted: {phones}")
        return phones

    @staticmethod
    def parse_text_phones(html: str):
        tree = HTMLParser(html)
        text = tree.text(separator=" ")
        phones = extract_phones(text)
        logger.debug(f"Text phones extracted: {phones}")
        return phones

    @staticmethod
    def parse_emails(hrefs):
        emails = []
        for href in hrefs:
            if href.lower().startswith("mailto:"):
                email = href.split(":", 1)[1].strip()
                if email and email not in emails:
                    emails.append(email)
        logger.debug(f"Emails extracted: {emails}")
        return emails

    @staticmethod
    def parse_socials(hrefs):
        socials = extract_social_links(hrefs)
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
    hrefs = [n.attributes.get("href", "") for n in tree.css("a")]

    logger.debug(f"Found {len(hrefs)} hrefs")

    tel_phones = Parser.parse_tel_links(hrefs)
    text_phones = Parser.parse_text_phones(html)
    phones = Parser.merge_unique(tel_phones + text_phones)

    # emails = Parser.parse_emails(hrefs)
    socials = Parser.parse_socials(hrefs)

    result = {
        "phones": phones,
        # "emails": emails,
        "socials": socials,
    }

    logger.info(f"Parsed contacts: {result}")
    return result
