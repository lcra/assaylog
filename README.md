# AssayLog

A REST API for logging and retrieving mineral assay results from mining sites.

Drill core samples are collected at mining sites and sent for assay analysis to determine
the concentration of target elements (gold, copper, iron etc.) at a given depth. AssayLog
provides a simple API to record sample results and query grade summaries by site.

Built to demonstrate Python backend development, AWS serverless deployment, infrastructure
as code with Terraform, and CI/CD with GitHub Actions.

## Architecture

HTTP Request -> API Gateway -> Lambda (FastAPI via Mangum) -> DynamoDB

- API Gateway handles the public HTTP endpoint
- Lambda runs the FastAPI application via the Mangum adapter
- DynamoDB stores sample records with site as partition key and id as sort key
- Terraform provisions all AWS infrastructure as code
- GitHub Actions runs tests and deploys on every push to main

## Tech Stack

- Python 3.11 / FastAPI / Pydantic
- AWS Lambda + API Gateway (HTTP API)
- DynamoDB (PAY_PER_REQUEST billing)
- Terraform
- GitHub Actions

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /samples | Log a new assay sample |
| GET | /samples/{site} | Retrieve all samples for a site |
| GET | /samples/{site}/summary | Average grade and sample count for a site |

### POST /samples

Request body:
```json
{
  "site": "Olympic Dam",
  "depth_m": 142.5,
  "element": "Cu",
  "grade": 2.3
}
```

Response (201):
```json
{
  "message": "Sample logged",
  "sample": {
    "site": "Olympic Dam",
    "id": "0ad43864-0573-4c34-8702-7dab500e88a5",
    "depth_m": "142.5",
    "element": "Cu",
    "grade": "2.3"
  }
}
```

### GET /samples/{site}

Response (200):
```json
{
  "site": "Olympic Dam",
  "samples": [
    {
      "site": "Olympic Dam",
      "id": "0ad43864-0573-4c34-8702-7dab500e88a5",
      "depth_m": "142.5",
      "element": "Cu",
      "grade": "2.3"
    }
  ]
}
```

### GET /samples/{site}/summary

Response (200):
```json
{
  "site": "Olympic Dam",
  "sample_count": 1,
  "average_grade": 2.3
}
```

## Running Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs for the interactive API documentation.

## Running Tests
```bash
pytest tests/ -v
```

## Deploying

All infrastructure is provisioned via Terraform. State is stored remotely in S3.
```bash
# Install Linux-compatible dependencies for Lambda
pip install -r requirements.txt \
  --target ./package \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --python-version 3.11

# Package the app and dependencies
zip -r lambda.zip app/ package/

# Deploy
cd terraform
terraform init
terraform apply
```

CI/CD via GitHub Actions deploys automatically on every push to main.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DYNAMODB_TABLE_NAME | assaylog-samples | DynamoDB table name |
| AWS_REGION | ap-southeast-2 | AWS region |

## Infrastructure

All resources provisioned via Terraform:

- `aws_lambda_function` - Python 3.11, 128MB memory, 30s timeout
- `aws_apigatewayv2_api` - HTTP API, catch-all route to Lambda
- `aws_dynamodb_table` - PAY_PER_REQUEST, site (partition) + id (sort) keys
- `aws_iam_role` - scoped to DynamoDB read/write on this table only
- Terraform state stored in S3 for shared access between local and CI/CD

## Live API

Base URL: `https://<api-id>.execute-api.<region>.amazonaws.com`
```powershell
# Log a sample
Invoke-WebRequest -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/samples" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"site": "Olympic Dam", "depth_m": 142.5, "element": "Cu", "grade": 2.3}'

# Get samples for a site
Invoke-WebRequest -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/samples/Olympic%20Dam" `
  -Method GET

# Get summary for a site
Invoke-WebRequest -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/samples/Olympic%20Dam/summary" `
  -Method GET
```