# /crawler/scraper_runner.py

import threading

from app.utils.loader import load_sites_from_config
from app.utils.logger_util import get_logger
from app.utils.timing_util import elapsed_time, log_thread_id
from crawler.orchestrator import CrawlerOrchestrator
from crawler.merge_results import merge_scraper_results
from app.utils.path_util import get_project_root

logger = get_logger()


@elapsed_time("run_scraper")
async def run_scraper():
    logger.info("*" * 100)
    logger.info(f"Running {log_thread_id(threading.get_ident(), 'scraper')}")

    # Phase 0: Load sites
    input_csv = get_project_root() / "data" / "small-sample-websites-company-names.csv"
    sites = load_sites_from_config(str(input_csv))
    logger.info(f"Loaded {len(sites)} sites")

    orch = CrawlerOrchestrator(concurrency=4, timeout=10)

    try:
        results = await orch.crawl(sites)
    except Exception as e:
        logger.error(f"Scraper crashed: {e}", exc_info=True)
        return

    logger.info(f"Scraper finished. Found {len(results)} valid sites.")

    # Merge with original CSV
    output_path = merge_scraper_results(str(input_csv), results)
    logger.info(f"Merged results saved to {output_path}")
