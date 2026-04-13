from fastapi import FastAPI
from app.chatbot import chatbot

app = FastAPI()

@app.post("/chat")
def chat(data: dict):
    return {
        "response": chatbot(data["query"], data["role"])
    }