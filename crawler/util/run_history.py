# crawler/util/run_history.py

import json

from app.utils.env_vars import PATHS
from app.utils.logger_util import get_logger

logger = get_logger()


def _count_contacts(jsonl_path: str):
    """
    Count non-empty phones/socials in a JSONL file.
    Works for both local FS and S3 via FileLoader.
    """
    phones = 0
    socials = 0

    from app.utils.file_loader import FileLoader
    fl = FileLoader()

    try:
        with fl.open_file(jsonl_path, "r", encoding="utf-8") as f:
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
    except Exception as e:
        # File may not exist yet (first run, etc.)
        logger.warning(f"Could not open JSONL for counting contacts: {jsonl_path} ({e})")

    return phones, socials


def record_run(
        start_ts: str,
        duration: float,
        config: list,
        final_res_file: str = None,
        history_res_file: str = None
):
    """
    Append a run summary to history_runs.jsonl.
    start_ts: timestamp extracted from results_YYYYMMDD_HHMMSS.jsonl
    duration: seconds
    config: [mp_chunks, domain_concurrency, domains_in_parallel]
    """

    # Initial results file (first pass)
    results_file = f"data/results_{start_ts}.jsonl"

    # Final merged file
    final_file = PATHS["path_final_result"] if final_res_file is None else final_res_file

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

    history_path = PATHS["path_history_result"] if history_res_file is None else history_res_file

    # Load existing history (if any), stack-like (newest on top)
    existing_lines: list[str] = []
    from app.utils.file_loader import FileLoader
    fl = FileLoader()

    try:
        with fl.open_file(history_path, "r", encoding="utf-8") as f:
            existing_lines = [line.rstrip("\n") for line in f if line.strip()]
    except Exception as e:
        logger.warning(f"No history yet, that's fine: {e}")

    # Write new history with newest entry first
    with fl.open_file(history_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        for line in existing_lines:
            f.write(line + "\n")

    logger.info(f"Recorded run history entry for {start_ts}")
