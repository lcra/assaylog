import boto3
import uuid
import os
from decimal import Decimal

TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "assaylog-samples")
REGION = os.environ.get("AWS_REGION", "ap-southeast-2")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def _convert_decimals(item: dict) -> dict:
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in item.items()}


def put_sample(site: str, depth_m: float, element: str, grade: float) -> dict:
    item = {
        "site": site,
        "id": str(uuid.uuid4()),
        "depth_m": Decimal(str(depth_m)),
        "element": element,
        "grade": Decimal(str(grade)),
    }
    table.put_item(Item=item)
    return _convert_decimals(item)


def get_samples_by_site(site: str) -> list:
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("site").eq(site)
    )
    return [_convert_decimals(item) for item in response.get("Items", [])]