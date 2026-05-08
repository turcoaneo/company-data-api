import re

MIN_DIGITS = 7
MAX_DIGITS = 16
MAX_PLAUSIBLE = 13  # your rule

PHONE_CANDIDATE_RE = re.compile(
    r"""
    \+?\d[\d\-.\s()]{6,}
    """,
    re.VERBOSE,
)


def digits_only(s: str) -> str:
    return "".join(c for c in s if c.isdigit())


def normalize_prefix(raw: str) -> str:
    s = raw.strip()
    if s.startswith("00"):
        return "+" + s[2:]
    return s


def is_plausible_phone(digits: str) -> bool:
    return MIN_DIGITS <= len(digits) <= MAX_DIGITS


def normalize_e164(digits: str, default_country="+1") -> str:
    country_digits = default_country.lstrip("+")

    # Already includes country code
    if digits.startswith(country_digits):
        return "+" + digits

    # US 10-digit
    if len(digits) == 10:
        return default_country + digits

    # Local trunk prefix (030..., 021..., etc.)
    if digits.startswith("0") and not digits.startswith(country_digits):
        return digits

    # 7-digit local
    if len(digits) == 7:
        return digits

    # International
    return "+" + digits


def dedupe_and_normalize_phones(candidates, default_country="+1"):
    result = []  # list of (digits, normalized)

    for raw in candidates:
        raw = normalize_prefix(raw)
        digits = digits_only(raw)

        if not is_plausible_phone(digits):
            continue

        # Track what to do
        skip_candidate = False
        replace_index = None

        for i, (existing_digits, _) in enumerate(result):

            # --- CASE A: candidate ends with existing (ZIP prefix garbage)
            if digits.endswith(existing_digits):
                # Example: 941244156264474 endswith 14156264474
                skip_candidate = True
                break

            # --- CASE B: existing ends with candidate (candidate is better)
            if existing_digits.endswith(digits):
                # Example: existing=4156264474, candidate=14156264474
                if len(digits) <= MAX_PLAUSIBLE:
                    replace_index = i
                skip_candidate = True
                break

            # --- CASE C: shared suffix → keep longest plausible
            # Example: digits=14156264474, existing=4156264474
            if digits.endswith(existing_digits[-7:]) or existing_digits.endswith(digits[-7:]):
                # choose longest ≤ MAX_PLAUSIBLE
                if len(existing_digits) < len(digits) <= MAX_PLAUSIBLE:
                    replace_index = i
                skip_candidate = True
                break

        # Apply replacement
        if replace_index is not None:
            result[replace_index] = (
                digits,
                normalize_e164(digits, default_country)
            )
            continue

        # Skip candidate entirely
        if skip_candidate:
            continue

        # Otherwise add new entry
        result.append((digits, normalize_e164(digits, default_country)))

    return [norm for _, norm in result]
