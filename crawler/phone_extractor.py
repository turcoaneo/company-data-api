# /crawler/phone_extractor.py

import logging
from typing import List

from crawler.util.phone_re import PHONE_RE

logger = logging.getLogger(__name__)

MIN_DIGITS = 9
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
