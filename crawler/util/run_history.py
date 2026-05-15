# crawler/util/run_history.py

import json
from pathlib import Path

from app.utils.logger_util import get_logger

logger = get_logger()


def _count_contacts(jsonl_path: Path):
    """Count non-empty phones/socials in a JSONL file."""
    phones = 0
    socials = 0

    if not jsonl_path.exists():
        return phones, socials

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception as e:
                logger.error(f"History extract line error for {line}: {e}")
                continue

            if obj.get("phones"):
                phones += 1
            if obj.get("socials"):
                socials += 1

    return phones, socials


def record_run(start_ts: str, duration: float, config: list):
    """
    Append a run summary to history_runs.jsonl.
    start_ts: timestamp extracted from results_YYYYMMDD_HHMMSS.jsonl
    duration: seconds
    config: [mp_chunks, domain_concurrency, domains_in_parallel]
    """

    # Find initial results file
    results_file = Path(f"data/results_{start_ts}.jsonl")
    final_file = Path("final_result.jsonl")

    initial_counts = _count_contacts(results_file)
    final_counts = _count_contacts(final_file)

    from crawler.util.ip_util import get_isp_info

    isp = get_isp_info()

    entry = {
        start_ts: {
            "initial": list(initial_counts),
            "final": list(final_counts),
            "config": config,
            "duration": round(duration, 3),
            "ip": isp["ip"],
            "isp_org": isp["org"],
            "asn": isp["asn"],
        }
    }

    history_path = Path("history_runs.jsonl")

    # Append the newest entry at the top (stack-like)
    if history_path.exists():
        existing = history_path.read_text(encoding="utf-8").strip().splitlines()
    else:
        existing = []

    with history_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        for line in existing:
            f.write(line + "\n")

    logger.info(f"Recorded run history entry for {start_ts}")
