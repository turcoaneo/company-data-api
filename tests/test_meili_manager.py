# tests/test_meili_manager.py

import pytest
from unittest.mock import patch, MagicMock
from meili_manager import MeiliManager


class TestMeiliManager:

    @pytest.fixture(autouse=True)
    def setup_manager(self):
        self.manager = MeiliManager(url="http://localhost:7700", index_name="companies")

    # ---------------------------------------------------------
    # HEALTH CHECK
    # ---------------------------------------------------------
    def test_is_running_true(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            assert self.manager.is_running() is True

    def test_is_running_false(self):
        with patch("requests.get", side_effect=Exception("boom")):
            assert self.manager.is_running() is False

    # ---------------------------------------------------------
    # AUTO-START (docker run)
    # ---------------------------------------------------------
    def test_start_meili(self):
        with patch("subprocess.Popen") as mock_popen:
            self.manager.start_meili()
            mock_popen.assert_called_once()

    # ---------------------------------------------------------
    # WAIT UNTIL READY
    # ---------------------------------------------------------
    def test_wait_until_ready_success(self):
        with patch.object(self.manager, "is_running", side_effect=[False, False, True]):
            self.manager.wait_until_ready(timeout=2)

    def test_wait_until_ready_timeout(self):
        with patch.object(self.manager, "is_running", return_value=False):
            with pytest.raises(RuntimeError):
                self.manager.wait_until_ready(timeout=1)

    # ---------------------------------------------------------
    # CONNECT
    # ---------------------------------------------------------
    def test_connect(self):
        with patch("meilisearch.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            self.manager.connect()

            assert self.manager.client is mock_instance
            mock_instance.index.assert_called_with("companies")
            assert self.manager.index == mock_instance.index.return_value

    # ---------------------------------------------------------
    # CREATE + CONFIGURE INDEX
    # ---------------------------------------------------------
    def test_create_and_configure_index(self):
        mock_client = MagicMock()
        mock_index = MagicMock()

        # client.index() must return our mock_index
        mock_client.index.return_value = mock_index

        self.manager.client = mock_client

        self.manager.create_and_configure_index()

        mock_client.create_index.assert_called_once()
        mock_index.update_searchable_attributes.assert_called_once()
        mock_index.update_filterable_attributes.assert_called_once()
        mock_index.update_sortable_attributes.assert_called_once()
        mock_index.update_ranking_rules.assert_called_once()

    # ---------------------------------------------------------
    # INGEST NDJSON
    # ---------------------------------------------------------
    def test_ingest_ndjson(self, tmp_path):
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"id": "1"}\n')

        with patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 202
            mock_post.return_value.text = '{"taskUid":1}'

            self.manager.ingest_ndjson(str(file_path))

            assert mock_post.call_count == 1
