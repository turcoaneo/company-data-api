from selectolax.parser import HTMLParser

def parse_contacts(html: str) -> dict:
    tree = HTMLParser(html)
    # TODO: implement extraction for phones, emails, socials
    return {
        "phones": [],
        "emails": [],
        "socials": [],
    }
