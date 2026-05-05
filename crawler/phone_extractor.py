import re
import logging
from typing import List

logger = logging.getLogger(__name__)

PHONE_CANDIDATE_RE = re.compile(
    r"""
    (?:
        (?:\+|\(|\d)            # allow +, (, or digit at start
        [\d\-\.\s\(\)]{5,}      # rest of the number
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
    ok = MIN_DIGITS <= len(digits) <= MAX_DIGITS
    if not ok:
        logger.debug(f"Rejected phone candidate '{raw}' (digit count={len(digits)})")
    return ok


def extract_phones(text: str) -> List[str]:
    candidates = [m.group(0) for m in PHONE_CANDIDATE_RE.finditer(text)]
    logger.debug(f"Phone candidates found: {candidates}")

    phones = [normalize_phone(c) for c in candidates if is_plausible_phone(c)]
    logger.debug(f"Plausible phones after filtering: {phones}")

    seen = set()
    result = []
    for p in phones:
        if p not in seen:
            seen.add(p)
            result.append(p)

    logger.debug(f"Final extracted phones: {result}")
    return result
