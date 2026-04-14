from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os

from database.db import init_db, get_db
from app.RAG_handler import index_schemas
from app.auth import get_current_user
from app.chatbot import process_chat

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await index_schemas()
    yield

app = FastAPI(lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatReq(BaseModel):
    message: str
    history: list = []


# ─── API ROUTES ────────────────────────────────────────────────────────

@app.get("/api/stats")
def stats(user_info: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    if user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    c = db.cursor()
    res = {
        "totalStudents": c.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "activeStudents": c.execute("SELECT COUNT(*) FROM students WHERE status='active'").fetchone()[0],
        "totalCourses": c.execute("SELECT COUNT(*) FROM courses").fetchone()[0],
        "totalEnrollments": c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0],
        "avgGpa": c.execute("SELECT ROUND(AVG(gpa),2) FROM students").fetchone()[0],
        "pendingFees": c.execute("SELECT COUNT(*) FROM fee_records WHERE status='overdue'").fetchone()[0],
        "deptBreakdown": [{"department": row["department"], "count": row["count"]} for row in c.execute("SELECT department, COUNT(*) as count FROM students GROUP BY department").fetchall()],
        "recentStudents": [dict(row) for row in c.execute("SELECT name, department, year, gpa FROM students ORDER BY enrolled_at DESC LIMIT 5").fetchall()]
    }
    return res

@app.post("/api/chat")
async def chat_endpoint(req: ChatReq, user_info: dict = Depends(get_current_user)):
    response = await process_chat(req.message, req.history, user_info)
    
    # Hide SQL from students
    if user_info["role"] != "admin":
        response["sql"] = None
        
    return response


# ─── FRONTEND ROUTE ────────────────────────────────────────────────────

@app.get("/")
def serve_frontend():
    """Serves the index.html file from the public directory"""
    index_path = os.path.join("public", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found. Please ensure public/index.html exists."}