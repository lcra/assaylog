from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError
from app import database

router = APIRouter()

class SampleIn(BaseModel):
    site: str = Field(min_length=1, max_length=200)
    depth_m: float = Field(gt=0)
    element: str = Field(min_length=1, max_length=10)
    grade: float = Field(ge=0)

@router.post("/samples", status_code=201)
def log_sample(sample: SampleIn):
    try:
        record = database.put_sample(
            site=sample.site,
            depth_m=sample.depth_m,
            element=sample.element,
            grade=sample.grade,
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
