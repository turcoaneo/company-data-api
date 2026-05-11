import logging
import re
from typing import Optional

from crawler.phone_extractor import is_plausible_phone
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


PREFIX_DELIMITER_RE = re.compile(
    r"""
    ^\+                # starts with +
    \s*
    (?P<prefix>\d{1,4}) # 1–4 digit prefix
    (?P<delim>[\s.\-()]+) # delimiter(s)
    """,
    re.VERBOSE,
)


def strip_invalid_delimited_plus(raw: str) -> str:
    """
    If a phone number starts with + and the prefix is visually delimited
    (e.g., +40-..., +995 ..., (+81) ..., +1.345. ...),
    validate the prefix. If invalid, strip '+'.
    """
    s = raw.strip()
    if not s.startswith("+"):
        return raw

    m = PREFIX_DELIMITER_RE.match(s)
    if not m:
        return raw  # no delimiter → leave it alone

    prefix = m.group("prefix")

    if prefix in VALID_COUNTRY_CODES:
        return raw  # valid international prefix

    # invalid → strip '+'
    return s[1:]


def reject_invalid_delimited_plus(raw: str) -> Optional[str]:
    """
    If a phone number starts with + and the prefix is visually delimited
    (e.g., +40-..., +995 ..., (+81) ..., +1.345. ...),
    return None to be removed.
    """
    s = raw.strip()
    m = PREFIX_DELIMITER_RE.match(s)
    prefix = m.group("prefix") if m is not None else None
    if not s.startswith("+") or not m or prefix in VALID_COUNTRY_CODES:
        return raw
    else:
        return None


PAREN_PLUS_RE = re.compile(
    r"""
    ^\(\+            # literal (+ at start
    (?P<prefix>\d{1,4})  # 1–4 digit prefix
    \)               # closing parenthesis
    """,
    re.VERBOSE,
)


def normalize_parenthesized_plus_prefix(raw: str) -> str:
    """
    Convert '(+40) 123-4567' → '+40 123-4567'
    before the main normalization logic.
    """
    s = raw.strip()
    m = PAREN_PLUS_RE.match(s)
    if not m:
        return raw

    prefix = m.group("prefix")
    # Only rewrite if prefix is a valid country code
    if prefix in VALID_COUNTRY_CODES:
        # Replace '(+40)' with '+40'
        return "+{}{}".format(prefix, s[m.end():])
    return raw


def dedupe_and_normalize_phones(candidates):
    # STEP 1 — Normalize all valid numbers
    normalized = []
    for raw in candidates:
        if not is_plausible_phone(raw):
            continue
        raw = normalize_parenthesized_plus_prefix(raw)
        raw = reject_invalid_delimited_plus(raw)
        if raw is None:
            continue
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
