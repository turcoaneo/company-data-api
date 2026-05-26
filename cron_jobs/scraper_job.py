# /cron_jobs/scraper_job.py

import threading
import time
import asyncio

from app.utils.env_vars import SCRAPER_CONFIG, PATHS, MEILI
from app.utils.logger_util import get_logger
from app.utils.timing_util import elapsed_time
from crawler.scraper_runner import run_scraper

logger = get_logger("scraper_job")

# ---------------------------------------------------------
# GLOBAL EVENT LOOP (persistent, reused forever)
# ---------------------------------------------------------
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@elapsed_time("run_scraper")
def run_job():
    run_scraper_crawler()
    meili_connect_ingest()


def meili_connect_ingest():
    from scripts.convert_for_meili import convert_files
    convert_files()

    from meili_manager import MeiliManager
    meili = MeiliManager()

    try:
        meili.connect_to_meili()
        from app.utils import meili_ingest_helper
        meili_ingest_helper.ingest_ndjson(index_name=MEILI["index"], file_path=PATHS["path_meili_final"])
        logger.info(f"Finished ingesting meili data into {meili.url}/{meili.index_name}.")
        meili_ingest_helper.ingest_ndjson(index_name=MEILI["top_index"], file_path=PATHS["path_meili_top"])
        logger.info(f"Finished ingesting meili data into {meili.url}/{meili.top_index_name}.")
    except Exception as e:
        logger.error(f"Cannot connect to Meili: {e}")


def run_scraper_crawler():
    from crawler.util.run_history import record_run
    from crawler.clean_files import clean_scraper_files
    import re

    start_time = time.time()
    clean_scraper_files()

    chunks = SCRAPER_CONFIG["mp_chunks"]
    domain_conc = SCRAPER_CONFIG["domain_concurrency"]
    domains_parallel = SCRAPER_CONFIG["domains_in_parallel"]

    # -----------------------------
    # SINGLE MODE (asyncio)
    # -----------------------------
    if not chunks:
        logger.info("Scraping (single, persistent loop)")
        loop.run_until_complete(run_scraper())

    # -----------------------------
    # MULTIPROCESS MODE
    # -----------------------------
    else:
        logger.info("Scraping (multiprocess)")
        from crawler.mp_crawler import run_scraper_multiprocess
        run_scraper_multiprocess(num_chunks=chunks)

    # Extract timestamp
    from app.service.service_metrics import find_latest_results_file
    latest_file = find_latest_results_file()
    if latest_file:
        m = re.search(r"results_(\d{8}_\d{6})\.jsonl", latest_file)
        ts = m.group(1) if m else "unknown"
    else:
        ts = "unknown"

    duration = time.time() - start_time

    record_run(
        start_ts=ts,
        duration=duration,
        config=[chunks, domain_conc, domains_parallel]
    )


def start_scraper_loop(interval_sec: int = 1200, is_looped: bool = True):
    logger.info(f"Starting scraper - looped: {is_looped}")

    def loop_cron_job():
        while True:
            run_job()
            time.sleep(interval_sec)
            if not is_looped:
                break

    threading.Thread(target=loop_cron_job, daemon=False).start()


if __name__ == "__main__":
    looped = SCRAPER_CONFIG["looped"]
    interval_seconds = int(SCRAPER_CONFIG["interval"])
    sleeping_time = int(SCRAPER_CONFIG["sleep_time"])

    logger.debug(
        f"Starting scraper loop - looped: {looped}, interval_seconds: {interval_seconds}, "
        f"sleeping_time: {sleeping_time}"
    )

    try:
        start_scraper_loop(interval_seconds, looped)
        while True:
            time.sleep(sleeping_time)
            if not looped:
                break
    except KeyboardInterrupt:
        logger.info("Scraper loop stopped.")
