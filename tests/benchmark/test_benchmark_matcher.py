# tests/benchmark/test_benchmark_matcher.py

import csv
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from matcher.api import matcher_router


class TestMatcherBenchmark:
    output_path = None

    @classmethod
    def setup_class(cls):
        # Build real API client
        app = FastAPI()
        app.include_router(matcher_router)
        cls.client = TestClient(app)

        # Input + output paths
        from app.utils.path_util import get_project_root
        cls.input_path = get_project_root() / "tests/benchmark/api-input-sample.csv"
        cls.output_path = get_project_root() / "tests/benchmark/results_benchmark_match.jsonl"

        # Ensure output file is empty
        cls.output_path.write_text("")

    def test_benchmark_matcher(self):
        assert self.input_path.exists(), "Input CSV missing"

        with open(self.input_path, newline="", encoding="utf-8") as f:
            reader: csv.DictReader = csv.DictReader(f)

            for row in reader:
                payload = {
                    "name": row.get("input name") or None,
                    "phone": row.get("input phone") or None,
                    "website": row.get("input website") or None,
                    "facebook": row.get("input_facebook") or None,
                }

                # Call real API
                resp = self.client.post("/api/match", json=payload)
                assert resp.status_code == 200

                result = {
                    "input": payload,
                    "output": resp.json(),
                }

                # Append to results.jsonl
                with open(self.output_path, "a", encoding="utf-8") as out:
                    out.write(json.dumps(result) + "\n")

        # Final assertion: file must not be empty
        assert self.output_path.stat().st_size > 0
