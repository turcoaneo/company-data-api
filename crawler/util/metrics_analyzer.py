# crawler/util/metrics_analyzer.py

import csv
import json
import re
import shutil
from pathlib import Path

from app.utils.logger_util import get_logger

logger = get_logger()


def _extract_id_from_path(path: str) -> str:
    """
    Extracts run ID from results_YYYYMMDD_HHMMSS.jsonl.
    If no match, returns the filename without extension.
    """
    name = Path(path).name
    m = re.search(r"results_(\d{8}_\d{6})\.jsonl", name)
    if m:
        return m.group(1)
    return Path(path).stem


def _count_jsonl_contacts(path: Path):
    phones = 0
    socials = 0
    sites_with_contacts = 0
    phones_and_socials = 0

    if not path.exists():
        return phones, socials, sites_with_contacts, phones_and_socials

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception as e:
                logger.error(f"Metrics analyzer extract line error for {line}: {e}")
                continue

            has_phone = bool(obj.get("phones"))
            has_social = bool(obj.get("socials"))

            if has_phone:
                phones += 1
            if has_social:
                socials += 1
            if has_phone or has_social:
                sites_with_contacts += 1
            if has_phone and has_social:
                phones_and_socials += 1

    return phones, socials, sites_with_contacts, phones_and_socials


def compute_scraper_metrics(
        input_csv_path: str,
        bad_urls_path: str,
        missing_contacts_path: str,
        initial_jsonl_path: str,
        final_jsonl_path: str
):
    # 1. Total sites
    with open(input_csv_path, "r", encoding="utf-8") as f:
        total_sites = sum(1 for _ in csv.reader(f)) - 1

    # 2. Unreachable + missing
    bad_urls = set()
    if Path(bad_urls_path).exists():
        with open(bad_urls_path, "r", encoding="utf-8") as f:
            for line in f:
                d = line.strip()
                if d:
                    bad_urls.add(d)

    missing_contacts = set()
    if Path(missing_contacts_path).exists():
        with open(missing_contacts_path, "r", encoding="utf-8") as f:
            for line in f:
                d = line.strip()
                if d:
                    missing_contacts.add(d)

    # 3. Initial + final stats
    (
        initial_phones,
        initial_socials,
        initial_sites_with_contacts,
        initial_both
    ) = _count_jsonl_contacts(Path(initial_jsonl_path))

    (
        final_phones,
        final_socials,
        final_sites_with_contacts,
        final_both
    ) = _count_jsonl_contacts(Path(final_jsonl_path))

    # 4. Recovered sites
    recovered_sites = final_sites_with_contacts - initial_sites_with_contacts

    # 5. Coverage
    coverage = total_sites - len(bad_urls) + recovered_sites

    # 6. Fill-rate metrics
    phones_per_coverage = final_phones / coverage if coverage else 0
    socials_per_coverage = final_socials / coverage if coverage else 0

    # UNIQUE datapoints = sites with phone OR social
    datapoints_per_coverage = final_sites_with_contacts / coverage if coverage else 0
    any_datapoints_per_coverage = datapoints_per_coverage

    return {
        "id": _extract_id_from_path(initial_jsonl_path),
        "total_sites": total_sites,
        "unreachable_sites": len(bad_urls),
        "missing_contacts": len(missing_contacts),
        "recovered_sites": recovered_sites,
        "coverage": coverage,
        "initial": {
            "phones": initial_phones,
            "socials": initial_socials,
            "sites_with_contacts": initial_sites_with_contacts,
            "phones_and_socials": initial_both,
        },
        "final": {
            "phones": final_phones,
            "socials": final_socials,
            "sites_with_contacts": final_sites_with_contacts,
            "phones_and_socials": final_both,
        },
        "fill_rates": {
            "phones_per_coverage": phones_per_coverage,
            "socials_per_coverage": socials_per_coverage,
            "datapoints_per_coverage": datapoints_per_coverage,
            "any_datapoints_per_coverage": any_datapoints_per_coverage,
        }
    }


def _load_top_metrics(top_metrics_path: Path) -> dict | None:
    if not top_metrics_path.exists():
        return None
    try:
        return json.loads(top_metrics_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Top metrics could not be loaded: {e}")
        return None


def _save_top_metrics(top_metrics_path: Path, metrics: dict) -> None:
    top_metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


def _copy_top_result(final_jsonl_path: str, top_result_path: Path) -> None:
    src = Path(final_jsonl_path)
    if src.exists():
        shutil.copyfile(src, top_result_path)


def compute_latest_and_top_metrics(
        input_csv_path: str,
        bad_urls_path: str,
        missing_contacts_path: str,
        initial_jsonl_path: str,
        final_jsonl_path: str,
        top_metrics_path: str = "best_metric.json",
        top_result_path: str = "top_result.jsonl",
):
    """
    Computes metrics for the latest run (final_result.jsonl),
    compares with stored top metrics, and updates top_result.jsonl + best_metric.json
    if the latest run is better (phones + socials).
    Returns:
      {
        "latest_results": {...},
        "top_results": {...},
      }
    """
    latest = compute_scraper_metrics(
        input_csv_path=input_csv_path,
        bad_urls_path=bad_urls_path,
        missing_contacts_path=missing_contacts_path,
        initial_jsonl_path=initial_jsonl_path,
        final_jsonl_path=final_jsonl_path,
    )

    top_metrics_file = Path(top_metrics_path)
    top_result_file = Path(top_result_path)

    existing_top = _load_top_metrics(top_metrics_file)

    latest_score = latest["final"]["phones"] + latest["final"]["socials"]
    top_score = (
        existing_top["final"]["phones"] + existing_top["final"]["socials"]
        if existing_top
        else -1
    )

    if latest_score > top_score:
        # New best run → update top_result.jsonl + best_metric.json
        _copy_top_result(final_jsonl_path, top_result_file)
        latest["id"] = _extract_id_from_path(initial_jsonl_path)
        _save_top_metrics(top_metrics_file, latest)
        top = latest
    else:
        # Keep existing top
        top = existing_top if existing_top is not None else latest

    return {
        "latest_results": latest,
        "top_results": top,
    }
