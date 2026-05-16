# tests/api/test_app_controller.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app import create_app


class TestAppController:

    @pytest.fixture
    def client(self):
        app = create_app()
        return TestClient(app)

    # -----------------------------
    # /api/metrics
    # -----------------------------
    @patch("app.run_metrics")
    def test_get_metrics(self, mock_service, client):
        mock_service.return_value = {
            "coverage": 123,
            "fill_rates": {"phones_per_coverage": 0.42},
            "final": {"phones": 50, "socials": 30},
        }

        response = client.get("/scraper/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["coverage"] == 123
        assert data["fill_rates"]["phones_per_coverage"] == 0.42
        assert data["final"]["phones"] == 50

        mock_service.assert_called_once()

    # -----------------------------
    # /api/scraper/history/summary
    # -----------------------------
    @patch("app.service.service_history.get_history_summary")
    def test_get_history_summary(self, mock_service, client):
        mock_service.return_value = {
            "20260516_090820": {
                "phones": 370,
                "socials": 313,
                "chunks_conc_par": [3, 3, 3],
                "duration": 453.061,
                "isp_org": "AS8953",
            }
        }

        response = client.get("/scraper/history/summary")

        assert response.status_code == 200
        data = response.json()

        assert "20260516_090820" in data
        assert data["20260516_090820"]["phones"] == 370
        assert data["20260516_090820"]["socials"] == 313
        assert data["20260516_090820"]["chunks_conc_par"] == [3, 3, 3]
        assert data["20260516_090820"]["isp_org"] == "AS8953"

        mock_service.assert_called_once()
