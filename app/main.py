from fastapi import FastAPI
from app.routes import samples

app = FastAPI(title="AssayLog", description="Mineral assay logging API")

app.include_router(samples.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AssayLog"}