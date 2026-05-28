# tests/service/test_matcher_service_sanitized.py

from unittest.mock import MagicMock, patch
import pytest

from matcher.service import MatcherService


# noinspection PyUnresolvedReferences
class TestMatcherServiceSanitized:

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
    # _normalize_field
    # ---------------------------------------------------------
    def test_normalize_field(self, svc):
        assert svc._normalize_field("..") is None
        assert svc._normalize_field("   ") is None
        assert svc._normalize_field("---") is None
        assert svc._normalize_field("abc") == "abc"
        assert svc._normalize_field(" steppir.com ") == "steppir.com"

    # ---------------------------------------------------------
    # sanitized_match() should skip garbage name and use website
    # ---------------------------------------------------------
    def test_sanitized_match_ignores_punctuation_name(self, svc):
        # First call: name search (skipped because name=None)
        # Second call: website search → returns hit
        svc._mock_index.search.side_effect = [
            {"hits": [{"id": "steppir"}]},
        ]

        hit = svc.sanitized_match(name="..", website="steppir.com")
        assert hit == {"id": "steppir"}

    # ---------------------------------------------------------
    # sanitized_match_top()
    # ---------------------------------------------------------
    def test_sanitized_match_top(self, svc):
        svc._mock_index.search.return_value = {"hits": [{"id": "top"}]}
        hit = svc.sanitized_match_top(name="..", website="steppir.com")
        assert hit == {"id": "top"}

    # ---------------------------------------------------------
    # sanitized_match should behave like match when input is clean
    # ---------------------------------------------------------
    def test_sanitized_match_clean(self, svc):
        svc._mock_index.search.return_value = {"hits": [{"id": "clean"}]}
        hit = svc.sanitized_match(name="Acme")
        assert hit == {"id": "clean"}

    # ---------------------------------------------------------
    # sanitized_match should return None when nothing matches
    # ---------------------------------------------------------
    def test_sanitized_match_none(self, svc):
        svc._mock_index.search.return_value = {"hits": []}
        hit = svc.sanitized_match(name="Acme")
        assert hit is None
