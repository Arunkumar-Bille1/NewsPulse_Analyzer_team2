# news_backend/chatbot_routes.py
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai  # Google Gen AI SDK[web:31][web:28]

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

genai.configure(api_key=API_KEY)  # Configure Gemini client[web:31][web:28]
model = genai.GenerativeModel("gemini-2.0-flash")  # Or other available model[web:17]

router = APIRouter(prefix="/api/chat", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        chat_session = model.start_chat(history=[])
        res = chat_session.send_message(req.message)
        return ChatResponse(reply=res.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
