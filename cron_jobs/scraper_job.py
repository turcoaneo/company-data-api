# /cron_jobs/scraper_job.py

import threading
import time

from app.utils.env_vars import SCRAPER_CONFIG, APP_ENV
from app.utils.logger_util import get_logger
from app.utils.timing_util import elapsed_time
from crawler.scraper_runner import run_scraper

logger = get_logger('scraper_job')


@elapsed_time("run_scraper")
def run_job():
    import time
    from crawler.util.run_history import record_run
    from crawler.clean_files import clean_scraper_files

    start_time = time.time()

    clean_scraper_files()

    chunks = SCRAPER_CONFIG["mp_chunks"]
    domain_conc = SCRAPER_CONFIG["domain_concurrency"]
    domains_parallel = SCRAPER_CONFIG["domains_in_parallel"]

    # Run scraper
    if not chunks:
        import asyncio
        logger.info('Scraping')
        asyncio.run(run_scraper())
    else:
        logger.info('Scraping (multiprocess)')
        from crawler.mp_crawler import run_scraper_multiprocess
        run_scraper_multiprocess(num_chunks=chunks)

    # Extract timestamp from results_YYYYMMDD_HHMMSS.jsonl
    import re
    from pathlib import Path

    results_files = list(Path(".").glob("data/results_*.jsonl"))
    if results_files:
        # pick the latest by timestamp in filename
        latest = max(results_files, key=lambda p: p.stat().st_mtime)
        m = re.search(r"results_(\d{8}_\d{6})\.jsonl", latest.name)
        if m:
            ts = m.group(1)
        else:
            ts = "unknown"
    else:
        ts = "unknown"

    duration = time.time() - start_time

    # Record run history
    record_run(
        start_ts=ts,
        duration=duration,
        config=[chunks, domain_conc, domains_parallel]
    )

    if APP_ENV == 'local_debug':
        exit(0)


def start_scraper_loop(interval_sec: int = 1200, is_looped: bool = True):
    logger.info(f"Starting scraper - looped: {is_looped}")

    def loop_cron_job():
        while True:
            run_job()
            time.sleep(interval_sec)
            if not is_looped:
                break

    threading.Thread(target=loop_cron_job, daemon=True).start()


if __name__ == "__main__":
    looped = SCRAPER_CONFIG["looped"]
    interval_seconds = int(SCRAPER_CONFIG["interval"])
    sleeping_time = int(SCRAPER_CONFIG["sleep_time"])
    logger.debug(
        f"Starting scraper loop - looped: {looped}, interval_seconds: {interval_seconds},"
        f"sleeping_time: {sleeping_time}")

    try:
        start_scraper_loop(interval_seconds, looped)
        while True:
            time.sleep(sleeping_time)  # Keep main thread alive considering overall processing if looped=False
            if not looped:
                break
    except KeyboardInterrupt:
        logger.info("Scraper loop stopped.")
