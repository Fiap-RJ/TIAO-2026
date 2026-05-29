"""Rota de chat — interface entre o front-end e o pipeline RAG."""

import logging
import traceback

from fastapi import APIRouter, HTTPException

from agents import app as agent_app
from domain.schemas import ChatRequest, ChatResponse, FonteDado

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_com_agente(request: ChatRequest):
    """Recebe a pergunta do paciente e retorna a resposta fundamentada via RAG."""
    try:
        resultado = agent_app.invoke({"question": request.mensagem})

        fontes = [
            FonteDado(
                painel=d.metadata.get("painel", "N/A"),
                marcador=d.metadata.get("caracteristica", "N/A"),
                gene=d.metadata.get("gene", "N/A"),
                conclusao_curta=d.metadata.get("conclusao_curta", "N/A"),
            )
            for d in resultado.get("context", [])
        ]

        return ChatResponse(resposta=resultado["answer"], fontes=fontes)

    except Exception as e:
        logger.error("Erro no pipeline RAG: %s", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
