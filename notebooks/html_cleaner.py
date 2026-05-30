# notebooks/html_cleaner.py

import re

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_RE = re.compile(r"<meta[^>]+>", re.IGNORECASE)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)


def clean_html(raw: str) -> str:
    # Extract <title>
    title_match = TITLE_RE.search(raw)
    title = title_match.group(1).strip() if title_match else ""

    # Extract <h1>
    h1_match = H1_RE.search(raw)
    h1 = h1_match.group(1).strip() if h1_match else ""

    # Neutralize misleading 403 Forbidden in BOTH
    def neutralize(text: str) -> str:
        t = text.lower()
        if "403" in t and "forbidden" in t:
            return ""
        return text

    title = neutralize(title)
    h1 = neutralize(h1)

    # Extract meta tags
    metas = META_RE.findall(raw)

    # Build semantic-only HTML
    return (
            f"<title>{title}</title>\n"
            + "\n".join(metas)
            + f"\n<h1>{h1}</h1>"
    )
