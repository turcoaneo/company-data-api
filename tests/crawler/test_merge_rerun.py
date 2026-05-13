import json
from crawler.merge_results import merge_two_runs


class TestMergeTwoRuns:
    @staticmethod
    def write_jsonl(path, rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

    # ---------------------------------------------------------
    # 1. Second pass fills missing phones
    # ---------------------------------------------------------
    def test_second_pass_fills_missing_phones(self, tmp_path):
        first_path = tmp_path / "first.jsonl"
        final_path = tmp_path / "final.jsonl"

        first_rows = [
            {"domain": "example.com", "phones": [], "socials": []},
        ]
        self.write_jsonl(first_path, first_rows)

        second_results = [
            {"url": "https://example.com/contact", "phones": ["123"], "socials": []}
        ]

        merge_two_runs(str(first_path), second_results, str(final_path))

        merged = [json.loads(line) for line in final_path.read_text().splitlines()]
        assert merged[0]["phones"] == ["123"]
        assert "url" not in merged[0]

    # ---------------------------------------------------------
    # 2. Second pass does NOT override existing phones
    # ---------------------------------------------------------
    def test_second_pass_does_not_override_existing_phones(self, tmp_path):
        first_path = tmp_path / "first.jsonl"
        final_path = tmp_path / "final.jsonl"

        first_rows = [
            {"domain": "example.com", "phones": ["999"], "socials": []},
        ]
        self.write_jsonl(first_path, first_rows)

        second_results = [
            {"url": "https://example.com/contact", "phones": ["123"], "socials": []}
        ]

        merge_two_runs(str(first_path), second_results, str(final_path))

        merged = [json.loads(line) for line in final_path.read_text().splitlines()]
        assert merged[0]["phones"] == ["123"]
        assert "url" not in merged[0]

    # ---------------------------------------------------------
    # 3. www stripping + URL fallback
    # ---------------------------------------------------------
    def test_www_stripping_and_url_fallback(self, tmp_path):
        first_path = tmp_path / "first.jsonl"
        final_path = tmp_path / "final.jsonl"

        first_rows = [
            {"domain": "www.example.com", "phones": [], "socials": []},
        ]
        self.write_jsonl(first_path, first_rows)

        second_results = [
            {"url": "https://example.com/contact", "phones": ["123"], "socials": []}
        ]

        merge_two_runs(str(first_path), second_results, str(final_path))

        merged = [json.loads(line) for line in final_path.read_text().splitlines()]
        assert merged[0]["domain"] == "example.com"
        assert merged[0]["phones"] == ["123"]
        assert "url" not in merged[0]

    # ---------------------------------------------------------
    # 4. Multiple domains merged correctly
    # ---------------------------------------------------------
    def test_multiple_domains_merged_correctly(self, tmp_path):
        first_path = tmp_path / "first.jsonl"
        final_path = tmp_path / "final.jsonl"

        first_rows = [
            {"domain": "a.com", "phones": [], "socials": []},
            {"domain": "b.com", "phones": ["999"], "socials": []},
        ]
        self.write_jsonl(first_path, first_rows)

        second_results = [
            {"url": "https://a.com/contact", "phones": ["111"], "socials": []},
            {"url": "https://b.com/contact", "phones": ["222"], "socials": []},
        ]

        merge_two_runs(str(first_path), second_results, str(final_path))

        merged = {json.loads(line)["domain"]: json.loads(line)
                  for line in final_path.read_text().splitlines()}

        assert merged["a.com"]["phones"] == ["111"]
        assert merged["b.com"]["phones"] == ["222"]
        assert "url" not in merged["a.com"]
        assert "url" not in merged["b.com"]

    # ---------------------------------------------------------
    # 5. Merge by domain, not URL — no duplicates
    # ---------------------------------------------------------
    def test_merge_by_domain_not_url(self, tmp_path):
        first_path = tmp_path / "first.jsonl"
        final_path = tmp_path / "final.jsonl"

        first_rows = [
            {"domain": "clockinc.org", "phones": [], "socials": []},
        ]
        self.write_jsonl(first_path, first_rows)

        second_results = [
            {
                "url": "https://www.clockinc.org/contact",
                "phones": ["3095580956"],
                "socials": ["https://facebook.com/clock.inc.qc"]
            }
        ]

        merge_two_runs(str(first_path), second_results, str(final_path))

        merged = [json.loads(line) for line in final_path.read_text().splitlines()]
        assert len(merged) == 1

        rec = merged[0]
        assert rec["domain"] == "clockinc.org"
        assert rec["phones"] == ["3095580956"]
        assert rec["socials"] == ["https://facebook.com/clock.inc.qc"]
        assert "url" not in rec

    # ---------------------------------------------------------
    # 6. Company fields must be preserved from first pass
    # ---------------------------------------------------------
    def test_company_fields_preserved(self, tmp_path):
        first_path = tmp_path / "first.jsonl"
        final_path = tmp_path / "final.jsonl"

        first_rows = [
            {
                "domain": "burst-media.com",
                "company_commercial_name": "Burst Media",
                "company_legal_name": "Burst Media LLC",
                "company_all_available_names": "Burst Media | Burst Media LLC",
                "phones": [],
                "socials": []
            }
        ]
        self.write_jsonl(first_path, first_rows)

        second_results = [
            {
                "url": "https://burst-media.com/contact",
                "phones": ["2085739931"],
                "socials": ["https://facebook.com/BurstMediaLLC/"]
            }
        ]

        merge_two_runs(str(first_path), second_results, str(final_path))

        merged = [json.loads(line) for line in final_path.read_text().splitlines()]
        rec = merged[0]

        # Company fields preserved
        assert rec["company_commercial_name"] == "Burst Media"
        assert rec["company_legal_name"] == "Burst Media LLC"
        assert rec["company_all_available_names"] == "Burst Media | Burst Media LLC"

        # Phones/socials updated
        assert rec["phones"] == ["2085739931"]
        assert rec["socials"] == ["https://facebook.com/BurstMediaLLC/"]

        # URL removed
        assert "url" not in rec
