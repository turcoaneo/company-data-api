# tests/service/test_matcher_service.py

from unittest.mock import MagicMock, patch

import pytest

from matcher.service import MatcherService


# noinspection PyUnresolvedReferences
class TestMatcherService:

    @pytest.fixture
    def svc(self):
        with patch("matcher.service.meilisearch.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_index = MagicMock()
            mock_client.index.return_value = mock_index
            mock_client_cls.return_value = mock_client

            service = MatcherService()
            service._mock_index = mock_index

            return service

    # ---------------------------------------------------------
    # _search_single
    # ---------------------------------------------------------
    def test_search_single_hit(self, svc):
        svc._mock_index.search.return_value = {"hits": [{"id": "123"}]}
        hit = svc._search_single("acme", ["company_commercial_name"])
        assert hit == {"id": "123"}

    def test_search_single_no_hit(self, svc):
        svc._mock_index.search.return_value = {"hits": []}
        hit = svc._search_single("acme", ["company_commercial_name"])
        assert hit is None

    # ---------------------------------------------------------
    # match()
    # ---------------------------------------------------------
    def test_match_name_first(self, svc):
        svc._mock_index.search.return_value = {"hits": [{"id": "name_hit"}]}
        hit = svc.match(name="Acme")
        assert hit == {"id": "name_hit"}

    def test_match_fallback_to_domain(self, svc):
        svc._mock_index.search.side_effect = [
            {"hits": []},  # name
            {"hits": [{"id": "dom"}]},  # domain
        ]
        hit = svc.match(name="X", website="acme.com")
        assert hit == {"id": "dom"}

    def test_match_none(self, svc):
        svc._mock_index.search.return_value = {"hits": []}
        hit = svc.match(name="X")
        assert hit is None

    # ---------------------------------------------------------
    # search()
    # ---------------------------------------------------------
    def test_search(self, svc):
        svc._mock_index.search.return_value = {"hits": [{"id": "1"}]}
        resp = svc.search("acme")
        assert resp == {"hits": [{"id": "1"}]}

    # ---------------------------------------------------------
    # suggest()
    # ---------------------------------------------------------
    def test_suggest(self, svc):
        svc._mock_index.search.return_value = {"hits": [{"id": "1"}]}
        resp = svc.suggest("ac")
        assert resp == {"hits": [{"id": "1"}]}
