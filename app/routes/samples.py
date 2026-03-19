from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app import database

router = APIRouter()

class SampleIn(BaseModel):
    site: str
    depth_m: float
    element: str
    grade: float

@router.post("/samples", status_code=201)
def log_sample(sample: SampleIn):
    record = database.put_sample(
        site=sample.site,
        depth_m=sample.depth_m,
        element=sample.element,
        grade=sample.grade,
    )
    return {"message": "Sample logged", "sample": record}

@router.get("/samples/{site}")
def get_samples(site: str):
    results = database.get_samples_by_site(site)
    if not results:
        raise HTTPException(status_code=404, detail=f"No samples found for site: {site}")
    return {"site": site, "samples": results}

@router.get("/samples/{site}/summary")
def get_summary(site: str):
    results = database.get_samples_by_site(site)
    if not results:
        raise HTTPException(status_code=404, detail=f"No samples found for site: {site}")
    grades = [float(s["grade"]) for s in results]
    avg_grade = sum(grades) / len(grades)
    return {
        "site": site,
        "sample_count": len(results),
        "average_grade": round(avg_grade, 4)
    }
