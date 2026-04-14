import math
from .ollama_client import embed, chat

SCHEMA_CHUNKS = [
    {"id": "students", "table": "students", "roles": ["admin"], "text": "Table: students. Columns: id, name, email, department, year, gpa, status. Use for: student counts, finding students, GPA."},
    {"id": "courses", "table": "courses", "roles": ["admin", "student"], "text": "Table: courses. Columns: id, code, name, department, credits, instructor, capacity, enrolled. Use for: available courses, seats open."},
    {"id": "enrollments", "table": "enrollments", "roles": ["admin", "student"], "text": "Table: enrollments. Columns: id, student_id, course_id, semester, grade. Use for: enrollment counts."},
    {"id": "fees", "table": "fee_records", "roles": ["admin"], "text": "Table: fee_records. Columns: id, student_id, amount, due_date, status. Use for: overdue fees, paid tracking."}
]

vector_store = []

def cosine_sim(a, b):
    if not a or not b: return 0
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(x*x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0

async def index_schemas():
    print("📚 Indexing schema chunks for RAG...")
    for chunk in SCHEMA_CHUNKS:
        embedding = await embed(chunk["text"])
        vector_store.append({**chunk, "embedding": embedding})
    print(f"✅ Indexed {len(vector_store)} chunks")

async def retrieve_context(query: str, role: str, top_k: int = 3):
    query_emb = await embed(query)
    accessible = [c for c in vector_store if role in c["roles"]]
    
    if not query_emb:
        # Fallback keyword match
        return accessible[:top_k]
        
    for chunk in accessible:
        chunk["score"] = cosine_sim(query_emb, chunk["embedding"])
        
    accessible.sort(key=lambda x: x["score"], reverse=True)
    return accessible[:top_k]

async def generate_sql(query: str, context_chunks: list, rbac: dict) -> str:
    schema_context = "\n\n".join(c["text"] for c in context_chunks)
    prompt = f"""You are a SQL generator for a SQLite database.
ALLOWED TABLES: {', '.join(rbac['allowed_tables'])}
RELEVANT SCHEMA: {schema_context}
RULES:
- Only SELECT queries
- Limit 50 unless counting
- Return ONLY the SQL, no markdown, no backticks.
Question: {query}
SQL:"""
    sql = await chat(prompt, [], temperature=0.0)
    return sql.replace('```sql', '').replace('```', '').strip()