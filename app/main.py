from fastapi import FastAPI
from mangum import Mangum
from app.routes import samples

app = FastAPI(title="AssayLog", description="Mineral assay logging API")

app.include_router(samples.router)

handler = Mangum(app)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AssayLog"}