from fastapi import Header, HTTPException
import re

ROLES = {
    "admin": {
        "allowed_tables": ["students", "courses", "enrollments", "grades", "fee_records", "admin_logs", "users"],
        "system_context": "You are an AI assistant for the school administration system. You have FULL ACCESS to all database tables. Query the database to get exact numbers."
    },
    "student": {
        "allowed_tables": ["courses", "enrollments"],
        "system_context": "You are an AI assistant for students. You have LIMITED ACCESS to only public courses and enrollments. You MUST NOT reveal individual student records."
    }
}

async def get_current_user(x_user_role: str = Header("student"), x_username: str = Header("anonymous")):
    if x_user_role not in ROLES:
        raise HTTPException(status_code=403, detail="Invalid role")
    return {"role": x_user_role, "username": x_username, "rbac": ROLES[x_user_role]}

def validate_sql(sql: str, allowed_tables: list[str]) -> dict:
    sql_lower = sql.lower()
    
    # Block write operations
    for op in ['insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate']:
        if op in sql_lower:
            return {"valid": False, "reason": f"Write operation '{op}' is not allowed."}
            
    # Extract tables
    tables = re.findall(r'(?:from|join)\s+([a-z_][a-z0-9_]*)', sql_lower)
    for table in tables:
        if table not in allowed_tables:
            return {"valid": False, "reason": f"Access to table '{table}' is not allowed for your role."}
            
    return {"valid": True}