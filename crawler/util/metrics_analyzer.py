# crawler/util/metrics_analyzer.py

import json
from pathlib import Path
import csv


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
                from app.utils.logger_util import get_logger
                logger = get_logger()
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
    # -----------------------------
    # 1. Total sites from CSV
    # -----------------------------
    with open(input_csv_path, "r", encoding="utf-8") as f:
        total_sites = sum(1 for _ in csv.reader(f)) - 1

    # -----------------------------
    # 2. Unreachable + missing
    # -----------------------------
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

    # -----------------------------
    # 3. Initial + final JSONL stats
    # -----------------------------
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

    # -----------------------------
    # 4. Recovered sites
    # -----------------------------
    recovered_sites = final_sites_with_contacts - initial_sites_with_contacts

    # -----------------------------
    # 5. Corrected coverage
    # -----------------------------
    coverage = total_sites - len(bad_urls) + recovered_sites

    # -----------------------------
    # 6. Fill-rate metrics
    # -----------------------------
    phones_per_coverage = final_phones / coverage if coverage else 0
    socials_per_coverage = final_socials / coverage if coverage else 0

    # UNIQUE datapoints = sites with phone OR social
    datapoints_per_coverage = final_sites_with_contacts / coverage if coverage else 0

    any_datapoints_per_coverage = datapoints_per_coverage

    # -----------------------------
    # 7. Return all metrics
    # -----------------------------
    return {
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
