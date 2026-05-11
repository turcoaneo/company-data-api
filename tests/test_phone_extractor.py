# tests/test_phone_extractor.py

from crawler.phone_extractor import (
    is_plausible_phone,
    normalize_phone,
)


class TestPhoneExtractor:

    def test_normalize_phone(self):
        assert normalize_phone("  +1   415   555  1234 ") == "+1 415 555 1234"

    def test_is_plausible_phone_valid(self):
        assert is_plausible_phone("+1 (415) 555-1234")
        assert is_plausible_phone("021-555-3333")

    def test_is_plausible_phone_reject_long_digit_only(self):
        # Squarespace/YUI IDs
        assert not is_plausible_phone("1516652858592")
        assert not is_plausible_phone("1480469240231")
        assert not is_plausible_phone("1412172079418")
