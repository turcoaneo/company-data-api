# tests/service/test_service_history.py

import json

from app.service.service_history import get_history_summary


class TestServiceHistory:

    def test_history_summary(self, tmp_path, monkeypatch):
        # Create fake history_runs.jsonl
        history = tmp_path / "history_runs.jsonl"
        history.write_text(
            "\n".join([
                json.dumps({
                    "20260516_090820": {
                        "initial": [365, 310],
                        "final": [370, 313],
                        "config": [3, 3, 3],
                        "duration": 453.061,
                        "ip": "128.127.122.238",
                        "isp_org": "AS8953 Orange Romania S.A.",
                        "asn": "unknown"
                    }
                }),
                json.dumps({
                    "20260516_085755": {
                        "initial": [345, 288],
                        "final": [345, 288],
                        "config": [4, 2, 4],
                        "duration": 143.48,
                        "ip": "213.233.88.209",
                        "isp_org": "AS12302 Vodafone Romania S.A.",
                        "asn": "unknown"
                    }
                }),
            ]),
            encoding="utf-8"
        )

        # Patch working directory so service reads tmp file
        monkeypatch.chdir(tmp_path)

        summary = get_history_summary()

        assert "20260516_090820" in summary
        assert summary["20260516_090820"]["phones"] == 370
        assert summary["20260516_090820"]["socials"] == 313
        assert summary["20260516_090820"]["chunks_conc_par"] == [3, 3, 3]
        assert summary["20260516_090820"]["isp_org"] == "AS8953"

        assert "20260516_085755" in summary
        assert summary["20260516_085755"]["isp_org"] == "AS12302"
