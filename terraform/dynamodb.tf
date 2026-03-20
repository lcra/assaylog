resource "aws_dynamodb_table" "samples" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "site"
  range_key    = "id"

  attribute {
    name = "site"
    type = "S"
  }

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Project = "AssayLog"
  }
}
