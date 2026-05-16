import pytest
from unittest.mock import patch

from app.service.service_metrics import run_metrics


class TestServiceMetrics:

    @patch("app.service.service_metrics.compute_scraper_metrics")
    def test_run_metrics(self, mock_compute):
        # Mock compute_scraper_metrics output
        mock_compute.return_value = {
            "coverage": 10,
            "final": {"phones": 5, "socials": 3},
            "fill_rates": {"phones_per_coverage": 0.5},
        }

        result = run_metrics()

        assert result["coverage"] == 10
        assert result["final"]["phones"] == 5
        assert result["fill_rates"]["phones_per_coverage"] == 0.5

        mock_compute.assert_called_once()
