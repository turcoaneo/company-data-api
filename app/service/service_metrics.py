# app/service/service_metrics.py

from pathlib import Path
from crawler.util.metrics_analyzer import compute_scraper_metrics


def find_latest_results_file() -> str | None:
    """
    Returns the latest results_*.jsonl file from /data.
    """
    data_dir = Path("data")
    files = list(data_dir.glob("results_*.jsonl"))
    if not files:
        return None
    latest = max(files, key=lambda p: p.stat().st_mtime)
    return str(latest)


def run_metrics():
    initial_jsonl = find_latest_results_file()
    if not initial_jsonl:
        # fallback for first run or missing files
        initial_jsonl = "results_latest.jsonl"

    return compute_scraper_metrics(
        input_csv_path="data/sample-websites-company-names.csv",
        bad_urls_path="bad_urls.txt",
        missing_contacts_path="missing_contacts.txt",
        initial_jsonl_path=initial_jsonl,
        final_jsonl_path="final_result.jsonl",
    )
