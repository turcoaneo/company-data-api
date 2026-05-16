# tests/service/test_service_metrics.py

import time
from unittest.mock import patch

from app.service.service_metrics import run_metrics, find_latest_results_file


class TestServiceMetrics:

    @patch("app.service.service_metrics.compute_latest_and_top_metrics")
    @patch("app.service.service_metrics.find_latest_results_file")
    def test_run_metrics(self, mock_find, mock_compute):
        mock_find.return_value = "data/results_20260516_061723.jsonl"

        mock_compute.return_value = {
            "coverage": 10,
            "final": {"phones": 5, "socials": 3},
            "fill_rates": {"phones_per_coverage": 0.5},
        }

        result = run_metrics()

        assert result["coverage"] == 10
        assert result["final"]["phones"] == 5
        assert result["fill_rates"]["phones_per_coverage"] == 0.5

        mock_find.assert_called_once()
        mock_compute.assert_called_once()

    def test_find_latest_results_file(self, tmp_path, monkeypatch):
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        f1 = data_dir / "results_20260101_120000.jsonl"
        f2 = data_dir / "results_20260101_130000.jsonl"

        f1.write_text("a")
        time.sleep(0.01)  # ensure different mtime
        f2.write_text("b")

        monkeypatch.chdir(tmp_path)

        latest = find_latest_results_file()
        assert latest.endswith("results_20260101_130000.jsonl")
