from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

samples_db: List[dict] = []

class SampleIn(BaseModel):
    site: str
    depth_m: float
    element: str
    grade: float

@router.post("/samples", status_code=201)
def log_sample(sample: SampleIn):
    record = sample.model_dump()
    samples_db.append(record)
    return {"message": "Sample logged", "sample": record}


@router.get("/samples/{site}")
def get_samples(site: str):
    results = [s for s in samples_db if s["site"] == site]
    if not results:
        raise HTTPException(status_code=404, detail=f"No samples found for site: {site}")
    return {"site": site, "samples": results}


@router.get("/samples/{site}/summary")
def get_summary(site: str):
    results = [s for s in samples_db if s["site"] == site]
    if not results:
        raise HTTPException(status_code=404, detail=f"No samples found for site: {site}")
    avg_grade = sum(s["grade"] for s in results) / len(results)
    return {
        "site": site,
        "sample_count": len(results),
        "average_grade": round(avg_grade, 4)
    }