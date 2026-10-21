"""
Contexto do atendimento — CardioIA Fase 6
=========================================

``ContextoAtendimento`` é o estado local compartilhado entre os agentes. É
passado como ``context=`` ao ``Runner.run`` e chega às tools, aos guardrails e
aos callbacks de handoff como ``RunContextWrapper[ContextoAtendimento]``
(``ctx.context``). Ele **não** é enviado ao LLM: é por ele que a predição
calculada pelo Analista chega ao Especialista e ao Planejador (R11.3).

Escopo dos campos (R10.4):

- ``cadeia_agentes``: agentes do turno corrente; o pipeline a reinicia em cada
  chamada de ``executar_atendimento``;
- ``notas_handoff``, ``avaliacao_risco`` e ``resultado_protocolos``: persistem
  durante todo o atendimento (perguntas de acompanhamento e gating dependem deles).
"""

from dataclasses import dataclass, field
from typing import Any

from domain.schemas import (
    AvaliacaoRisco,
    DadosPaciente,
    NotaHandoff,
    ResultadoProtocolos,
)
from services.risco import Preditor


@dataclass
class ContextoAtendimento:
    """Estado de um atendimento (reaproveitado entre turnos no modo interativo)."""

    atendimento_id: str
    paciente: DadosPaciente
    preditor: Preditor
    avaliacao_risco: AvaliacaoRisco | None = None
    resultado_protocolos: ResultadoProtocolos | None = None
    notas_handoff: list[NotaHandoff] = field(default_factory=list)
    cadeia_agentes: list[str] = field(default_factory=lambda: ["Orquestrador"])


# --- predicados de gating ---------------------------------------------------------
# Assinatura exigida pelo SDK em ``is_enabled``: (RunContextWrapper, Agent) -> bool.
# Ficam aqui para serem compartilhados por tools.py e orquestrador.py sem import
# circular; os três são mutuamente exclusivos (exatamente um é verdadeiro).
def risco_pendente(ctx: Any, agent: Any) -> bool:
    """Etapa 1: o risco ainda não foi calculado."""
    return ctx.context.avaliacao_risco is None


def protocolos_pendentes(ctx: Any, agent: Any) -> bool:
    """Etapa 2: risco calculado, protocolos ainda não selecionados."""
    return (
        ctx.context.avaliacao_risco is not None
        and ctx.context.resultado_protocolos is None
    )


def pronto_para_planejar(ctx: Any, agent: Any) -> bool:
    """Etapa 3 (e acompanhamento): risco e protocolos disponíveis."""
    return (
        ctx.context.avaliacao_risco is not None
        and ctx.context.resultado_protocolos is not None
    )
