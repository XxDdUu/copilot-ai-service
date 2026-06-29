from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.api.search import router as search_router

app = FastAPI(
    title="Enterprise AI Copilot",
    version="1.0.0"
)

app.include_router(ingest_router)
app.include_router(search_router)
@app.get("/health")
def health():
    return {"status": "UP"}
