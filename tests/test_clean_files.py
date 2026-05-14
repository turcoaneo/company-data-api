# tests/test_clean_files.py

from crawler.clean_files import clean_scraper_files


class TestCleanFiles:
    def test_clean_files_removes_targets_and_patterns(self, tmp_path):
        # Exact files
        exact_files = [
            tmp_path / "bad_urls.txt",
            tmp_path / "missing_contacts.txt",
            tmp_path / "bad_urls_report.csv",
            tmp_path / "bad_urls_report.json",
            tmp_path / "final_result.jsonl",
        ]

        # Pattern-based files
        pattern_files = [
            tmp_path / "partial_results_0.jsonl",
            tmp_path / "partial_results_1.jsonl",
            tmp_path / "results_foo.jsonl",
            tmp_path / "results_bar.jsonl",
        ]

        # Create all files
        for p in exact_files + pattern_files:
            p.write_text("dummy")

        # Run cleaner
        clean_scraper_files(str(tmp_path))

        # Assert all removed
        for p in exact_files + pattern_files:
            assert not p.exists()
