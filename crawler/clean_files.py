# /crawler/clean_files.py

from pathlib import Path
from typing import List

import boto3
from botocore.exceptions import ClientError

from app.utils.env_vars import PATHS, APP_ENV, S3_BUCKET
from app.utils.logger_util import get_logger

logger = get_logger()

# Exact filenames
FILES_TO_CLEAN = [
    PATHS["path_bad_urls"],
    PATHS["path_missing_contacts"],
    PATHS["path_bad_urls_report_csv"],
    PATHS["path_bad_urls_report_json"],
    PATHS["path_final_result"],
]

# Pattern-based filenames
PATTERNS_TO_CLEAN = [
    "data/partial_results_*",
    "data/results_*",
]

# S3 config
s3 = boto3.client("s3")


def is_s3_mode() -> bool:
    """Return True when running in UAT/PROD on AWS."""
    return APP_ENV in ("uat", "prod")


# -------------------------------------------------------------------
# LOCAL CLEANER
# -------------------------------------------------------------------
def _clean_local_files(base_dir: str, files_to_clean: List[str], patterns: List[str]):
    base = Path(base_dir)

    # Remove exact files
    for filename in files_to_clean:
        path = base / filename
        if path.exists():
            try:
                path.unlink()
                logger.info(f"Deleted local file: {path}")
            except Exception as e:
                logger.error(f"Error removing file {path}: {e}")

    # Remove wildcard-matching files
    for pattern in patterns:
        for path in base.glob(pattern):
            if path.exists():
                try:
                    path.unlink()
                    logger.info(f"Deleted local file: {path}")
                except Exception as e:
                    logger.error(f"Error removing file {path}: {e}")


# -------------------------------------------------------------------
# S3 CLEANER
# -------------------------------------------------------------------
def _clean_s3_files(files_to_clean: List[str], patterns: List[str]):
    # Remove exact files
    for key in files_to_clean:
        try:
            s3.delete_object(Bucket=S3_BUCKET, Key=key)
            logger.info(f"Deleted S3 object: {key}")
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchKey":
                logger.error(f"Error deleting S3 object {key}: {e}")

    # Remove wildcard-matching files
    for pattern in patterns:
        prefix = pattern.split("/")[0]  # e.g. "data"
        try:
            resp = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
            for obj in resp.get("Contents", []):
                key = obj["Key"]
                if Path(key).match(pattern):
                    try:
                        s3.delete_object(Bucket=S3_BUCKET, Key=key)
                        logger.info(f"Deleted S3 object: {key}")
                    except Exception as e:
                        logger.error(f"Error deleting S3 object {key}: {e}")
        except Exception as e:
            logger.error(f"Error listing S3 objects for pattern {pattern}: {e}")


# -------------------------------------------------------------------
# PUBLIC API
# -------------------------------------------------------------------
def clean_scraper_files(
        base_dir: str = ".",
        patterns: List[str] = None,
        files_to_clean: List[str] = None
) -> None:
    """
    Remove stale scraper output files before a new run.
    Supports both exact filenames and wildcard patterns.
    Works in LOCAL (filesystem) and UAT/PROD (S3).
    """
    if patterns is None:
        patterns = PATTERNS_TO_CLEAN

    if files_to_clean is None:
        files_to_clean = FILES_TO_CLEAN

    if is_s3_mode():
        logger.info("Cleaning scraper files from S3...")
        _clean_s3_files(files_to_clean, patterns)
    else:
        logger.info("Cleaning scraper files from local filesystem...")
        _clean_local_files(base_dir, files_to_clean, patterns)
