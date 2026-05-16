# tests/utils/test_metrics_analyzer.py

import json
import csv
from pathlib import Path

import pytest

from crawler.util.metrics_analyzer import compute_scraper_metrics


class TestMetricsAnalyzer:

    @pytest.fixture
    def setup_files(self, tmp_path):
        """
        Creates a realistic environment:
        - input CSV with 5 sites
        - bad_urls.txt with 1 unreachable
        - missing_contacts.txt with 1 missing
        - initial JSONL with 2 sites having contacts
        - final JSONL with 3 sites having contacts (1 recovered)
        """
        # Switch working directory
        old_cwd = Path.cwd()
        import os
        os.chdir(tmp_path)

        # 1. CSV with 5 sites
        csv_path = tmp_path / "sites.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["domain"])
            writer.writerow(["a.com"])
            writer.writerow(["b.com"])
            writer.writerow(["c.com"])
            writer.writerow(["d.com"])
            writer.writerow(["e.com"])

        # 2. bad_urls.txt (1 unreachable)
        bad_urls = tmp_path / "bad_urls.txt"
        bad_urls.write_text("d.com\n", encoding="utf-8")

        # 3. missing_contacts.txt (1 missing)
        missing = tmp_path / "missing_contacts.txt"
        missing.write_text("c.com\n", encoding="utf-8")

        # 4. initial JSONL (2 sites with contacts)
        initial = tmp_path / "results_20260515_120000.jsonl"
        initial.write_text(
            "\n".join([
                json.dumps({"url": "a.com", "phones": ["1"], "socials": []}),
                json.dumps({"url": "b.com", "phones": [], "socials": ["fb"]}),
                json.dumps({"url": "c.com", "phones": [], "socials": []}),
            ]),
            encoding="utf-8"
        )

        # 5. final JSONL (3 sites with contacts → 1 recovered)
        final = tmp_path / "final_result.jsonl"
        final.write_text(
            "\n".join([
                json.dumps({"domain": "a.com", "phones": ["1"], "socials": []}),
                json.dumps({"domain": "b.com", "phones": [], "socials": ["fb"]}),
                json.dumps({"domain": "c.com", "phones": ["2"], "socials": []}),  # recovered
            ]),
            encoding="utf-8"
        )

        yield {
            "csv": csv_path,
            "bad": bad_urls,
            "missing": missing,
            "initial": initial,
            "final": final,
        }

        os.chdir(old_cwd)

    def test_compute_metrics(self, setup_files):
        paths = setup_files

        metrics = compute_scraper_metrics(
            input_csv_path=str(paths["csv"]),
            bad_urls_path=str(paths["bad"]),
            missing_contacts_path=str(paths["missing"]),
            initial_jsonl_path=str(paths["initial"]),
            final_jsonl_path=str(paths["final"]),
        )

        assert metrics["total_sites"] == 5
        assert metrics["unreachable_sites"] == 1
        assert metrics["missing_contacts"] == 1

        assert metrics["recovered_sites"] == 1
        assert metrics["coverage"] == 5

        # Initial
        assert metrics["initial"]["sites_with_contacts"] == 2
        assert metrics["initial"]["phones"] == 1
        assert metrics["initial"]["socials"] == 1
        assert metrics["initial"]["phones_and_socials"] == 0

        # Final
        assert metrics["final"]["sites_with_contacts"] == 3
        assert metrics["final"]["phones"] == 2
        assert metrics["final"]["socials"] == 1
        assert metrics["final"]["phones_and_socials"] == 0

        fr = metrics["fill_rates"]
        assert fr["phones_per_coverage"] == pytest.approx(2 / 5)
        assert fr["socials_per_coverage"] == pytest.approx(1 / 5)
        assert fr["datapoints_per_coverage"] == pytest.approx(3 / 5)
        assert fr["any_datapoints_per_coverage"] == pytest.approx(3 / 5)
