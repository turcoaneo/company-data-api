# tests/api/test_metrics_controller.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app import create_app


class TestMetricsController:

    @pytest.fixture
    def client(self):
        app = create_app()
        return TestClient(app)

    @patch("app.run_metrics")
    def test_get_metrics(self, mock_service, client):
        mock_service.return_value = {
            "coverage": 123,
            "fill_rates": {"phones_per_coverage": 0.42},
            "final": {"phones": 50, "socials": 30},
        }

        response = client.get("/api/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["coverage"] == 123
        assert data["fill_rates"]["phones_per_coverage"] == 0.42
        assert data["final"]["phones"] == 50

        mock_service.assert_called_once()
