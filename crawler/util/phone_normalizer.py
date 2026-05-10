import logging
from crawler.util.country_codes import VALID_COUNTRY_CODES

logger = logging.getLogger(__name__)

MIN_DIGITS = 7
MAX_DIGITS = 16
MAX_PLAUSIBLE = 13


def digits_only(s: str) -> str:
    return "".join(c for c in s if c.isdigit())


def normalize_prefix(raw: str) -> str:
    s = raw.strip()
    if s.startswith("00"):
        return "+" + s[2:]
    return s


def is_valid_plus_number(raw: str) -> bool:
    if not raw.startswith("+"):
        return False

    digits = digits_only(raw[1:])

    # Try 1–3 digit country codes
    for length in (1, 2, 3):
        prefix = digits[:length]
        if prefix in VALID_COUNTRY_CODES:
            return True

    logger.debug(f"Ignoring invalid international prefix: {raw}")
    return False


def normalize_one(raw: str):
    """
    Normalize a single phone number.
    Returns None if invalid or should be ignored.
    """
    raw = normalize_prefix(raw)

    # Case 1: valid international
    if raw.startswith("+"):
        if not is_valid_plus_number(raw):
            return None
        digits = digits_only(raw)
        return "+" + digits

    # Case 2: local number
    digits = digits_only(raw)
    if not (MIN_DIGITS <= len(digits) <= MAX_DIGITS):
        return None

    return digits


def dedupe_and_normalize_phones(candidates):
    # STEP 1 — Normalize all valid numbers
    normalized = []
    for raw in candidates:
        norm = normalize_one(raw)
        if norm:
            normalized.append(norm)

    # STEP 2 — Sort by length DESC (longest first)
    normalized.sort(key=len, reverse=True)

    # STEP 3 — Keep only numbers not suffixes of previously kept ones
    result = []
    for num in normalized:
        digits = digits_only(num)

        keep = True
        for existing in result:
            existing_digits = digits_only(existing)

            # If this number is a suffix of an already kept number → skip
            if existing_digits.endswith(digits):
                keep = False
                break

        if keep:
            result.append(num)

    return result
