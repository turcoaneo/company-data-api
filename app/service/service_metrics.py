# app/service/service_metrics.py

from crawler.util.metrics_analyzer import compute_scraper_metrics


def run_metrics():
    return compute_scraper_metrics(
        input_csv_path="data/sample-websites-company-names.csv",
        bad_urls_path="bad_urls.txt",
        missing_contacts_path="missing_contacts.txt",
        initial_jsonl_path="results_latest.jsonl",   # or your timestamped file
        final_jsonl_path="final_result.jsonl",
    )
