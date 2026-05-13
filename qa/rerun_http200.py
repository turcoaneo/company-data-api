# qa/rerun_http200.py

import asyncio

from app.utils.logger_util import get_logger
from crawler.merge_results import merge_two_runs
from crawler.orchestrator import CrawlerOrchestrator

logger = get_logger()


def load_http_200_domains(json_path: str):
    """
    Load domains from the 'http_200' list in bad_urls_report.json.
    """
    import json

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure key exists and is a list
    domains = data.get("http_200", [])
    return [d.strip() for d in domains if isinstance(d, str) and d.strip()]


async def rerun_http200_domains(
        bad_urls_json_path: str,
        first_pass_output_path: str,
        final_path: str,
        per_domain_concurrency: int = 4,
        timeout: int = 10,
):
    """
    Re-run all HTTP-200 domains and merge results with first-pass output.
    Returns final_path.
    """
    http200_domains = load_http_200_domains(bad_urls_json_path)

    logger.info(f"Re-running {len(http200_domains)} HTTP-200 domains...")

    orch = CrawlerOrchestrator(
        per_domain_concurrency=per_domain_concurrency,
        timeout=timeout
    )

    second_pass_results = await orch.crawl(http200_domains)

    merge_two_runs(first_pass_output_path, second_pass_results, final_path)

    logger.debug(f"Final merged results saved to {final_path}")


def job_wrapper():
    """
    Standalone runner, similar to qa_bad_urls.
    """
    logger.info("Running HTTP-200 re-run as standalone script")
    asyncio.run(
        rerun_http200_domains(
            bad_urls_json_path="./bad_urls_report.json",
            first_pass_output_path="data/results_20260513_132243.jsonl",
            final_path="qa/qa_final_result.jsonl"
        )
    )


if __name__ == "__main__":
    job_wrapper()
