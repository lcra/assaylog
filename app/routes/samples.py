from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator
from botocore.exceptions import ClientError
from app import database

router = APIRouter()

class SampleIn(BaseModel):
    site: str = Field(min_length=1, max_length=200)
    hole_id: str = Field(min_length=1, max_length=100)
    depth_m: float = Field(gt=0)
    sample_from_m: float = Field(ge=0)
    sample_to_m: float = Field(gt=0)
    element: str = Field(min_length=1, max_length=10)
    grade: float = Field(ge=0)
    assay_method: str = Field(min_length=1, max_length=50)
    unit: str = Field(min_length=1, max_length=20)
    batch_id: Optional[str] = Field(default=None, max_length=100)
    collected_at: Optional[datetime] = None
    lab_received_at: Optional[datetime] = None
    status: str = Field(default="submitted", min_length=1, max_length=50)
    source_system: Optional[str] = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_interval(self):
        if self.sample_to_m <= self.sample_from_m:
            raise ValueError("sample_to_m must be greater than sample_from_m")
        return self

@router.post("/samples", status_code=201)
def log_sample(sample: SampleIn):
    try:
        record = database.put_sample(
            site=sample.site,
            hole_id=sample.hole_id,
            depth_m=sample.depth_m,
            sample_from_m=sample.sample_from_m,
            sample_to_m=sample.sample_to_m,
            element=sample.element,
            grade=sample.grade,
            assay_method=sample.assay_method,
            unit=sample.unit,
            batch_id=sample.batch_id,
            collected_at=sample.collected_at,
            lab_received_at=sample.lab_received_at,
            status=sample.status,
            source_system=sample.source_system,
        )
    except ClientError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"message": "Sample logged", "sample": record}

@router.get("/samples/{site}")
def get_samples(site: str):
    try:
        results = database.get_samples_by_site(site)
    except ClientError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    if not results:
        raise HTTPException(status_code=404, detail=f"No samples found for site: {site}")
    return {"site": site, "samples": results}

@router.get("/samples/{site}/summary")
def get_summary(site: str):
    try:
        results = database.get_samples_by_site(site)
    except ClientError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    if not results:
        raise HTTPException(status_code=404, detail=f"No samples found for site: {site}")
    grades = [float(s["grade"]) for s in results]
    avg_grade = sum(grades) / len(grades)
    return {
        "site": site,
        "sample_count": len(results),
        "average_grade": round(avg_grade, 4)
    }
