# meili_ingest_helper.py

import requests

from app.utils.env_vars import MEILI, PATHS

MEILI_URL = MEILI["url"]
INDEX_NAME = MEILI["index"]
FILE_PATH = PATHS["path_meili_final"]


def ingest_ndjson(url: str = MEILI_URL, index_name: str = INDEX_NAME, file_path: str = FILE_PATH):
    from app.utils.file_loader import FileLoader
    with FileLoader().open_file(file_path, "rb") as f:
        resp = requests.post(
            f"{url}/indexes/{index_name}/documents",
            params={"primaryKey": "id"},
            data=f,
            headers={"Content-Type": "application/x-ndjson"}
        )
    return resp.status_code, resp.text
