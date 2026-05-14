# /crawler/scraper_runner.py

import threading

from app.utils.loader import load_sites_from_config
from app.utils.logger_util import get_logger
from app.utils.path_util import get_project_root
from app.utils.timing_util import log_thread_id
from crawler.orchestrator import CrawlerOrchestrator

logger = get_logger()


async def run_scraper():
    logger.info("*" * 100)
    logger.info(f"Running {log_thread_id(threading.get_ident(), 'scraper')}")

    # Phase 0: Load sites
    input_csv = get_project_root() / "data" / "sample-websites-company-names.csv"
    sites = load_sites_from_config(str(input_csv))
    logger.info(f"Loaded {len(sites)} sites")

    orch = CrawlerOrchestrator()

    try:
        results = await orch.crawl(sites)
    except Exception as e:
        logger.error(f"Scraper crashed: {e}", exc_info=True)
        return

    logger.info(f"Scraper finished. Found {len(results)} sites with extracted contacts.")

    # Merge with original CSV
    from app.utils.env_vars import SCRAPER_CONFIG
    is_sync_saving = SCRAPER_CONFIG["sync_saving"]
    if is_sync_saving:
        from crawler.merge_results import merge_scraper_results
        output_path = merge_scraper_results(str(input_csv), results)
    else:
        from crawler.merge_results import async_merge_scraper_results
        output_path = await async_merge_scraper_results(str(input_csv), results)

    logger.info(f"Merged results saved to {output_path}")

    # ---------------------------------------------------------
    # Run QA unreachable-domain analysis
    # ---------------------------------------------------------
    logger.info("Scraper - Running QA unreachable-domain analysis...")

    from qa.qa_bad_urls import run_bad_urls_check
    await run_bad_urls_check(
        path="./bad_urls.txt",
        csv_out="./bad_urls_report.csv"
    )

    logger.info("QA unreachable-domain report saved to bad_urls_report.csv")

    # ---------------------------------------------------------
    # Run unreachable classifier to produce JSON
    # ---------------------------------------------------------
    logger.info("Classifying unreachable domains...")

    from qa.unreachable_classifier import classify_csv_to_json
    await classify_csv_to_json(
        csv_path="./bad_urls_report.csv",
        json_out="./bad_urls_report.json")

    logger.info("Unreachable-domain classification saved to bad_urls_report.json")

    # ---------------------------------------------------------
    # SECOND PASS: re-run all HTTP-200 unreachable domains
    # ---------------------------------------------------------
    from qa.rerun_http200 import rerun_http200_domains

    scraper_final_path = "final_result.jsonl"
    await rerun_http200_domains(
        bad_urls_json_path="./bad_urls_report.json",
        first_pass_output_path=str(output_path),
        final_path=scraper_final_path
    )
    logger.info(f"Final merged results saved to {scraper_final_path}")

    logger.info("Scraper runner finished successfully")
