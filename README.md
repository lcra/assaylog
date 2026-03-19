# AssayLog

A REST API for logging and retrieving mineral assay results from mining sites.

## Status

In progress - DynamoDB connected, data persists across restarts.

## Tech Stack

- Python / FastAPI
- AWS Lambda + API Gateway (coming)
- DynamoDB
- Terraform (coming)
- GitHub Actions (coming)

## Running Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables

DYNAMODB_TABLE_NAME - defaults to assaylog-samples
AWS_REGION - defaults to ap-southeast-2

## Endpoints

POST /samples - log a new assay sample
GET  /samples/{site} - retrieve all samples for a site
GET  /samples/{site}/summary - average grade and sample count for a site