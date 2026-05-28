
## Prepare Meilisearch
### Start Meilisearch in Docker
```bash
./scripts/bootstrap_meili.sh 
```

### Add ID for Meili index
```shell
python .\scripts\convert_for_meili.py
```

### Delete index
```shell
Invoke-WebRequest -Method DELETE "http://localhost:7700/indexes/companies"
```
```bash
curl -X DELETE "http://localhost:7700/indexes/companies"
```

### Ingest into Meili from project root
```shell
Invoke-WebRequest -Method POST `
  -Uri "http://localhost:7700/indexes/companies/documents?primaryKey=id" `
  -ContentType "application/x-ndjson" `
  -InFile "results\meili_final.jsonl"
```

```bash
curl -X POST "http://localhost:7700/indexes/top_result_companies/documents?primaryKey=id" \
     -H "Content-Type: application/x-ndjson" \
     --data-binary @results/meili_top.jsonl
```

### Verify Meili
```shell
Invoke-WebRequest "http://localhost:7700/tasks/<task_number>" | Select-Object -Expand Content

Invoke-WebRequest "http://localhost:7700/indexes/companies/documents?limit=3" | Select-Object -Expand Content
```

```bash
curl -X GET "http://localhost:7700/tasks/<task_number>"

curl -X GET "http://localhost:7700/indexes/companies/documents?limit=3"
```

## Terraform AWS
### Create S3 bucket for file persistence
aws s3api create-bucket --bucket company-data-api-tf-state --region eu-north-1 --create-bucket-configuration LocationConstraint=eu-north-1
### DynamoDB for versioning
aws dynamodb create-table --table-name company-data-api-tf-locks --attribute-definitions \
AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST

### Ops
terraform init
terraform validate

terraform plan -var-file="dev.tfvars"

terraform apply -var-file="dev.tfvars" -auto-approve

terraform destroy -var-file="dev.tfvars" -auto-approve