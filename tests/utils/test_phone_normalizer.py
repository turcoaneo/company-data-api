# tests/utils/test_phone_normalizer.py

from crawler.util.phone_normalizer import (
    dedupe_and_normalize_phones,
    digits_only,
    normalize_prefix,
)


class TestPhoneNormalizer:

    def test_digits_only(self):
        assert digits_only("(415) 626-4474") == "4156264474"
        assert digits_only("+44 20 7946 0958") == "442079460958"

    def test_normalize_prefix(self):
        assert normalize_prefix("0044123456789") == "+44123456789"
        assert normalize_prefix("+44123456789") == "+44123456789"
        assert normalize_prefix("44123456789") == "44123456789"

    def test_us_variants_de_duped(self):
        phones = [
            "4156264474",
            "(415) 626‑4474",
            "+1 415 626 4474",
            "0041 56 26 44 74",  # wrong country but same digits? No → kept separate
        ]
        result = dedupe_and_normalize_phones(phones)
        assert "+14156264474" in result
        assert len(result) == 1  # US + Swiss-like number

    def test_international_equivalence(self):
        phones = [
            "+44123456789",
            "0044123456789",
            "+44 123 456 789",
        ]
        result = dedupe_and_normalize_phones(phones)
        assert result == ["+44123456789"]

    def test_zip_code_filtered(self):
        phones = ["+14156264474", "94124 (415) 626-4474"]
        result = dedupe_and_normalize_phones(phones, default_country="+1")
        assert result == ["+14156264474"]

    def test_mixed_formats(self):
        phones = [
            "+49 (30) 1234 5678",
            "0049 30 1234 5678",
            "(030) 1234 5678",  # local German number → different digits
        ]
        result = dedupe_and_normalize_phones(phones, default_country="+1")

        assert "+493012345678" in result
        assert len(result) == 1
