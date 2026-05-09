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
    import asyncio
    logger.info('Scraping')
    asyncio.run(run_scraper())
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
