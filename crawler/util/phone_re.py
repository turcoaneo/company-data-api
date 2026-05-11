# /crawler/util/phone_re.py

import re

# Realistic phone number pattern
PHONE_RE = re.compile(
    r"""
    (?:
        (?:\+?\d{1,3}[\s\-.]?)?          # optional +CC or CC
        (?:\(\+?\d{1,4}\)|\d{2,4})       # area code: (415), (+40), 1234
        (?:[\s\-.]?\d{2,4}){2,3}         # 2 or 3 groups of 2–4 digits
        (?:\s*(?:ext|x|\#)\s*\d{1,5})?   # extension
    )
    """,
    re.VERBOSE,
)
