# /crawler/mp_crawler.py

import asyncio
import json
import math
from multiprocessing import Process
from pathlib import Path
from typing import List

import boto3

from app.utils.env_vars import PATHS, APP_ENV, S3_BUCKET
from app.utils.loader import load_sites_from_config
from app.utils.logger_util import get_logger
from app.utils.timing_util import log_thread_id
from app.utils.file_loader import FileLoader
from crawler.merge_results import merge_scraper_results
from crawler.orchestrator import CrawlerOrchestrator

logger = get_logger("mp_scraper")


def _split_into_chunks(items: List[str], num_chunks: int) -> List[List[str]]:
    if num_chunks <= 1 or len(items) <= num_chunks:
        return [items]
    size = math.ceil(len(items) / num_chunks)
    return [items[i:i + size] for i in range(0, len(items), size)]


def _write_partial_jsonl(path: str, rows: List[dict]) -> None:
    fl = FileLoader()
    with fl.open_file(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


async def _crawl_chunk(chunk_id: int, domains: List[str], output_dir: str) -> None:
    logger.info(f"[chunk {chunk_id}] Starting crawl for {len(domains)} domains")
    orch = CrawlerOrchestrator()

    try:
        results = await orch.crawl(domains)
    except Exception as e:
        logger.error(f"[chunk {chunk_id}] Scraper crashed: {e}", exc_info=True)
        return

    partial_path = f"{output_dir}/partial_results_{chunk_id}.jsonl"
    _write_partial_jsonl(partial_path, results)
    logger.info(f"[chunk {chunk_id}] Saved {len(results)} results to {partial_path}")


def _worker_process(chunk_id: int, domains: List[str], output_dir: str) -> None:
    import threading
    logger.info("*" * 80)
    thread_id = log_thread_id(threading.get_ident(), 'scraper_chunk')
    logger.info(f"[chunk {chunk_id}] Running {thread_id}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_crawl_chunk(chunk_id, domains, output_dir))
    except Exception as e:
        logger.error(f"[chunk {chunk_id}] Worker crashed: {e}", exc_info=True)
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        if pending:
            try:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception as e:
                logger.error(f"Error while awaiting pending tasks for chunk {chunk_id}, thread {thread_id}: {e}")

        loop.close()
        logger.info(f"[chunk {chunk_id}] Event loop closed for {thread_id}")


def _load_partial_results(output_dir: str) -> List[dict]:
    fl = FileLoader()
    results = []

    if APP_ENV == "local":
        for path in sorted(Path(output_dir).glob("partial_results_*.jsonl")):
            with fl.open_file(str(path), "r", encoding="utf-8") as f:
                for line in f:
                    results.append(json.loads(line))
        return results

    # UAT/PROD → S3
    s3 = boto3.client("s3")
    prefix = output_dir.rstrip("/") + "/"

    resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    for obj in resp.get("Contents", []):
        key = obj["Key"]
        if "partial_results_" in key:
            with fl.open_file(key, "r", encoding="utf-8") as f:
                for line in f:
                    results.append(json.loads(line))

    return results


async def _run_qa_pipeline(merged_output_path: Path) -> None:
    from qa.qa_bad_urls import run_bad_urls_check
    from qa.unreachable_classifier import classify_csv_to_json
    from qa.rerun_http200 import rerun_http200_domains

    logger.info("Running QA unreachable-domain analysis...")
    await run_bad_urls_check(
        path=PATHS["path_bad_urls"],
        csv_out=PATHS["path_bad_urls_report_csv"]
    )

    logger.info("Classifying unreachable domains...")
    await classify_csv_to_json(
        csv_path=PATHS["path_bad_urls_report_csv"],
        json_out=PATHS["path_bad_urls_report_json"]
    )

    scraper_final_path = PATHS["path_final_result"]
    logger.info("Re-running HTTP-200 unreachable domains...")
    await rerun_http200_domains(
        bad_urls_json_path=PATHS["path_bad_urls_report_json"],
        first_pass_output_path=str(merged_output_path),
        final_path=scraper_final_path
    )

    logger.info(f"Final merged results saved to {scraper_final_path}")


def run_scraper_multiprocess(num_chunks: int = 8, output_dir: str = "data") -> None:
    logger.info("*" * 100)
    logger.info("Running scraper in multiprocessing mode")

    input_csv = PATHS["path_data_sample"]
    sites = load_sites_from_config(str(input_csv))
    logger.info(f"Loaded {len(sites)} sites")

    chunks = _split_into_chunks(sites, num_chunks)

    procs: List[Process] = []
    for idx, chunk in enumerate(chunks):
        p = Process(target=_worker_process, args=(idx, chunk, output_dir))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    logger.info("All chunks finished. Loading partial results...")
    all_results = _load_partial_results(output_dir)
    logger.info(f"Loaded {len(all_results)} total results from partial files")

    logger.info("Merging partial results with input CSV...")
    merged_output_path = merge_scraper_results(input_csv, all_results, output_dir)
    logger.info(f"Merged results saved to {merged_output_path}")

    asyncio.run(_run_qa_pipeline(merged_output_path))

    logger.info("Multiprocess scraper run finished successfully")
