from langchain_core.tools import tool
from sqlalchemy import text
from app.vectorstore.pgvector_store import engine

@tool
def query_database(sql_query: str) -> str:
    """
    Execute a read-only SQL query on the PostgreSQL database.
    Use this to get metadata about uploaded documents, users, departments, or chat sessions.
    
    ONLY SELECT statements are permitted. Do not attempt modification operations (INSERT, UPDATE, DELETE).
    
    Args:
        sql_query (str): The SELECT SQL statement to execute.
    """
    cleaned_query = sql_query.strip().lower()
    if not cleaned_query.startswith("select"):
        return "Error: Only read-only SELECT queries are allowed."

    # Basic guardrails against destructive statements
    forbidden_keywords = ["insert", "update", "delete", "drop", "alter", "truncate", "create"]
    for keyword in forbidden_keywords:
        if f" {keyword} " in f" {cleaned_query} " or cleaned_query.startswith(keyword):
            return f"Error: Write operations are forbidden (found keyword '{keyword}')."

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            if not result.returns_rows:
                return "Query executed successfully, but returned no rows."
            
            keys = result.keys()
            rows = result.fetchall()
            if not rows:
                return "Query returned 0 rows."
            
            # Format rows as list of dicts
            formatted_rows = []
            for r in rows:
                formatted_rows.append({key: str(val) for key, val in zip(keys, r)})
            return str(formatted_rows)
    except Exception as e:
        return f"Error executing SQL query: {str(e)}"
