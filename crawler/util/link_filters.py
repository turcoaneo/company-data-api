# crawler/util/link_filters.py

SEMANTIC_KEYWORDS = [
    "about", "contact", "support", "team", "staff",
    "leadership", "company", "info", "who-we-are",
    "whoweare", "help", "customer-service", "customer",
]

GARBAGE_EXT = [
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".zip", ".rar", ".mp4", ".avi", ".mov", ".docx", ".xlsx",
]

LOW_SIGNAL = [
    "calendar", "events", "blog", "news", "feed",
    "wp-json", "tag", "category", "product", "shop",
    "portfolio", "gallery", "media", "uploads",
]


def is_semantic(href: str) -> bool:
    href = href.lower()
    return any(k in href for k in SEMANTIC_KEYWORDS)


def is_garbage(href: str) -> bool:
    href = href.lower()
    return any(href.endswith(ext) for ext in GARBAGE_EXT)


def is_low_signal(href: str) -> bool:
    href = href.lower()
    return any(bad in href for bad in LOW_SIGNAL)
