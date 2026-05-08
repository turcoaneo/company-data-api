from crawler.pipeline import normalize_record


class TestNormalizeRecord:

    # ---------------------------------------------------------
    # 1. Full record with all fields present
    # ---------------------------------------------------------
    def test_full_record(self):
        record = {
            "url": "example.com",
            "phones": ["123 456 789"],
            "emails": ["a@example.com"],
            "socials": ["https://facebook.com/example"]
        }

        out = normalize_record(record)

        assert out["url"] == "example.com"
        assert out["phones"] == ["+123456789"]
        assert out["emails"] == ["a@example.com"]
        assert out["socials"] == ["https://facebook.com/example"]

    # ---------------------------------------------------------
    # 2. Missing phones/emails/socials → should become empty lists
    # ---------------------------------------------------------
    def test_missing_fields(self):
        record = {"url": "example.com"}

        out = normalize_record(record)

        assert out["phones"] == []
        assert out["emails"] == []
        assert out["socials"] == []

    # ---------------------------------------------------------
    # 3. Fields explicitly set to None → should become empty lists
    # ---------------------------------------------------------
    def test_none_fields(self):
        record = {
            "url": "example.com",
            "phones": None,
            "emails": None,
            "socials": None
        }

        out = normalize_record(record)

        assert out["phones"] == []
        assert out["emails"] == []
        assert out["socials"] == []

    # ---------------------------------------------------------
    # 4. Empty lists should remain empty lists
    # ---------------------------------------------------------
    def test_empty_lists(self):
        record = {
            "url": "example.com",
            "phones": [],
            "emails": [],
            "socials": []
        }

        out = normalize_record(record)

        assert out["phones"] == []
        assert out["emails"] == []
        assert out["socials"] == []

    # ---------------------------------------------------------
    # 5. Mixed case: some fields missing, some None, some valid
    # ---------------------------------------------------------
    def test_mixed_fields(self):
        record = {
            "url": "example.com",
            "phones": ["123"],
            "emails": None,
            # socials missing
        }

        out = normalize_record(record)

        assert out["phones"] == []
        assert out["emails"] == []
        assert out["socials"] == []

    # ---------------------------------------------------------
    # 6. URL missing → should still return None
    # ---------------------------------------------------------
    def test_missing_url(self):
        record = {
            "phones": ["(123)-456-789"],
            "emails": ["a@example.com"],
            "socials": []
        }

        out = normalize_record(record)

        assert out.get("url") is None
        assert out["phones"] == ["+123456789"]
        assert out["emails"] == ["a@example.com"]
        assert out["socials"] == []
