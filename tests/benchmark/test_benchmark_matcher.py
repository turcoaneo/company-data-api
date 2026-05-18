# tests/benchmark/test_benchmark_matcher.py

import csv
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from matcher.api import matcher_router


class TestBenchmarkMatcher:
    output_path = None

    @classmethod
    def setup_class(cls):
        app = FastAPI()
        app.include_router(matcher_router)
        cls.client = TestClient(app)

        # Input + output paths
        from app.utils.path_util import get_project_root
        cls.input_path = get_project_root() / "tests/benchmark/api-input-sample.csv"
        cls.output_path = get_project_root() / "tests/benchmark/results_benchmark_match.jsonl"

        # Ensure output file is empty
        cls.output_path.write_text("")

    def test_match_benchmark_with_coverage(self):
        assert self.input_path.exists()

        with open(self.input_path, newline="", encoding="utf-8") as f:
            reader: csv.DictReader = csv.DictReader(f)

            for row in reader:
                payload = {
                    "name": row.get("input name") or None,
                    "phone": row.get("input phone") or None,
                    "website": row.get("input website") or None,
                    "facebook": row.get("input_facebook") or None,
                }

                resp = self.client.post("/api/match", json=payload)
                assert resp.status_code == 200

                output = resp.json()

                # Coverage check: does any output field contain any input token?
                coverage = False
                input_tokens = [
                    str(v).lower()
                    for v in payload.values()
                    if v and isinstance(v, str)
                ]

                if isinstance(output, dict):
                    for out_val in output.values():
                        if isinstance(out_val, str):
                            out_val_low = out_val.lower()
                            if any(tok in out_val_low for tok in input_tokens):
                                coverage = True
                                break

                result = {
                    "input": payload,
                    "output": output,
                    "coverage": coverage,
                }

                with open(self.output_path, "a", encoding="utf-8") as out:
                    out.write(json.dumps(result) + "\n")

        assert self.output_path.stat().st_size > 0
