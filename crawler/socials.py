from typing import List
import re

SOCIAL_DOMAINS = [
    "facebook.com",
    "linkedin.com",
    "instagram.com",
    "x.com",
    "twitter.com",
    "youtube.com",
    "tiktok.com",
    "pinterest.com",
    "threads.net",
    "snapchat.com",
    "wechat.com",
    "vk.com",
]

SOCIAL_RE = re.compile(
    r"https?://(?:www\.)?(%s)/[^\s\"']+" % "|".join(
        d.replace(".", r"\.") for d in SOCIAL_DOMAINS
    ),
    re.IGNORECASE,
)


def extract_social_links(hrefs: List[str]) -> List[str]:
    socials = []
    seen = set()
    for href in hrefs:
        if not href:
            continue
        m = SOCIAL_RE.search(href)
        if m and href not in seen:
            seen.add(href)
            socials.append(href)
    return socials
