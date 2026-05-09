# tests/test_phone_extractor.py

from crawler.phone_extractor import (
    extract_phones,
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

    def test_extract_simple_numbers(self):
        text = "Call us at (021) 555 3333 or +1 415 555 1234"
        phones = extract_phones(text)
        assert "(021) 555 3333" in phones
        assert "+1 415 555 1234" in phones

    def test_extract_rejects_yui_ids(self):
        text = """
        id="block-yui_3_17_2_25_1516652858592_24920"
        id="block-yui_3_17_2_19_1480469240231_21286"
        """
        phones = extract_phones(text)
        assert phones == []

    def test_extract_with_separators(self):
        text = "Phone: 021-555-3333 or 021.555.3333 or 021 555 3333"
        phones = extract_phones(text)
        assert len(phones) == 3
        assert "021-555-3333" in phones
        assert "021.555.3333" in phones
        assert "021 555 3333" in phones

    def test_extract_with_extension(self):
        text = "Call +1 415 555 1234 ext 55"
        phones = extract_phones(text)
        assert "+1 415 555 1234 ext 55" in phones

    def test_extract_deduplication(self):
        text = "Call (021) 555 3333 or (021) 555 3333"
        phones = extract_phones(text)
        assert phones == ["(021) 555 3333"]
