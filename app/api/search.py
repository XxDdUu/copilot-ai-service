from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.embedding_service import EmbeddingService
from app.vectorstore.pgvector_store import pgvector_store

router = APIRouter(
    prefix="/api",
    tags=["Search"]
)

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

embedding_service = EmbeddingService()

@router.post("/search")
async def search(request: SearchRequest):
    try:
        query_emb = embedding_service.embed_query(request.query)
        results = pgvector_store.similarity_search(query_emb, limit=request.limit)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
