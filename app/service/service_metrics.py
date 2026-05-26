# app/service/service_metrics.py

from pathlib import Path

from crawler.util.metrics_analyzer import compute_latest_and_top_metrics


def find_latest_results_file() -> str | None:
    from app.utils.env_vars import APP_ENV, S3_BUCKET
    import boto3

    # LOCAL MODE
    if APP_ENV in ["local", "test"]:
        data_dir = Path("data")
        files = list(data_dir.glob("results_*.jsonl"))
        if not files:
            return None
        latest = max(files, key=lambda p: p.stat().st_mtime)
        return str(latest)

    # S3 MODE
    s3 = boto3.client("s3")
    resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="data/results_")

    if "Contents" not in resp:
        return None

    # S3 uses LastModified instead of mtime
    latest = max(resp["Contents"], key=lambda o: o["LastModified"])
    return latest["Key"]


def run_metrics():
    from app.utils.env_vars import PATHS
    initial_jsonl = find_latest_results_file()
    if not initial_jsonl:
        print("Can't find latest jsonl")
        return {}

    return compute_latest_and_top_metrics(
        input_csv_path=PATHS["path_data_sample"],
        bad_urls_path=PATHS["path_bad_urls"],
        missing_contacts_path=PATHS["path_missing_contacts"],
        initial_jsonl_path=initial_jsonl,
        final_jsonl_path=PATHS["path_final_result"],
        top_metrics_path=PATHS["path_best_metric"],
        top_result_path=PATHS["path_top_result"],
    )
