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
    "sync_saving": merged.get("SCRAPER_SYNC_SAVING", "True") == "True",
    "looped": merged.get("SCRAPER_JOB_LOOPED", "True") == "True",
    "sleep_time": int(merged.get("SCRAPER_SLEEPING_TIME", 5)),
    "interval": int(merged.get("SCRAPER_INTERVAL_SECONDS", 5)),
}
