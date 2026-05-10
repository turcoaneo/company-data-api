# crawler/socials.py

SOCIAL_DOMAINS = [
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "tiktok.com",
    "youtube.com",
    "twitter.com",
    "x.com",
    "pinterest.com",
]

SOCIAL_KEYWORDS = [
    "facebook",
    "instagram",
    "linkedin",
    "tiktok",
    "youtube",
    "twitter",
    "pinterest",
    "follow us",
    "social",
]

SOCIAL_CLASSES = [
    "social",
    "social-link",
    "social-icon",
    "sqs-block-button-element",
    "sqs-block-button-container",
    "bg-social-facebook",
    "bg-social-instagram",
    "bg-social-twitter",
]


def is_social_domain(href: str) -> bool:
    return any(domain in href.lower() for domain in SOCIAL_DOMAINS)


def is_social_context(node) -> bool:
    # Check class attributes
    cls = (node.attributes.get("class") or "").lower()
    if any(key in cls for key in SOCIAL_CLASSES):
        return True

    # Check aria-label
    aria = (node.attributes.get("aria-label") or "").lower()
    if any(key in aria for key in SOCIAL_KEYWORDS):
        return True

    # Check anchor text
    text = node.text(strip=True).lower()
    if any(key in text for key in SOCIAL_KEYWORDS):
        return True

    return False


def extract_social_links(tree):
    socials = []

    for a in tree.css("a"):
        href = a.attributes.get("href") or ""
        if not href:
            continue

        if not is_social_domain(href):
            continue

        # Must be inside a semantic social container
        node = a
        is_valid = False

        # Check the <a> itself
        if is_social_context(node):
            is_valid = True

        # Check parents up to 3 levels
        parent = node.parent
        depth = 0
        while parent is not None and depth < 3:
            if is_social_context(parent):
                is_valid = True
                break
            parent = parent.parent
            depth += 1

        if is_valid:
            socials.append(href)

    # Deduplicate
    return list(dict.fromkeys(socials))
