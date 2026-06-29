from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from app.services.minio_service import minio_service
from app.services.pdf_service import PdfService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.vectorstore.pgvector_store import pgvector_store
import tempfile
import os

router = APIRouter(
    prefix="/api",
    tags=["Ingest"]
)
class IngestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    document_id: int = Field(alias="documentId")
    bucket_name: str = Field(alias="bucketName")
    object_key: str = Field(alias="objectKey")

pdf_service = PdfService()
chunking_service = ChunkingService()
embedding_service = EmbeddingService()

@router.post("/ingest")
async def ingest(request: IngestRequest):
    try:
        # Retrieve PDF bytes from MinIO
        file_bytes = minio_service.get_object_bytes(request.bucket_name, request.object_key)
        
        # Write to temporary file for compatibility with PdfService
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_pdf.write(file_bytes)
            temp_path = temp_pdf.name
            
        try:
            text = pdf_service.extract_text(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        if not text or not text.strip():
            return {"status": "success", "message": "Document contains no extractable text."}
            
        # Segment text into chunks
        chunks = chunking_service.chunk_text(text)
        
        # Generate embeddings for the chunks
        embeddings = embedding_service.embed_documents(chunks)
        
        # Save chunks and vectors in PostgreSQL pgvector store
        pgvector_store.save_chunks(request.document_id, chunks, embeddings)
        
        return {"status": "success", "message": f"Successfully ingested {len(chunks)} chunks."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))