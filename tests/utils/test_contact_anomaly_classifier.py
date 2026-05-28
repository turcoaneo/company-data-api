# tests/test_contact_anomaly_classifier.py

import json
import tempfile
import os

from qa.contact_anomaly_classifier import (
    classify_contacts_jsonl,
    extract_tokens,
    social_matches_company,
)


class TestContactAnomalyClassifier:

    def test_extract_tokens(self):
        tokens = extract_tokens("my-domain.com", "My Domain Inc")
        assert "mydomain" in tokens
        assert "domain" in tokens
        assert "my" not in tokens  # too short (<3 chars)

    def test_social_matches_company(self):
        tokens = {"steppir", "communication"}
        assert social_matches_company("https://facebook.com/steppir", tokens)
        assert not social_matches_company("https://facebook.com/randompage", tokens)

    def test_classify_contacts_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            jsonl_path = os.path.join(tmpdir, "contacts.jsonl")
            report_path = os.path.join(tmpdir, "report.json")

            with open(jsonl_path, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "domain": "aaa.com",
                    "phones": ["1", "2", "3", "4", "5", "6"],
                    "socials": ["https://facebook.com/aaa"],
                    "company_commercial_name": "A Company"
                }) + "\n")

                f.write(json.dumps({
                    "domain": "bbb.com",
                    "phones": ["1"],
                    "socials": ["https://facebook.com/random"],
                    "company_commercial_name": "B Company"
                }) + "\n")

                f.write(json.dumps({
                    "domain": "ccc.com",
                    "phones": ["1"],
                    "socials": ["https://facebook.com/ccc"],
                    "company_commercial_name": "C Company"
                }) + "\n")

            report = classify_contacts_jsonl(
                jsonl_path=jsonl_path,
                threshold_phones=5,
                threshold_socials=5,
                report_path=report_path,
            )

            # Basic anomaly checks
            assert "aaa.com" in report["too_many_phones"]
            assert "bbb.com" in report["socials_mismatch"]
            assert "ccc.com" not in report["socials_mismatch"]

            # Report file exists and contains details
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "details" in data
            assert "aaa.com" in data["details"]
            assert data["details"]["aaa.com"]["flags"] == ["too_many_phones"]
            assert "bbb.com" in data["details"]
            assert "socials_mismatch" in data["details"]["bbb.com"]["flags"]
