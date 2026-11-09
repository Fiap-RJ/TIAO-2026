from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.cardioia.services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["Chat Triagem"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    origem: str
    resposta: str
    session_id: Optional[str] = None


@router.post("/", response_model=ChatResponse)
def rota_chat(payload: ChatRequest):
    """Atende à rota POST /api/chat consumida pelo Web e Mobile."""
    resultado = chat_service.processar_mensagem(
        mensagem=payload.message,
        session_id=payload.session_id
    )
    return ChatResponse(**resultado)