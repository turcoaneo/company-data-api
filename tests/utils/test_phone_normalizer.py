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
        assert digits_only("818.422.3831") == "8184223831"

    def test_normalize_prefix(self):
        assert normalize_prefix("0044123456789") == "+44123456789"
        assert normalize_prefix("+44123456789") == "+44123456789"
        assert normalize_prefix("44123456789") == "44123456789"

    def test_invalid_plus_numbers_are_ignored(self):
        phones = ["+904-824-8353", "+99912345678"]
        result = dedupe_and_normalize_phones(phones)
        assert result == ["+9048248353"]

    def test_valid_plus_numbers(self):
        phones = ["+386-328-2710"]
        result = dedupe_and_normalize_phones(phones)
        assert result == ["+3863282710"]

    def test_plus_and_no_plus(self):
        phones = ["904-824-8353", "+904-824-8353", "+386-328-2710"]
        result = dedupe_and_normalize_phones(phones)
        assert "+3863282710" in result
        assert "+9048248353" in result
        assert len(result) == 2

    def test_us_and_local_duplicate(self):
        phones = ["+17139798345", "713-979-8345"]
        result = dedupe_and_normalize_phones(phones)
        assert result == ["+17139798345"]

    def test_real_world_us_variants(self):
        phones = ["(229) 436-9620", "229-344-5037"]
        result = dedupe_and_normalize_phones(phones)
        assert "2294369620" in result
        assert "2293445037" in result
        assert len(result) == 2

    def test_mixed_formats(self):
        phones = [
            "+49 (30) 1234 5678",
            "0049 30 1234 5678",
            "(030) 1234 5678",
        ]
        result = dedupe_and_normalize_phones(phones)
        assert "+493012345678" in result
        assert "03012345678" in result
        assert len(result) == 2
