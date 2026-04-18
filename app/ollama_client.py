import httpx
import os

# ─── API CONFIGURATION ─────────────────────────────────────────────────
# Choose your provider. Here are examples for Groq and OpenAI.

# Example for GROQ (Free & Fast):
API_KEY = "apikey"
BASE_URL = "https://api.groq.com/openai/v1"
MODEL = "llama-3.1-8b-instant"  # Groq's optimized version of GPT-3.5

# Example for OPENAI:
# API_KEY = "sk-your_openai_api_key_here"
# BASE_URL = "https://api.openai.com/v1"
# MODEL = "gpt-4o-mini"
# ───────────────────────────────────────────────────────────────────────

async def chat(system_prompt: str, messages: list, temperature: float = 0.1, max_tokens: int = 1024) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    formatted_messages = [{"role": "system", "content": system_prompt}] + messages
    
    payload = {
        "model": MODEL,
        "messages": formatted_messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            print(f"API Error: {e.response.text}")
            return "Error: Check your API Key and terminal for details."
        except Exception as e:
            print(f"Connection Error: {e}")
            return "Error communicating with AI API."

async def embed(text: str) -> list[float]:
    """
    Since we switched to an external API for chat, we will bypass local embeddings.
    Returning an empty list automatically triggers the 'keyword search' fallback 
    in your rag_handler.py, which works perfectly for a small database schema!
    """
    return []