import json
from .classifier import classify_intent
from .RAG_handler import retrieve_context, generate_sql
from .auth import validate_sql
from .DB_handler import execute_query
from .ollama_client import chat

async def process_chat(message: str, history: list, user_info: dict) -> dict:
    role = user_info["role"]
    rbac = user_info["rbac"]
    
    intent = classify_intent(message)
    if intent == "greeting":
        ans = await chat(rbac["system_context"], [{"role": "user", "content": message}])
        return {"answer": ans, "sql": None, "results": []}

    try:
        # 1. Retrieve & Generate SQL
        context = await retrieve_context(message, role)
        raw_sql = await generate_sql(message, context, rbac)
        
        # 2. Validate
        validation = validate_sql(raw_sql, rbac["allowed_tables"])
        if not validation["valid"]:
            deny_message = "permission restrict" if role != "admin" else f"Access denied: {validation['reason']}"
            return {"answer": deny_message, "sql": raw_sql, "results": []}

        # 3. Execute
        results = execute_query(raw_sql)
        
        # 4. Generate Answer
        results_str = json.dumps(results[:20], indent=2) if results else "No results found"
        answer_prompt = f"""{rbac["system_context"]}
User asked: "{message}"
DB Results:
{results_str}
Provide a clear, helpful, conversational answer based ONLY on these results."""
        
        answer = await chat(answer_prompt, [])
        return {"answer": answer, "sql": raw_sql, "results": results}

    except Exception as e:
        return {"answer": "I had trouble querying the database.", "sql": locals().get('raw_sql', ''), "error": str(e)}