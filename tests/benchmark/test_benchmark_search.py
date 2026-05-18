# tests/benchmark/test_benchmark_search.py

import csv
import json
import random

from fastapi import FastAPI
from fastapi.testclient import TestClient

from matcher.api import matcher_router


class TestBenchmarkSearch:
    output_path = None

    @classmethod
    def setup_class(cls):
        app = FastAPI()
        app.include_router(matcher_router)
        cls.client = TestClient(app)

        # Input + output paths
        from app.utils.path_util import get_project_root
        cls.input_path = get_project_root() / "tests/benchmark/api-input-sample.csv"
        cls.output_path = get_project_root() / "tests/benchmark/results_benchmark_search.jsonl"
        cls.output_path.write_text("")

    def test_search_random_fields(self):
        assert self.input_path.exists()

        with open(self.input_path, newline="", encoding="utf-8") as f:
            reader: csv.DictReader = csv.DictReader(f)

            for row in reader:
                candidates = [
                    row.get("input name"),
                    row.get("input phone"),
                    row.get("input website"),
                    row.get("input_facebook"),
                ]
                candidates = [c for c in candidates if c]

                if not candidates:
                    continue

                query = random.choice(candidates)

                resp = self.client.get(f"/api/search?q={query}&limit=3")
                assert resp.status_code == 200

                result = {
                    "query": query,
                    "response": resp.json(),
                }

                with open(self.output_path, "a", encoding="utf-8") as out:
                    out.write(json.dumps(result) + "\n")

        assert self.output_path.stat().st_size > 0
