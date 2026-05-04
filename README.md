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

## Docker

```bash
docker build -t company-data-api:local .
docker run --rm -p 8000:8000 company-data-api:local
```

## AWS Fargate & Terraform

- `terraform/` will contain ECS/Fargate, ECR, networking, and IAM definitions.
- `.github/workflows/deploy.yml` will:
  - build & push Docker image to ECR
  - run `terraform init/plan/apply` (with remote state)
- You will plug in your own Terraform and workflow definitions later.
