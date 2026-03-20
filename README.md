# AssayLog

A REST API for logging and retrieving mineral assay results from mining sites.

## Status

In progress - Endpoint tests added, all passing.

## Tech Stack

- Python / FastAPI
- AWS Lambda + API Gateway
- DynamoDB
- Terraform
- GitHub Actions (coming)

## Running Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Running Tests
```bash
pytest tests/ -v
```

## Deploying
```bash
# Install Linux-compatible dependencies
pip install -r requirements.txt --target ./package --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.11

# Package the app
Compress-Archive -Path package\*, app -DestinationPath lambda.zip

# Deploy
cd terraform
terraform init
terraform apply
```

## Environment Variables

- DYNAMODB_TABLE_NAME - defaults to assaylog-samples
- AWS_REGION - defaults to ap-southeast-2

## Endpoints

- POST /samples - log a new assay sample
- GET /samples/{site} - retrieve all samples for a site
- GET /samples/{site}/summary - average grade and sample count for a site

## Architecture

HTTP Request -> API Gateway -> Lambda (FastAPI via Mangum) -> DynamoDB

## Infrastructure

All AWS resources provisioned via Terraform:

- Lambda function running Python 3.11
- API Gateway HTTP API routing all requests to Lambda
- IAM role scoped to DynamoDB read/write only
- DynamoDB table with site as partition key and id as sort key

## Live API

Base URL: https://zw3kb7keq2.execute-api.ap-southeast-2.amazonaws.com

Example requests:
```powershell
# Log a sample
Invoke-WebRequest -Uri "https://zw3kb7keq2.execute-api.ap-southeast-2.amazonaws.com/samples" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"site": "Olympic Dam", "depth_m": 142.5, "element": "Cu", "grade": 2.3}'

# Get samples for a site
Invoke-WebRequest -Uri "https://zw3kb7keq2.execute-api.ap-southeast-2.amazonaws.com/samples/Olympic%20Dam" -Method GET
```