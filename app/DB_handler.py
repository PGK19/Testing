import sqlite3
from database.db import DB_PATH

def execute_query(sql: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    except Exception as e:
        raise Exception(f"SQL Error: {str(e)}")
    finally:
        conn.close()