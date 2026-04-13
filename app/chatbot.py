from app.classifier import classify_query
from app.DB_handler import handle_db_query
from app.RAG_handler import handle_rag_query

def chatbot(query, role):
    query_type = classify_query(query)

    if query_type == "DB_QUERY":
        return handle_db_query(query, role)

    return handle_rag_query(query, role)