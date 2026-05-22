# Company Data API

Veridion-style tech challenge: crawl websites, extract company signals, index them, and expose a matching API.

## Stack

- Python 3.13+
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

### Running the API locally
#### Option A — Using PyCharm (recommended)
Two run configurations are already included:

1. “Main – API and Scraper Job”
 - Runs the FastAPI server and the periodic scraper job.

 - Entry point: company-data-api/main.py

 - Uvicorn on port 8000

 - Swagger UI: http://localhost:8000/docs

2. “Meili bootstrap”
 - Initializes Meilisearch with your processed dataset.

 - Entry point: company-data-api/meili_manager.py

 - Creates index, uploads documents, verifies ingestion

 - Open PyCharm → Run/Debug Configurations → select → Run.

#### Option B — Using terminal
1. “Main – API and Scraper Job”
```bash
uvicorn main:app --reload
# Swagger UI: http://localhost:8000/docs
```

2. “Meili bootstrap”
```shell
python scripts/bootstrap_meili.sh
```


## Run tests

### Usual tests
```bash
pytest --ignore=tests/benchmark 
```

### Usual tests + benchmark if Meili is up
```bash
pytest
```

## GitHub Actions — Terraform Infrastructure
Workflow: https://github.com/turcoaneo/company-data-api/actions/workflows/terraform.yml

### Run Apply
 - Open the workflow page

 - Click Run workflow

 - Select branch

 - Choose apply

 - Run

### Run Destroy
 - Same steps, but choose destroy.

### Permissions
 - Anyone with Triage access can safely trigger these workflows.
