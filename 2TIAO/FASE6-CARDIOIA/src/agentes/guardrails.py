"""
Guardrails — CardioIA Fase 6
============================

Validação determinística (sem LLM) na entrada e na saída do fluxo.

- ``validar_entrada_atendimento`` (input guardrail do Orquestrador, modo
  bloqueante: ``run_in_parallel=False`` evita gastar tokens antes de validar).
  Dispara se o paciente estiver ausente do contexto, se a mensagem estiver
  vazia ou tiver mais de 2000 caracteres, ou se pedir prescrição/dose/remédio
  (``PEDIDOS_PRESCRICAO``).
- ``validar_recomendacao_final`` (output guardrail do Planejador): delega a
  ``verificar_recomendacao``; qualquer violação dispara o tripwire e o
  pipeline devolve a recomendação determinística (fallback seguro).
"""

import logging
from typing import Any

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    input_guardrail,
    output_guardrail,
)

from agentes.contexto import ContextoAtendimento
from domain.constantes import PEDIDOS_PRESCRICAO
from domain.schemas import RecomendacaoFinal
from services.recomendacao import verificar_recomendacao

logger = logging.getLogger("cardioia.agentes.guardrails")

MAX_CARACTERES_ENTRADA = 2000


def _texto_do_conteudo(conteudo: Any) -> str:
    """Conteúdo de mensagem: ``str`` ou lista de partes (``{"type": "input_text", "text": ...}``)."""
    if isinstance(conteudo, str):
        return conteudo
    if isinstance(conteudo, list):
        partes = [p.get("text", "") for p in conteudo if isinstance(p, dict)]
        return " ".join(t for t in partes if isinstance(t, str))
    return ""


def extrair_ultima_mensagem_usuario(entrada: str | list[Any]) -> str:
    """Texto da última mensagem ``user``. Com sessão, o SDK pode entregar uma lista de itens."""
    if isinstance(entrada, str):
        return entrada
    for item in reversed(entrada):
        if isinstance(item, dict) and item.get("role") == "user":
            return _texto_do_conteudo(item.get("content"))
    return ""


def _bloquear(motivo: str) -> GuardrailFunctionOutput:
    logger.warning("entrada bloqueada: %s", motivo)
    return GuardrailFunctionOutput(
        output_info={"motivo": motivo}, tripwire_triggered=True
    )


@input_guardrail(run_in_parallel=False)
async def validar_entrada_atendimento(
    ctx: RunContextWrapper[ContextoAtendimento], agent: Agent, input: str | list[Any]
) -> GuardrailFunctionOutput:
    """Bloqueia entradas fora do escopo informativo antes de qualquer chamada ao LLM."""
    if getattr(ctx.context, "paciente", None) is None:
        return _bloquear("dados do paciente ausentes no contexto do atendimento")
    texto = extrair_ultima_mensagem_usuario(input).strip()
    if not texto:
        return _bloquear("mensagem vazia")
    if len(texto) > MAX_CARACTERES_ENTRADA:
        return _bloquear(f"mensagem com mais de {MAX_CARACTERES_ENTRADA} caracteres")
    if PEDIDOS_PRESCRICAO.search(texto):
        return _bloquear(
            "o CardioIA é informativo e não indica medicamentos, prescrições ou doses; "
            "consulte um profissional de saúde"
        )
    return GuardrailFunctionOutput(
        output_info={"motivo": None}, tripwire_triggered=False
    )


@output_guardrail
async def validar_recomendacao_final(
    ctx: RunContextWrapper[ContextoAtendimento], agent: Agent, output: RecomendacaoFinal
) -> GuardrailFunctionOutput:
    """Confere a saída do Planejador contra o risco e os protocolos calculados pelas tools."""
    violacoes = verificar_recomendacao(
        output, ctx.context.avaliacao_risco, ctx.context.resultado_protocolos
    )
    if violacoes:
        logger.warning("guardrail de saída: %s", violacoes)
    return GuardrailFunctionOutput(
        output_info={"violacoes": violacoes}, tripwire_triggered=bool(violacoes)
    )
