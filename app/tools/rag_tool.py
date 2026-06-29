from langchain_core.tools import tool
from app.services.embedding_service import EmbeddingService
from app.vectorstore.pgvector_store import pgvector_store

embedding_service = EmbeddingService()

@tool
def query_knowledge_base(query: str) -> str:
    """
    Search the knowledge base for information about documents, policies, or technical specs.
    Use this tool when the user asks questions about specific loaded PDFs, documents, or knowledge.
    
    Args:
        query (str): The search query to locate relevant parts of documents.
    """
    try:
        query_emb = embedding_service.embed_query(query)
        results = pgvector_store.similarity_search(query_emb, limit=5)
        if not results:
            return "No matching documents or knowledge found."
        
        formatted_results = []
        for idx, r in enumerate(results):
            formatted_results.append(
                f"Source {idx+1} (Doc ID: {r['document_id']}, Chunk: {r['chunk_index']}):\n{r['content']}"
            )
        return "\n\n---\n\n".join(formatted_results)
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"
