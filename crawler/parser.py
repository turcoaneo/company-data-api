from selectolax.parser import HTMLParser
from .phone_extractor import extract_phones
from .socials import extract_social_links


def parse_contacts(html: str) -> dict:
    tree = HTMLParser(html)

    # Collect all hrefs
    hrefs = [n.attributes.get("href", "") for n in tree.css("a")]

    # Phones from tel: links
    tel_phones = []
    for href in hrefs:
        if href.lower().startswith("tel:"):
            tel_phones.append(href.split(":", 1)[1].strip())

    # Phones from plain text
    text_content = tree.text(separator=" ")
    text_phones = extract_phones(text_content)

    # Merge phones (tel: + text)
    phones = []
    seen = set()
    for p in tel_phones + text_phones:
        if p not in seen:
            seen.add(p)
            phones.append(p)

    # Emails (still useful even if not required now)
    emails = []
    for href in hrefs:
        if href.lower().startswith("mailto:"):
            email = href.split(":", 1)[1].strip()
            if email and email not in emails:
                emails.append(email)

    # Social links
    socials = extract_social_links(hrefs)

    return {
        "phones": phones,
        "emails": emails,
        "socials": socials,
    }
