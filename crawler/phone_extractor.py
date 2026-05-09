# /crawler/phone_extractor.py

import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# Realistic phone number pattern
PHONE_RE = re.compile(
    r"""
    (?:
        (?:\+?\d{1,3}[\s\-.]?)?
        (?:\(\d{2,4}\)|\d{2,4})
        [\s\-.]?
        \d{2,4}
        [\s\-.]?
        \d{2,4}
        (?:\s*(?:ext|x|\#)\s*\d{1,5})?
    )
    """,
    re.VERBOSE,
)

MIN_DIGITS = 7
MAX_DIGITS = 16


def normalize_phone(raw: str) -> str:
    """Normalize whitespace and remove double spaces."""
    return " ".join(raw.split()).strip()


def is_plausible_phone(raw: str) -> bool:
    """Reject long digit-only sequences and enforce digit count."""
    digits = [c for c in raw if c.isdigit()]

    # Reject Squarespace/YUI IDs, timestamps, etc.
    if raw.isdigit() and len(digits) > 10:
        logger.debug(f"Rejected long digit-only sequence: {raw}")
        return False

    ok = MIN_DIGITS <= len(digits) <= MAX_DIGITS
    if not ok:
        logger.debug(f"Rejected phone candidate '{raw}' (digit count={len(digits)})")
    return ok


def extract_phones(text: str) -> List[str]:
    """Extract realistic phone numbers from visible text."""
    candidates = PHONE_RE.findall(text)
    logger.debug(f"Phone candidates found: {candidates}")

    phones = []
    for c in candidates:
        if is_plausible_phone(c):
            phones.append(normalize_phone(c))

    # Deduplicate
    seen = set()
    result = []
    for p in phones:
        if p not in seen:
            seen.add(p)
            result.append(p)

    logger.debug(f"Final extracted phones: {result}")
    return result
