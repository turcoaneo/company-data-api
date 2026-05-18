# crawler/util/history_summary.py

import json
from pathlib import Path

from app.utils.env_vars import PATHS


def load_history_summary(history_path: str = PATHS["path_history_result"]) -> dict:
    """
    Returns a dict:
    {
        "20260516_090820": {
            "phones": 370,
            "socials": 313,
            "chunks_conc_par": [3,3,3],
            "duration": 453.061,
            "isp_org": "AS8953"
        },
        ...,
    }
    """
    path = Path(history_path)
    if not path.exists():
        return {}

    summary = {}

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)
            ts = next(iter(entry.keys()))
            data = entry[ts]

            phones = data["final"][0]
            socials = data["final"][1]
            cfg = data["config"]
            duration = data["duration"]
            isp_org = data.get("isp_org", "")

            # Extract only ASN prefix (e.g. "AS8953")
            isp_short = isp_org.split()[0] if isp_org else ""

            summary[ts] = {
                "phones": phones,
                "socials": socials,
                "chunks_conc_par": cfg,
                "duration": duration,
                "isp_org": isp_short,
            }

    return summary
