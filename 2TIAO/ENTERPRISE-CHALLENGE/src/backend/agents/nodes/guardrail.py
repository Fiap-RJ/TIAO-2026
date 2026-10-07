"""Nó de guardrail — valida a resposta gerada antes de entregar ao usuário."""

import json
import logging
import time

from agents.state import AgentState
from services.guardrails import validar_resposta

logger = logging.getLogger(__name__)


def guardrail(state: AgentState) -> dict:
    """Aplica validações de segurança na resposta do LLM."""

    start_time = time.perf_counter()

    resultado = validar_resposta(state.answer)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    log_data = {
        "request_id": getattr(state, "request_id", "unknown"),
        "node": "guardrail",
        "latency_ms": latency_ms,
        "status": "success" if resultado.aprovado else "blocked",
        "violacoes": resultado.violacoes if resultado.violacoes else [],
        "disclaimer_adicionado": resultado.disclaimer_adicionado,
    }

    if not resultado.aprovado or resultado.violacoes:
        logger.warning(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))

    return {
        "answer": resultado.resposta_final,
        "violacoes": list(resultado.violacoes),
        "bloqueado": not resultado.aprovado,
    }
