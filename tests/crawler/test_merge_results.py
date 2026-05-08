import json

# noinspection PyPackageRequirements
import pandas as pd
import pytest

from crawler.merge_results import merge_scraper_results


class TestMergeScraperResults:

    @pytest.fixture
    def input_csv(self, tmp_path):
        """
        Create a realistic input CSV matching the Veridion challenge structure.
        """
        csv_path = tmp_path / "input.csv"

        df = pd.DataFrame({
            "domain": [
                "bostonzen.org",
                "mazautoglass.com",
                "top-salon-hair-salon.business.site",
            ],
            "company_commercial_name": [
                "Greater Boston Zen Center",
                "MAZ Auto Glass",
                "Top salon Hair Salon",
            ],
            "company_legal_name": [
                "GREATER BOSTON ZEN CENTER INC.",
                "",
                "",
            ],
            "company_all_available_names": [
                "Greater Boston Zen Center | Boston Zen | GREATER BOSTON ZEN CENTER INC.",
                "MAZ Auto Glass",
                "Top salon Hair Salon | Top salon",
            ],
        })

        df.to_csv(csv_path, index=False)
        return csv_path

    @pytest.fixture
    def scraper_results(self):
        """
        Fake scraper output from orchestrator.
        """
        return [
            {
                "url": "bostonzen.org",
                "phones": ["+1 234 567 890"],
                "emails": ["info@bostonzen.org"],
                "socials": ["https://facebook.com/bostonzen"],
            },
            {
                "url": "top-salon-hair-salon.business.site",
                "phones": [],
                "emails": [],
                "socials": ["https://instagram.com/top_salon"],
            },
        ]

    # ---------------------------------------------------------
    # Test 1: merged JSONL file is created
    # ---------------------------------------------------------
    def test_output_file_created(self, input_csv, scraper_results, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        output_path = merge_scraper_results(str(input_csv), scraper_results, output_dir=str(tmp_path))

        assert output_path.exists()
        assert output_path.suffix == ".jsonl"

    # ---------------------------------------------------------
    # Test 2: merged rows contain original + scraped fields
    # ---------------------------------------------------------
    def test_merged_content(self, input_csv, scraper_results, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        output_path = merge_scraper_results(str(input_csv), scraper_results, output_dir=str(tmp_path))

        lines = output_path.read_text().splitlines()
        assert len(lines) == 3  # same number of rows as input CSV

        rows = [json.loads(line) for line in lines]

        # Row 1: bostonzen.org
        r1 = next(r for r in rows if r["domain"] == "bostonzen.org")
        assert r1["phones"] == ["+1 234 567 890"]
        assert r1["emails"] == ["info@bostonzen.org"]
        assert r1["socials"] == ["https://facebook.com/bostonzen"]
        assert r1["company_commercial_name"] == "Greater Boston Zen Center"

        # Row 2: mazautoglass.com (no scraper result)
        r2 = next(r for r in rows if r["domain"] == "mazautoglass.com")
        assert r2["phones"] == []
        assert r2["emails"] == []
        assert r2["socials"] == []

        # Row 3: top-salon-hair-salon.business.site
        r3 = next(r for r in rows if r["domain"] == "top-salon-hair-salon.business.site")
        assert r3["phones"] == []
        assert r3["emails"] == []
        assert r3["socials"] == ["https://instagram.com/top_salon"]

    # ---------------------------------------------------------
    # Test 3: missing scraped fields default to empty lists
    # ---------------------------------------------------------
    def test_missing_fields_default(self, input_csv, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        # scraper returns only one domain, missing fields
        results = [{"url": "bostonzen.org"}]

        output_path = merge_scraper_results(str(input_csv), results, output_dir=str(tmp_path))
        rows = [json.loads(line) for line in output_path.read_text().splitlines()]

        r1 = next(r for r in rows if r["domain"] == "bostonzen.org")
        assert r1["phones"] == []
        assert r1["emails"] == []
        assert r1["socials"] == []
