# /cron_jobs/scraper_job.py

import time

from app.utils.env_vars import SCRAPER_CONFIG, PATHS, MEILI, APP_ENV, S3_BUCKET
from app.utils.logger_util import get_logger
from app.utils.timing_util import elapsed_time
from crawler.clean_files import clean_scraper_files

logger = get_logger("scraper_job")


@elapsed_time("run_scraper")
def run_job():
    run_scraper_crawler()

    meili_connect_ingest()


def meili_connect_ingest():
    # Convert scraper final result to meili PK-wise JSONL
    from scripts.convert_for_meili import convert_files
    convert_files()
    # Ingest file into Meili
    from meili_manager import MeiliManager
    meili = MeiliManager()
    try:
        meili.connect_to_meili()  # Meili supposedly already running
        from app.utils import meili_ingest_helper
        meili_ingest_helper.ingest_ndjson(index_name=MEILI["index"], file_path=PATHS["path_meili_final"])
        logger.info(f"Finished ingesting meili data into {meili.url}/{meili.index_name}.")
        meili_ingest_helper.ingest_ndjson(index_name=MEILI["top_index"], file_path=PATHS["path_meili_top"])
        logger.info(f"Finished ingesting meili data into {meili.url}/{meili.top_index_name}.")
    except Exception as e:
        logger.error(f"Cannot connect to Meili: {e}")


def run_scraper_crawler():
    import time
    from crawler.util.run_history import record_run
    start_time = time.time()
    clean_scraper_files()
    chunks = SCRAPER_CONFIG["mp_chunks"]
    domain_conc = SCRAPER_CONFIG["domain_concurrency"]
    domains_parallel = SCRAPER_CONFIG["domains_in_parallel"]

    # Run scraper
    logger.info('Scraping (multiprocess)')
    from crawler.mp_crawler import run_scraper_multiprocess
    run_scraper_multiprocess(num_chunks=chunks)

    # Extract timestamp from results_YYYYMMDD_HHMMSS.jsonl
    import re
    if APP_ENV in ["local", "test"]:
        from pathlib import Path
        results_files = list(Path("data").glob("results_*.jsonl"))

        if results_files:
            latest = max(results_files, key=lambda p: p.stat().st_mtime)
            name = latest.name
        else:
            name = None

    else:
        import boto3
        s3 = boto3.client("s3")
        resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="data/results_")

        if "Contents" in resp and resp["Contents"]:
            # pick latest by LastModified
            latest = max(resp["Contents"], key=lambda o: o["LastModified"])
            name = latest["Key"].split("/")[-1]  # extract filename
        else:
            name = None

    if name:
        m = re.search(r"results_(\d{8}_\d{6})\.jsonl", name)
        ts = m.group(1) if m else "unknown"
    else:
        ts = "unknown"


def start_scraper_loop(interval_sec: int = 1200, is_looped: bool = True):
    logger.info(f"Starting scraper - looped: {is_looped}")

    def loop_cron_job():
        while True:
            run_job()
            time.sleep(interval_sec)
            if not is_looped:
                break

    loop_cron_job()


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
