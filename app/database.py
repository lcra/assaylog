import boto3
import uuid
import os

TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "assaylog-samples")
REGION = os.environ.get("AWS_REGION", "ap-southeast-2")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def put_sample(site: str, depth_m: float, element: str, grade: float) -> dict:
    item = {
        "site": site,
        "id": str(uuid.uuid4()),
        "depth_m": str(depth_m),
        "element": element,
        "grade": str(grade),
    }
    table.put_item(Item=item)
    return item


def get_samples_by_site(site: str) -> list:
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("site").eq(site)
    )
    return response.get("Items", [])