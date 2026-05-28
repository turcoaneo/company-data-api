# tests/service/test_service_anomalies.py

from unittest.mock import patch
from app.service.service_anomalies import get_contact_anomalies


class TestServiceAnomalies:

    @patch("app.service.service_anomalies.classify_contacts_jsonl")
    def test_get_contact_anomalies(self, mock_classifier):
        mock_classifier.return_value = {
            "too_many_phones": ["aaa.com"],
            "too_many_socials": ["bbb.com"],
            "socials_mismatch": ["ccc.com"],
            "details": {"ignored.com": {}},
        }

        result = get_contact_anomalies()

        assert result["too_many_phones"] == ["aaa.com"]
        assert result["too_many_socials"] == ["bbb.com"]
        assert result["socials_mismatch"] == ["ccc.com"]

        mock_classifier.assert_called_once()
