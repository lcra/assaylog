from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.routes import samples

app = FastAPI(title="AssayLog", description="Mineral assay logging API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(samples.router)

handler = Mangum(app)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "AssayLog"}