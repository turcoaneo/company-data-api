# app/utils/env_vars.py

import os

from dotenv import dotenv_values


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
    "mp_chunks": int(merged.get("MULTI_PROCESSING_CHUNKS", 8)),
    "domain_concurrency": int(merged.get("PER_DOMAIN_CONCURRENCY", 4)),
    "domains_in_parallel": int(merged.get("MAX_DOMAINS_IN_PARALLEL", 8)),
}
