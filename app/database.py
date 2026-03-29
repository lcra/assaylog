import boto3
import uuid
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "assaylog-samples")
REGION = os.environ.get("AWS_REGION", "ap-southeast-2")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def _convert_decimals(item: dict) -> dict:
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in item.items()}


def put_sample(
    site: str,
    hole_id: str,
    depth_m: float,
    sample_from_m: float,
    sample_to_m: float,
    element: str,
    grade: float,
    assay_method: str,
    unit: str,
    batch_id: Optional[str] = None,
    collected_at: Optional[datetime] = None,
    lab_received_at: Optional[datetime] = None,
    status: str = "submitted",
    source_system: Optional[str] = None,
) -> dict:
    item = {
        "site": site,
        "id": str(uuid.uuid4()),
        "hole_id": hole_id,
        "depth_m": Decimal(str(depth_m)),
        "sample_from_m": Decimal(str(sample_from_m)),
        "sample_to_m": Decimal(str(sample_to_m)),
        "element": element,
        "grade": Decimal(str(grade)),
        "assay_method": assay_method,
        "unit": unit,
        "status": status,
    }
    if batch_id is not None:
        item["batch_id"] = batch_id
    if collected_at is not None:
        item["collected_at"] = collected_at.isoformat()
    if lab_received_at is not None:
        item["lab_received_at"] = lab_received_at.isoformat()
    if source_system is not None:
        item["source_system"] = source_system
    table.put_item(Item=item)
    return _convert_decimals(item)


def get_samples_by_site(site: str) -> list:
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("site").eq(site)
    )
    return [_convert_decimals(item) for item in response.get("Items", [])]