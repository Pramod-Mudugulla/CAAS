import requests
from fastapi import FastAPI
from pydantic import BaseModel
import uuid

app = FastAPI()

chat_sessions = {}

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

@app.post("/chat")
def chat(req: ChatRequest):

    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    chat_sessions[session_id].append(f"user: {req.message}")
    
    history = chat_sessions[session_id][-5:]

    prompt = "\n".join(history) + "\nassistant: "

    try:
        response = requests.post( 
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        reply = response.json()['response']

        chat_sessions[session_id].append(f"assistant: {reply}")

        return {
            "response": reply,
            'session_id': session_id
        }
    except Exception as e:
        return {"error": str(e)}