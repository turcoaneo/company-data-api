# app/utils/env_vars.py

import os

from dotenv import dotenv_values

# Load base + environment-specific config
base_env = dotenv_values(".env")
env_specific = dotenv_values(f".env.{os.environ.get('APP_ENV', 'test')}")
merged = {**base_env, **env_specific, **os.environ}
APP_ENV = merged.get("APP_ENV", "test")

LOG_LEVEL = merged.get("LOG_LEVEL", "info")

SCRAPER_CONFIG = {
    "write_files": merged.get("SCRAPER_WRITE_FILES", "True") == "True",
    "shallow_crawl": merged.get("SCRAPER_SHALLOW_CRAWL", "True") == "True",
    "sync_saving": merged.get("SCRAPER_SYNC_SAVING", "True") == "True",
    "looped": merged.get("SCRAPER_JOB_LOOPED", "True") == "True",
    "cron_running": merged.get("SCRAPER_CRON_RUNNING", "False") == "True",
    "sleep_time": int(merged.get("SCRAPER_SLEEPING_TIME", 5)),
    "interval": int(merged.get("SCRAPER_INTERVAL_SECONDS", 5)),
    "mp_chunks": int(merged.get("SCRAPER_MULTI_PROCESSING_CHUNKS", 8)),
    "domain_concurrency": int(merged.get("SCRAPER_PER_DOMAIN_CONCURRENCY", 4)),
    "domains_in_parallel": int(merged.get("SCRAPER_MAX_DOMAINS_IN_PARALLEL", 8)),
}

MEILI = {
    "url": str(merged.get("MEILI_URL", str("http://localhost:7700"))),
    "index": str(merged.get("MEILI_INDEX", str("companies"))),
    "top_index": str(merged.get("MEILI_TOP_INDEX", str("top_result_companies"))),
    "internal_bootstrap": merged.get("MEILI_BOOTSTRAP_INTERNAL", "True") == "True",
}

PATHS = {
    "path_bad_urls": str(merged.get("PATHS_BAD_URLS", "results/bad_urls.txt")),
    "path_bad_urls_report_csv": str(merged.get("PATHS_BAD_URLS_REPORT_CSV", "results/bad_urls_report.csv")),
    "path_bad_urls_report_json": str(merged.get("PATHS_BAD_URLS_REPORT_JSON", "results/bad_urls_report.json")),
    "path_missing_contacts": str(merged.get("PATHS_MISSING_CONTACTS", "results/missing_contacts.txt")),
    "path_final_result": str(merged.get("PATHS_FINAL_RESULT", "results/final_result.jsonl")),
    "path_history_result": str(merged.get("PATHS_HISTORY_RESULT", "results/history_runs.jsonl")),
    "path_meili_final": str(merged.get("PATHS_MEILI_FINAL", "results/meili_final.jsonl")),
    "path_best_metric": str(merged.get("PATHS_BEST_METRIC", "results/best_metric.json")),
    "path_top_result": str(merged.get("PATHS_TOP_RESULT", "results/top_result.jsonl")),
    "path_meili_top": str(merged.get("PATHS_MEILI_TOP", "results/meili_top.jsonl")),
    "path_data_sample": str(merged.get("PATHS_DATA_SAMPLE", "data/sample-websites-company-names.csv")),
    "path_api_input": str(merged.get("PATHS_API_INPUT", "data/api-input-sample.csv")),
}

S3_BUCKET = merged.get("S3_BUCKET", "company-api-bucket")
