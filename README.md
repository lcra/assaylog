# AssayLog

A REST API for logging and retrieving mineral assay results from mining sites.

## Status

In progress - API running locally with in-memory data store.

## Tech Stack

- Python / FastAPI
- AWS Lambda + API Gateway (coming)
- DynamoDB (coming)
- Terraform (coming)
- GitHub Actions (coming)

## Running Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints

POST /samples - log a new assay sample
GET  /samples/{site} - retrieve all samples for a site
GET  /samples/{site}/summary - average grade and sample count for a site