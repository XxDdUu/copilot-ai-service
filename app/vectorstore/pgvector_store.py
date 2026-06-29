from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector
from app.core.config import settings
from datetime import datetime

# Initialize SQLAlchemy
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1024))  # 1024 dimensions for BAAI/bge-m3
    created_at = Column(DateTime, default=datetime.utcnow)

class PgVectorStore:
    def __init__(self):
        # Flyway manages schema creation, but we ensure connection works
        pass

    def save_chunks(self, document_id: int, chunks: list[str], embeddings: list[list[float]]):
        session = SessionLocal()
        try:
            for idx, (content, embedding) in enumerate(zip(chunks, embeddings)):
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=idx,
                    content=content,
                    embedding=embedding
                )
                session.add(db_chunk)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def similarity_search(self, query_embedding: list[float], limit: int = 5) -> list[dict]:
        session = SessionLocal()
        try:
            # Sort by cosine distance: 1 - cosine similarity
            results = (
                session.query(DocumentChunk)
                .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                .limit(limit)
                .all()
            )
            return [
                {
                    "content": r.content,
                    "document_id": r.document_id,
                    "chunk_index": r.chunk_index,
                }
                for r in results
            ]
        finally:
            session.close()

pgvector_store = PgVectorStore()
