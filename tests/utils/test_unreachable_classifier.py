# tests/test_unreachable_classifier.py

import json
import tempfile
import os
import asyncio

from qa.unreachable_classifier import classify_csv_to_json_sync, classify_reason


class TestUnreachableClassifier:

    def test_classify_reason(self):
        assert classify_reason("DNS resolution failed") == "dns_error"
        assert classify_reason("getaddrinfo failed") == "dns_error"
        assert classify_reason("HTTPS: Timeout") == "timeout"
        assert classify_reason("SSL error: something") == "ssl_error"
        assert classify_reason("ServerDisconnectedError") == "server_disconnected"
        assert classify_reason("Connection error: x") == "connection_error"
        assert classify_reason("403 Forbidden (Cloudflare bot protection)") == "blocked_by_cloudflare"
        assert classify_reason("HTTP 404") == "http_404"
        assert classify_reason("HTTP 521") == "http_521"

    def test_classify_csv_to_json_sync(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "bad_urls_report.csv")
            json_path = os.path.join(tmpdir, "bad_urls_report.json")

            with open(csv_path, "w", encoding="utf-8") as f:
                f.write("domain,status,protocol,reason\n")
                f.write("a.com,unreachable,,DNS resolution failed\n")
                f.write("b.com,unreachable,,HTTPS: HTTP 404 | HTTP: HTTP 404\n")
                f.write("c.com,unreachable,,HTTPS: 403 Forbidden (Cloudflare bot protection)\n")

            categories = asyncio.run(classify_csv_to_json_sync(csv_path, json_path))

            assert "dns_error" in categories
            assert "http_404" in categories
            assert "blocked_by_cloudflare" in categories

            assert categories["dns_error"] == ["a.com"]
            assert categories["http_404"] == ["b.com"]
            assert categories["blocked_by_cloudflare"] == ["c.com"]

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert "dns_error" in data
                assert "http_404" in data
                assert "blocked_by_cloudflare" in data
