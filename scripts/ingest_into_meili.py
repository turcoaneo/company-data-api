# scripts/ingest_into_meili.py

import meilisearch


client = meilisearch.Client("http://localhost:7700")
index = client.index("companies")

with open("meili_final.jsonl", "rb", encoding="utf-8") as f:
    data = f.read()

index.add_documents_ndjson(data)
