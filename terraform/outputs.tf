output "api_url" {
  description = "Base URL of the API Gateway endpoint"
  value       = aws_apigatewayv2_api.assaylog.api_endpoint
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.assaylog.function_name
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.samples.name
}
