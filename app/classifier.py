def classify_intent(query: str) -> str:
    """
    Very simple classifier to determine if query needs DB access.
    In a full app, you might use Ollama here to classify the intent.
    """
    greetings = ["hello", "hi", "hey", "who are you"]
    if any(query.lower().strip().startswith(g) for g in greetings):
        return "greeting"
    return "database_query"