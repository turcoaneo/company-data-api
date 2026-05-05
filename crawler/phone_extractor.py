import re
from typing import List

# Very permissive, then filtered by length and digit count
PHONE_CANDIDATE_RE = re.compile(
    r"""
    (?:
        \+?\d[\d\-\.\s\(\)]{5,}   # +40 123 456 789, (021)5553333, 021-555-3333
    )
    """,
    re.VERBOSE,
)

MIN_DIGITS = 7
MAX_DIGITS = 16


def normalize_phone(raw: str) -> str:
    return " ".join(raw.split()).strip()


def is_plausible_phone(raw: str) -> bool:
    digits = [c for c in raw if c.isdigit()]
    return MIN_DIGITS <= len(digits) <= MAX_DIGITS


def extract_phones(text: str) -> List[str]:
    candidates = [m.group(0) for m in PHONE_CANDIDATE_RE.finditer(text)]
    phones = [normalize_phone(c) for c in candidates if is_plausible_phone(c)]
    # Deduplicate preserving order
    seen = set()
    result = []
    for p in phones:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result
