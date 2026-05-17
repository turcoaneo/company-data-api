# tests/api/test_matcher_api.py

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI


class TestMatcherAPI:

    @pytest.fixture(autouse=True)
    def setup_client(self):
        # Patch meilisearch.Client BEFORE importing matcher.api
        with patch("matcher.service.meilisearch.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_index = MagicMock()
            mock_client.index.return_value = mock_index
            mock_client_cls.return_value = mock_client

            # Import inside the patch context so MatcherService uses the mocked client
            from matcher.api import matcher_router

            app = FastAPI()
            app.include_router(matcher_router)
            self.client = TestClient(app)

            # expose for tests if needed
            self._mock_client = mock_client
            self._mock_index = mock_index

            yield  # let the tests run

    # ---------------------------------------------------------
    # /api/match
    # ---------------------------------------------------------
    def test_match_company_found(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.match.return_value = {"id": "abc123"}

        with patch.object(api, "service", mock_service):
            resp = self.client.post("/api/match", json={"name": "Acme"})
            assert resp.status_code == 200
            assert resp.json() == {"id": "abc123"}

    def test_match_company_not_found(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.match.return_value = None

        with patch.object(api, "service", mock_service):
            resp = self.client.post("/api/match", json={"name": "Unknown"})
            assert resp.status_code == 200
            assert resp.json() == {"message": "No match found"}

    # ---------------------------------------------------------
    # /api/search
    # ---------------------------------------------------------
    def test_search(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.search.return_value = {"hits": [{"id": "1"}]}

        with patch.object(api, "service", mock_service):
            resp = self.client.get("/api/search?q=acme")
            assert resp.status_code == 200
            assert resp.json() == {"hits": [{"id": "1"}]}

    # ---------------------------------------------------------
    # /api/suggest
    # ---------------------------------------------------------
    def test_suggest(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.suggest.return_value = {"hits": [{"id": "1"}]}

        with patch.object(api, "service", mock_service):
            resp = self.client.get("/api/suggest?prefix=ac")
            assert resp.status_code == 200
            assert resp.json() == {"hits": [{"id": "1"}]}

    # ---------------------------------------------------------
    # /api/match/sample
    # ---------------------------------------------------------
    def test_match_sample(self):
        from matcher import api

        mock_service = MagicMock()
        mock_service.match_sample.return_value = [
            {"input": {"name": "Acme"}, "output": {"id": "123"}}
        ]

        with patch.object(api, "service", mock_service):
            resp = self.client.get("/api/match/sample")
            assert resp.status_code == 200
            assert resp.json() == [
                {"input": {"name": "Acme"}, "output": {"id": "123"}}
            ]
