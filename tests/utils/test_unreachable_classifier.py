# tests/utils/test_unreachable_classifier.py

import json
import tempfile
import os

from qa.unreachable_classifier import (
    classify_unreachable_reason,
    classify_csv_to_json,
)


class TestUnreachableClassifier:

    def test_classify_unreachable_reason(self):
        assert classify_unreachable_reason("DNS resolution failed") == "dns_error"
        assert classify_unreachable_reason("getaddrinfo failed") == "dns_error"
        assert classify_unreachable_reason("403 Forbidden (Cloudflare bot protection)") == "blocked_by_cloudflare"
        assert classify_unreachable_reason("HTTP 409") == "cloudflare_conflict"
        assert classify_unreachable_reason("HTTP 521") == "origin_down_cloudflare"
        assert classify_unreachable_reason("HTTP 404") == "http_404"
        assert classify_unreachable_reason("ServerDisconnectedError") == "server_disconnected"
        assert classify_unreachable_reason("SSL error: something") == "ssl_error"
        assert classify_unreachable_reason("Timeout") == "timeout"
        assert classify_unreachable_reason("Connection error: something") == "connection_error"

    def test_classify_csv_to_json(self):
        # Create a temporary CSV
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "bad_urls_report.csv")
            json_path = os.path.join(tmpdir, "bad_urls_report.json")

            with open(csv_path, "w", encoding="utf-8") as f:
                f.write("domain,status,protocol,reason\n")
                f.write("example.com,unreachable,,DNS resolution failed\n")
                f.write("blocked.com,unreachable,,403 Forbidden (Cloudflare bot protection)\n")

            results = classify_csv_to_json(csv_path, json_path)

            assert len(results) == 2
            assert results[0]["category"] == "dns_error"
            assert results[1]["category"] == "blocked_by_cloudflare"

            # Verify JSON file exists and is valid
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert len(data) == 2
                assert data[0]["domain"] == "example.com"
                assert data[1]["category"] == "blocked_by_cloudflare"
