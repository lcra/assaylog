variable "aws_region" {
  description = "AWS region to deploy into"
  default     = "ap-southeast-2"
}

variable "table_name" {
  description = "DynamoDB table name"
  default     = "assaylog-samples"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  default     = "assaylog"
}

variable "idempotency_table_name" {
  description = "DynamoDB table name for idempotency keys"
  default     = "assaylog-idempotency"
}