from app.ollama_client import call_ollama
from app.auth import get_role_prompt

def handle_rag_query(query, role):
    prompt = f"""
    {get_role_prompt(role)}

    Question: {query}
    """

    return call_ollama(prompt)