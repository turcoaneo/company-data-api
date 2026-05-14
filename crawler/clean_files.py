# /crawler/clean_files.py

from pathlib import Path

from app.utils.logger_util import get_logger

logger = get_logger()

# Exact filenames
FILES_TO_CLEAN = [
    "bad_urls.txt",
    "missing_contacts.txt",
    "bad_urls_report.csv",
    "bad_urls_report.json",
    "final_result.jsonl",
]

# Pattern-based filenames
PATTERNS_TO_CLEAN = [
    "data/partial_results_*",
    "data/results_*",
]


def clean_scraper_files(base_dir: str = ".", patterns=None) -> None:
    """
    Remove stale scraper output files before a new run.
    Supports both exact filenames and wildcard patterns.
    Safe for both single-process and multiprocess runs.
    """
    if patterns is None:
        patterns = PATTERNS_TO_CLEAN
    base = Path(base_dir)

    # Remove exact files
    for filename in FILES_TO_CLEAN:
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
