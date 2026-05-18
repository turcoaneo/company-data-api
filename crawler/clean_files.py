# /crawler/clean_files.py

from pathlib import Path
from typing import List

from app.utils.env_vars import PATHS
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


def clean_scraper_files(base_dir: str = ".", patterns=None, files_to_clean: List[str] = None) -> None:
    """
    Remove stale scraper output files before a new run.
    Supports both exact filenames and wildcard patterns.
    Safe for both single-process and multiprocess runs.
    """
    if patterns is None:
        patterns = PATTERNS_TO_CLEAN
    base = Path(base_dir)

    # Remove exact files
    if files_to_clean is None:
        files_to_clean = FILES_TO_CLEAN
    for filename in files_to_clean:
        path = base / filename
        if path.exists():
            try:
                path.unlink()
            except Exception as e:
                logger.error(f"Error removing file {path}: {e}")

    # Remove wildcard-matching files
    for pattern in patterns:
        for path in base.glob(pattern):
            if path.exists():
                try:
                    path.unlink()
                except Exception as e:
                    logger.error(f"Error removing file {path}: {e}")
