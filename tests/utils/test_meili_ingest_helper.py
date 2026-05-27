# tests/utils/test_meili_ingest_helper.py

from unittest.mock import patch, MagicMock
import pytest

from app.utils import meili_ingest_helper


class TestMeiliIngestHelper:
    @pytest.fixture(autouse=True)
    def _setup(self):
        # common patches can go here later if needed
        yield

    @pytest.fixture
    def mock_file_loader_open(self):
        with patch("app.utils.meili_ingest_helper.FileLoader.open_file") as m:
            m.return_value.__enter__.return_value = MagicMock()
            yield m

    @pytest.fixture
    def mock_requests_post(self):
        with patch("app.utils.meili_ingest_helper.requests.post") as m:
            yield m

    def test_ingest_success_local(self, mock_file_loader_open, mock_requests_post, monkeypatch):
        monkeypatch.setattr("app.utils.meili_ingest_helper.APP_ENV", "local")
        monkeypatch.setattr("app.utils.meili_ingest_helper.Path.exists", lambda *_: True)

        mock_requests_post.return_value.status_code = 202
        mock_requests_post.return_value.text = "ok"

        result = meili_ingest_helper.ingest_ndjson(
            url="http://localhost:7700",
            index_name="companies",
            file_path="data/meili_final.jsonl"
        )

        assert result["ok"] is True
        assert result["status"] == 202
        assert result["response"] == "ok"

    def test_ingest_missing_file_local(self, monkeypatch):
        monkeypatch.setattr("app.utils.meili_ingest_helper.APP_ENV", "local")
        monkeypatch.setattr("app.utils.meili_ingest_helper.Path.exists", lambda *_: False)

        result = meili_ingest_helper.ingest_ndjson(
            file_path="missing.jsonl"
        )

        assert result["ok"] is False
        assert "not found" in result["error"]

    def test_ingest_s3_missing(self, monkeypatch):
        monkeypatch.setattr("app.utils.meili_ingest_helper.APP_ENV", "prod")

        mock_s3 = MagicMock()
        mock_s3.head_object.side_effect = Exception("nope")

        with patch("app.utils.meili_ingest_helper.boto3.client", return_value=mock_s3):
            result = meili_ingest_helper.ingest_ndjson(
                file_path="data/meili_top.jsonl"
            )

        assert result["ok"] is False
        assert "not found" in result["error"]

    def test_ingest_request_failure(self, mock_file_loader_open, mock_requests_post, monkeypatch):
        monkeypatch.setattr("app.utils.meili_ingest_helper.APP_ENV", "local")
        monkeypatch.setattr("app.utils.meili_ingest_helper.Path.exists", lambda *_: True)

        mock_requests_post.side_effect = Exception("connection error")

        result = meili_ingest_helper.ingest_ndjson(
            file_path="data/meili_final.jsonl"
        )

        assert result["ok"] is False
        assert "failed" in result["error"]
