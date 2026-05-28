# tests/api/test_matcher_api_sanitized.py

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI


class TestMatcherAPISanitized:

    @pytest.fixture(autouse=True)
    def setup_client(self):
        # Patch meilisearch.Client BEFORE importing matcher.api
        with patch("matcher.service.meilisearch.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_index = MagicMock()
            mock_client.index.return_value = mock_index
            mock_client_cls.return_value = mock_client

            from matcher.api import matcher_router

            app = FastAPI()
            app.include_router(matcher_router)
            self.client = TestClient(app)

            self._mock_client = mock_client
            self._mock_index = mock_index

            yield

    # ---------------------------------------------------------
    # /api/match/sanitized
    # ---------------------------------------------------------
    def test_sanitized_match(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.sanitized_match.return_value = {"id": "clean123"}

        with patch.object(api, "service", mock_service):
            resp = self.client.post("/api/match/sanitized", json={"name": "Acme"})
            assert resp.status_code == 200
            assert resp.json() == {"id": "clean123"}

    def test_sanitized_match_not_found(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.sanitized_match.return_value = None

        with patch.object(api, "service", mock_service):
            resp = self.client.post("/api/match/sanitized", json={"name": "Ghost"})
            assert resp.status_code == 200
            assert resp.json() == {"message": "No match found"}

    # ---------------------------------------------------------
    # /api/match-top/sanitized
    # ---------------------------------------------------------
    def test_sanitized_match_top(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.sanitized_match_top.return_value = {"id": "top_clean"}

        with patch.object(api, "service", mock_service):
            resp = self.client.post("/api/match-top/sanitized", json={"name": "Acme"})
            assert resp.status_code == 200
            assert resp.json() == {"id": "top_clean"}

    def test_sanitized_match_top_not_found(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.sanitized_match_top.return_value = None

        with patch.object(api, "service", mock_service):
            resp = self.client.post("/api/match-top/sanitized", json={"name": "Ghost"})
            assert resp.status_code == 200
            assert resp.json() == {"message": "No match found"}
