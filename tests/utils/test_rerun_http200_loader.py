import json
import tempfile
from qa.rerun_http200 import load_http_200_domains


class TestLoadHttp200Domains:

    def test_loads_domains_from_list(self):
        sample = {
            "http_200": [
                "hautesalonjc.com",
                "romesportshalloffame.com",
                "sbmobilenails.com",
                "carrettausa.com",
                "sanctuaryfarmphila.org"
            ]
        }

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
            json.dump(sample, f)
            f.flush()

            result = load_http_200_domains(f.name)

        assert result == [
            "hautesalonjc.com",
            "romesportshalloffame.com",
            "sbmobilenails.com",
            "carrettausa.com",
            "sanctuaryfarmphila.org",
        ]

    def test_missing_key_returns_empty_list(self):
        sample = {"other": ["x.com"]}

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
            json.dump(sample, f)
            f.flush()

            result = load_http_200_domains(f.name)

        assert result == []

    def test_ignores_non_string_entries(self):
        sample = {"http_200": ["valid.com", 123, None, {}, " another.com "]}

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as f:
            json.dump(sample, f)
            f.flush()

            result = load_http_200_domains(f.name)

        assert result == ["valid.com", "another.com"]
