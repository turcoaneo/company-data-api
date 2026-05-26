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
    Works for both local paths and S3 keys.
    Extracts run ID from results_YYYYMMDD_HHMMSS.jsonl.
    """
    name = path.split("/")[-1]
    m = re.search(r"results_(\d{8}_\d{6})\.jsonl", name)
    return m.group(1) if m else name.replace(".jsonl", "")


def _count_jsonl_contacts(path: str):
    from app.utils.env_vars import APP_ENV, S3_BUCKET

    phones = socials = sites_with_contacts = phones_and_socials = 0

    # LOCAL / TEST
    if APP_ENV in ["local", "test"]:
        if not Path(path).exists():
            return phones, socials, sites_with_contacts, phones_and_socials

    # UAT / PROD → check S3 existence
    else:
        import boto3
        s3 = boto3.client("s3")
        try:
            s3.head_object(Bucket=S3_BUCKET, Key=path)
        except s3.exceptions.ClientError:
            return phones, socials, sites_with_contacts, phones_and_socials

    # Read via FileLoader (works for both local + S3)
    from app.utils.file_loader import FileLoader
    with FileLoader().open_file(path, "r", encoding="utf-8") as f:
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
    from app.utils.file_loader import FileLoader

    # 1. Total sites
    with FileLoader().open_file(input_csv_path, "r", encoding="utf-8") as f:
        total_sites = sum(1 for _ in csv.reader(f)) - 1

    # 2. Unreachable + missing
    bad_urls = set()
    if Path(bad_urls_path).exists():
        with FileLoader().open_file(bad_urls_path, "r", encoding="utf-8") as f:
            for line in f:
                d = line.strip()
                if d:
                    bad_urls.add(d)

    missing_contacts = set()
    if Path(missing_contacts_path).exists():
        with FileLoader().open_file(missing_contacts_path, "r", encoding="utf-8") as f:
            for line in f:
                d = line.strip()
                if d:
                    missing_contacts.add(d)

    # 3. Initial + final stats
    initial_phones, initial_socials, initial_sites_with_contacts, initial_both = \
        _count_jsonl_contacts(initial_jsonl_path)

    final_phones, final_socials, final_sites_with_contacts, final_both = \
        _count_jsonl_contacts(final_jsonl_path)

    # 4. Recovered sites
    recovered_sites = final_sites_with_contacts - initial_sites_with_contacts

    # 5. Coverage
    coverage = total_sites - len(bad_urls) + recovered_sites

    # 6. Fill-rate metrics
    phones_per_coverage = final_phones / coverage if coverage else 0
    socials_per_coverage = final_socials / coverage if coverage else 0
    datapoints_per_coverage = final_sites_with_contacts / coverage if coverage else 0
    datapoints_per_sites = final_sites_with_contacts / total_sites

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
            "datapoints_per_sites": datapoints_per_sites,
        }
    }


def _load_top_metrics(top_metrics_path: str) -> dict | None:
    from app.utils.env_vars import APP_ENV, S3_BUCKET

    # LOCAL / TEST
    if APP_ENV in ["local", "test"]:
        p = Path(top_metrics_path)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Top metrics could not be loaded: {e}")
            return None

    # UAT / PROD → S3
    import boto3
    s3 = boto3.client("s3")
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=top_metrics_path)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        return None
    except Exception as e:
        logger.error(f"Top metrics could not be loaded from S3: {e}")
        return None


def _save_top_metrics(top_metrics_path: str, metrics: dict) -> None:
    from app.utils.env_vars import APP_ENV, S3_BUCKET

    data = json.dumps(metrics, ensure_ascii=False, indent=2)

    # LOCAL / TEST
    if APP_ENV in ["local", "test"]:
        Path(top_metrics_path).write_text(data, encoding="utf-8")
        return

    # UAT / PROD → S3
    import boto3
    boto3.client("s3").put_object(
        Bucket=S3_BUCKET,
        Key=top_metrics_path,
        Body=data.encode("utf-8"),
        ContentType="application/json",
    )


def _copy_top_result(final_jsonl_path: str, top_result_path: str) -> None:
    from app.utils.env_vars import APP_ENV, S3_BUCKET

    # LOCAL / TEST
    if APP_ENV in ["local", "test"]:
        src = Path(final_jsonl_path)
        if src.exists():
            shutil.copyfile(src, Path(top_result_path))
        return

    # UAT / PROD → S3
    import boto3
    s3 = boto3.client("s3")
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=final_jsonl_path)
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=top_result_path,
            Body=obj["Body"].read(),
            ContentType="application/jsonl",
        )
    except Exception as e:
        logger.error(f"Could not copy top result on S3: {e}")


def compute_latest_and_top_metrics(
        input_csv_path: str,
        bad_urls_path: str,
        missing_contacts_path: str,
        initial_jsonl_path: str,
        final_jsonl_path: str,
        top_metrics_path: str,
        top_result_path: str,
):
    latest = compute_scraper_metrics(
        input_csv_path=input_csv_path,
        bad_urls_path=bad_urls_path,
        missing_contacts_path=missing_contacts_path,
        initial_jsonl_path=initial_jsonl_path,
        final_jsonl_path=final_jsonl_path,
    )

    existing_top = _load_top_metrics(top_metrics_path)

    latest_score = latest["final"]["phones"] + latest["final"]["socials"]
    top_score = (
        existing_top["final"]["phones"] + existing_top["final"]["socials"]
        if existing_top else -1
    )

    if latest_score > top_score:
        _copy_top_result(final_jsonl_path, top_result_path)
        latest["id"] = _extract_id_from_path(initial_jsonl_path)
        _save_top_metrics(top_metrics_path, latest)
        top = latest
    else:
        top = existing_top if existing_top is not None else latest

    return {
        "latest_results": latest,
        "top_results": top,
    }
