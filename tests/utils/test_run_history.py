# tests/utils/test_run_history.py

import json
from pathlib import Path

import pytest

from crawler.util.run_history import record_run


class TestRunHistory:

    @pytest.fixture
    def tmp_results(self, tmp_path):
        """
        Creates a fake results_YYYYMMDD_HHMMSS.jsonl and final_result.jsonl
        inside a temporary directory.
        """
        # Switch working directory to tmp_path for the duration of the test
        old_cwd = Path.cwd()
        import os
        try:
            os.chdir(tmp_path)

            # Create initial results file
            initial = tmp_path / "results_20260515_061008.jsonl"
            initial.write_text(
                "\n".join([
                    json.dumps({"phones": ["+401"], "socials": []}),
                    json.dumps({"phones": [], "socials": ["fb"]}),
                    json.dumps({"phones": [], "socials": []}),
                ]),
                encoding="utf-8"
            )

            # Create final results file
            final = tmp_path / "final_result.jsonl"
            final.write_text(
                "\n".join([
                    json.dumps({"phones": ["+402"], "socials": ["ig"]}),
                    json.dumps({"phones": [], "socials": ["tw"]}),
                ]),
                encoding="utf-8"
            )

            yield tmp_path
        finally:
            os.chdir(old_cwd)

    def test_record_run_creates_history_entry(self, tmp_results):
        """
        Ensures record_run() writes a correct entry into history_runs.jsonl
        with initial/final counts, config, and duration.
        """
        ts = "20260515_061008"
        duration = 12.345
        config = [2, 2, 4]

        # Execute
        record_run(start_ts=ts, duration=duration, config=config)

        history_file = tmp_results / "history_runs.jsonl"
        assert history_file.exists()

        # Read first (newest) entry
        lines = history_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 1

        entry = json.loads(lines[0])
        assert ts in entry

        data = entry[ts]

        # Validate counts
        assert data["initial"] == [1, 1]      # 1 phone, 1 social
        assert data["final"] == [1, 2]        # 1 phone, 2 socials

        # Validate config + duration
        assert data["config"] == config
        assert data["duration"] == pytest.approx(duration, rel=1e-3)

    def test_record_run_stacks_entries(self, tmp_results):
        """
        Ensures new entries are prepended (stack behavior).
        """
        # First entry
        record_run("20260101_000000", 1.0, [1, 1, 1])
        # Second entry (should appear first)
        record_run("20260102_000000", 2.0, [2, 2, 2])

        history_file = tmp_results / "history_runs.jsonl"
        lines = history_file.read_text(encoding="utf-8").strip().splitlines()

        assert len(lines) == 2

        first = json.loads(lines[0])
        second = json.loads(lines[1])

        assert "20260102_000000" in first
        assert "20260101_000000" in second
