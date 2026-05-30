"""Nó de guardrail — valida a resposta gerada antes de entregar ao usuário."""

import logging

from agents.state import AgentState
from services.guardrails import validar_resposta

logger = logging.getLogger(__name__)


def guardrail(state: AgentState) -> dict:
    """Aplica validações de segurança na resposta do LLM."""
    resultado = validar_resposta(state.answer)

    if not resultado.aprovado:
        logger.warning("GUARDRAIL ATIVADO — Violações: %s", resultado.violacoes)

    if resultado.disclaimer_adicionado:
        logger.info("Disclaimer adicionado automaticamente (ausente na resposta original)")

    if resultado.violacoes:
        logger.warning("Violações detectadas: %s", resultado.violacoes)

    return {"answer": resultado.resposta_final}
