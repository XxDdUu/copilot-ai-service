from app.core.model import get_embedding_model

class EmbeddingService:

    def embed_documents(self, texts):
        return get_embedding_model().encode(
            texts,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, query):
        return get_embedding_model().encode(
            query,
            normalize_embeddings=True
        ).tolist()
