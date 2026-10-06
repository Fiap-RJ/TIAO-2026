"""Rota de chat — interface entre o front-end e o pipeline RAG."""

import logging
import traceback
import uuid
import time

from fastapi import APIRouter, HTTPException


from api.routes.metrics import registrar_execucao
from agents import app as agent_app
from domain.schemas import ChatRequest, ChatResponse, FonteDado
from services.history_store import salvar_interacao

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_com_agente(request: ChatRequest):
    start_time = time.perf_counter()
    """Recebe a pergunta do paciente e retorna a resposta fundamentada via RAG."""
    try:
        req_id = str(uuid.uuid4())

        resultado = agent_app.invoke({"question": request.mensagem,"request_id": req_id})

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        # Verifica se houve bloqueio por guardrails
        violacoes = resultado.get("violacoes", [])
        bloqueado = len(violacoes) > 0

        # Alimenta as métricas
        registrar_execucao(
            latencia_total_ms=latency_ms, 
            bloqueado=bloqueado, 
            violacoes=violacoes
        )

        return ChatResponse(
            resposta=resultado["answer"], 
            fontes=fontes,
            painel_utilizado=painel_utilizado,
            guardrails_acionados=violacoes
        )
    
        fontes = [
            FonteDado(
                painel=d.metadata.get("painel", "N/A"),
                marcador=d.metadata.get("caracteristica", "N/A"),
                gene=d.metadata.get("gene", "N/A"),
                conclusao_curta=d.metadata.get("conclusao_curta", "N/A"),
            )
            for d in resultado.get("context", [])
        ]

        # Determina o painel principal a partir das fontes
        
        painel_utilizado = fontes[0].painel if fontes else "Geral"

        try:
            salvar_interacao(
                paciente_id=request.paciente_id,
                pergunta=resultado.get("question", request.mensagem),
                resposta=resultado["answer"],
                fontes=[fonte.model_dump() for fonte in fontes],
            )
        except Exception:
            logger.warning("Falha ao persistir histórico da interação", exc_info=True)

        return ChatResponse(resposta=resultado["answer"], fontes=fontes, painel_utilizado=painel_utilizado,
            guardrails_acionados=resultado.get("violacoes", [])
        )
    except Exception as e:
        logger.error("Erro no pipeline RAG: %s", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
