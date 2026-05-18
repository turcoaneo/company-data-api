# app/service/service_metrics.py

from pathlib import Path

from crawler.util.metrics_analyzer import compute_latest_and_top_metrics


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
    from app.utils.env_vars import PATHS
    initial_jsonl = find_latest_results_file()
    if not initial_jsonl:
        # fallback for first run or missing files
        initial_jsonl = "results_latest.jsonl"

    return compute_latest_and_top_metrics(
        input_csv_path="data/sample-websites-company-names.csv",
        bad_urls_path=PATHS["path_bad_urls"],
        missing_contacts_path=PATHS["path_missing_contacts"],
        initial_jsonl_path=initial_jsonl,
        final_jsonl_path=PATHS["path_final_result"],
        top_metrics_path=PATHS["path_best_metric"],
        top_result_path=PATHS["path_top_result"],
    )
