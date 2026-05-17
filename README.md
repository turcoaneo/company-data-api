# Company Data API

Veridion-style tech challenge: crawl websites, extract company signals, index them, and expose a matching API.

## Stack

- Python 3.11+
- FastAPI (with built-in OpenAPI/Swagger UI at `/docs`)
- aiohttp + selectolax for crawling/parsing
- Docker, AWS Fargate (via Terraform), GitHub Actions (CI/CD)

## Setup (local, with venv)

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## Run API

```bash
uvicorn main:app --reload
# Swagger UI: http://localhost:8000/docs
```

## Run tests

```bash
pytest
```

## Prepare Meilisearch
### Start Meilisearch in Docker
```powershell
docker run -d --name ms -p 7700:7700 getmeili/meilisearch:v1.7
```

### Add ID for Meili index
```shell
python .\scripts\convert_for_meili.py
```

### Create index
```shell
Invoke-WebRequest -Method DELETE "http://localhost:7700/indexes/companies"
```

### Ingest into Meili
```shell
Invoke-WebRequest -Method POST `
  -Uri "http://localhost:7700/indexes/companies/documents?primaryKey=id" `
  -ContentType "application/x-ndjson" `
  -InFile "D:\DEV\Python\company-data-api\meili_final.jsonl"
```

```bash
curl -X POST "http://localhost:7700/indexes/companies/documents?primaryKey=id" \
     -H "Content-Type: application/x-ndjson" \
     --data-binary @meili_final.jsonl
```

### Verify Meili
```shell
Invoke-WebRequest "http://localhost:7700/tasks/7" | Select-Object -Expand Content

Invoke-WebRequest "http://localhost:7700/indexes/companies/documents?limit=3" | Select-Object -Expand Content
```


