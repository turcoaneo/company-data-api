# crawler/util/meili_ingest_helper.py
import boto3
import requests
from pathlib import Path
from app.utils.env_vars import MEILI, PATHS, APP_ENV, S3_BUCKET
from app.utils.file_loader import FileLoader
from app.utils.logger_util import get_logger

logger = get_logger()

MEILI_URL = MEILI["url"]
INDEX_NAME = MEILI["index"]
FILE_PATH = PATHS["path_meili_final"]


def _file_exists(path: str) -> bool:
    """Check existence locally or on S3."""
    if APP_ENV in ["local", "test"]:
        return Path(path).exists()

    s3 = boto3.client("s3")
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=path)
        return True
    except Exception as e:
        logger.error(f"Could not find file {path} : {e}")
        return False


def ingest_ndjson(
    url: str = MEILI_URL,
    index_name: str = INDEX_NAME,
    file_path: str = FILE_PATH
):
    """Upload NDJSON to Meilisearch with existence check and clean return."""
    if not _file_exists(file_path):
        msg = f"NDJSON file not found: {file_path}"
        return {"ok": False, "status": None, "error": msg}

    try:
        with FileLoader().open_file(file_path, "rb") as f:
            resp = requests.post(
                f"{url}/indexes/{index_name}/documents",
                params={"primaryKey": "id"},
                data=f,
                headers={"Content-Type": "application/x-ndjson"}
            )
    except Exception as e:
        msg = f"Meili ingestion failed: {e}"
        logger.error(msg)
        return {"ok": False, "status": None, "error": msg}

    return {
        "ok": resp.status_code in (200, 202),
        "status": resp.status_code,
        "response": resp.text,
        "file": file_path,
        "index": index_name,
    }
