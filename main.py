from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from agent import chat_with_user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    
class ChatResponse(BaseModel):
    response: str
    
@app.get("/")
def health_check():
    return { "status": "ok", "service": "chat-service", "message": "API is running"}
    
    
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        if not request.message.strip():
            return ChatResponse(response="Please provide a valid message.")
        response = chat_with_user(request.message, request.history)
        return ChatResponse(response=response)
    except Exception as e:
        return ChatResponse(response=f"An error occurred: {str(e)}")
   