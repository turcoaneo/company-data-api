# app/utils/env_vars.py

import os

from dotenv import dotenv_values

from app.utils.path_util import get_project_root

# Load base + environment-specific config
base_env = dotenv_values(".env")
env_specific = dotenv_values(f".env.{os.environ.get('APP_ENV', 'test')}")
merged = {**base_env, **env_specific, **os.environ}
APP_ENV = merged.get("APP_ENV", "test")

LOG_LEVEL = merged.get("LOG_LEVEL", "warning")

SCRAPER_CONFIG = {
    "write_files": merged.get("SCRAPER_WRITE_FILES", "True") == "True",
    "shallow_crawl": merged.get("SCRAPER_SHALLOW_CRAWL", "True") == "True",
    "sync_saving": merged.get("SCRAPER_SYNC_SAVING", "True") == "True",
    "looped": merged.get("SCRAPER_JOB_LOOPED", "True") == "True",
    "sleep_time": int(merged.get("SCRAPER_SLEEPING_TIME", 5)),
    "interval": int(merged.get("SCRAPER_INTERVAL_SECONDS", 5)),
    "mp_chunks": int(merged.get("SCRAPER_MULTI_PROCESSING_CHUNKS", 8)),
    "domain_concurrency": int(merged.get("SCRAPER_PER_DOMAIN_CONCURRENCY", 4)),
    "domains_in_parallel": int(merged.get("SCRAPER_MAX_DOMAINS_IN_PARALLEL", 8)),
}

PATHS = {
    "path_bad_urls": str(merged.get("PATHS_BAD_URLS", str(get_project_root() / "results/bad_urls.txt"))),
    "path_bad_urls_report_csv":
        str(merged.get("PATHS_BAD_URLS_REPORT_CSV", str(get_project_root() / "results/bad_urls_report.csv"))),
    "path_bad_urls_report_json":
        str(merged.get("PATHS_BAD_URLS_REPORT_JSON", str(get_project_root() / "results/bad_urls_report.json"))),
    "path_missing_contacts": str(
        merged.get("PATHS_MISSING_CONTACTS", str(get_project_root() / "results/missing_contacts.txt"))),
    "path_final_result": str(
        merged.get("PATHS_FINAL_RESULT", str(get_project_root() / "results/final_result.jsonl"))),
    "path_history_result": str(
        merged.get("PATHS_HISTORY_RESULT", str(get_project_root() / "results/history_runs.jsonl"))),
    "path_meili_final": str(
        merged.get("PATHS_MEILI_FINAL", str(get_project_root() / "results/meili_final.jsonl"))),
    "path_best_metric": str(
        merged.get("PATHS_BEST_METRIC", str(get_project_root() / "results/best_metric.json"))),
    "path_top_result": str(
        merged.get("PATHS_TOP_RESULT", str(get_project_root() / "results/top_result.jsonl"))),
}
