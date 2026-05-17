# tests/benchmark/test_benchmark_suggest.py

import csv
import json
import random

from fastapi import FastAPI
from fastapi.testclient import TestClient

from matcher.api import matcher_router


class TestSuggestBenchmark:
    output_path = None

    @classmethod
    def setup_class(cls):
        app = FastAPI()
        app.include_router(matcher_router)
        cls.client = TestClient(app)

        # Input + output paths
        from app.utils.path_util import get_project_root
        cls.input_path = get_project_root() / "tests/benchmark/api-input-sample.csv"
        cls.output_path = get_project_root() / "tests/benchmark/results_benchmark_suggest.jsonl"
        cls.output_path.write_text("")

    def test_suggest_prefixes(self):
        assert self.input_path.exists()

        with open(self.input_path, newline="", encoding="utf-8") as f:
            reader: csv.DictReader = csv.DictReader(f)

            for row in reader:
                name = row.get("input name")
                if not name:
                    continue

                prefix = name[: random.randint(2, 5)]

                resp = self.client.get(f"/api/suggest?prefix={prefix}&limit=5")
                assert resp.status_code == 200

                result = {
                    "prefix": prefix,
                    "response": resp.json(),
                }

                with open(self.output_path, "a", encoding="utf-8") as out:
                    out.write(json.dumps(result) + "\n")

        assert self.output_path.stat().st_size > 0
