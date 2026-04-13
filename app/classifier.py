from app.ollama_client import call_ollama

def classify_query(query):
    prompt = f"""
    Classify the query into:
    DB_QUERY or KNOWLEDGE

    Query: {query}
    """

    return call_ollama(prompt).strip()