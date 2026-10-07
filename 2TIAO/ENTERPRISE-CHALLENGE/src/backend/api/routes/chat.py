"""Rota de chat — interface entre o front-end e o pipeline RAG."""

import logging
import time
import uuid

from fastapi import APIRouter, HTTPException

from agents import app as agent_app
from api.routes.metrics import registrar_execucao
from domain.schemas import ChatRequest, ChatResponse, FonteDado
from services.history_store import salvar_interacao

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat_com_agente(request: ChatRequest) -> ChatResponse:
    """Recebe a pergunta do paciente e retorna a resposta fundamentada via RAG.

    Rota síncrona de propósito: `agent_app.invoke` é bloqueante e o FastAPI
    executa rotas `def` no threadpool, sem travar o event loop.
    """
    req_id = str(uuid.uuid4())
    inicio = time.perf_counter()

    try:
        resultado = agent_app.invoke(
            {
                "question": request.mensagem,
                "request_id": req_id,
                "detail_level": request.nivel_detalhe,
            }
        )
    except Exception:
        # Decisão consciente: falhas (500) ainda NÃO entram no /metrics, cujo
        # contrato atual não tem campo de erro. A contabilidade de erros
        # (total/latência/taxa de erro) fica para a A5.1.
        logger.exception("Erro no pipeline RAG (request_id=%s)", req_id)
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar a pergunta. request_id={req_id}",
        ) from None

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

    # Violações e bloqueio vêm do nó `guardrail` (AgentState.violacoes / .bloqueado)
    violacoes = list(resultado.get("violacoes", []))
    bloqueado = bool(resultado.get("bloqueado", False))

    latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)
    registrar_execucao(latencia_total_ms=latencia_ms, bloqueado=bloqueado, violacoes=violacoes)

    try:
        salvar_interacao(
            paciente_id=request.paciente_id,
            pergunta=resultado.get("question", request.mensagem),
            resposta=resultado["answer"],
            fontes=[fonte.model_dump() for fonte in fontes],
        )
    except Exception:
        logger.warning("Falha ao persistir histórico da interação", exc_info=True)

    return ChatResponse(
        resposta=resultado["answer"],
        fontes=fontes,
        painel_utilizado=painel_utilizado,
        guardrails_acionados=violacoes,
    )
