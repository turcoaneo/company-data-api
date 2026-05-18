# scripts/ingest_into_meili.py

import meilisearch

from app.utils.env_vars import PATHS

client = meilisearch.Client("http://localhost:7700")
index = client.index("companies")

with open(PATHS["path_meili_final"], "rb", encoding="utf-8") as f:
    data = f.read()

index.add_documents_ndjson(data)
