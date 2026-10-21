"""
Agente Orquestrador e montagem da cadeia — CardioIA Fase 6
==========================================================

``criar_orquestrador(settings)`` monta a cadeia completa:

    Orquestrador → Analista de Risco → Especialista em Protocolos → Planejador de Resposta

Gating por código: os três predicados (``risco_pendente``,
``protocolos_pendentes`` e ``pronto_para_planejar``, definidos em
``agentes/contexto.py`` e reexportados aqui) são mutuamente
exclusivos, então em cada etapa existe exatamente um handoff habilitado para o
Orquestrador. Em perguntas de acompanhamento (risco e protocolos já no
contexto), só o handoff Orquestrador → Planejador fica disponível.

Callbacks de handoff: o ``handoff()`` do SDK exige exatamente 1 parâmetro
(``ctx``) sem ``input_type`` e 2 (``ctx, nota``) com ``input_type``; caso
contrário levanta ``UserError`` na construção. Por isso o destino é ligado por
closures de fábrica (``functools.partial`` geraria 3 parâmetros).
"""

import logging
from collections.abc import Callable

from agents import Agent, RunContextWrapper, handoff

from agentes import analista_risco, especialista_protocolos, planejador_resposta
from agentes.contexto import (
    ContextoAtendimento,
    pronto_para_planejar,
    protocolos_pendentes,
    risco_pendente,
)
from agentes.guardrails import validar_entrada_atendimento
from agentes.instrucoes import montar_instrucoes, montar_model_settings
from core.config import Settings, obter_settings
from domain.schemas import NotaHandoff

logger = logging.getLogger("cardioia.agentes.orquestrador")

NOME = "Orquestrador"
DESCRICAO_HANDOFF = "Ponto de entrada do atendimento; coordena as etapas e encaminha ao especialista adequado."

INSTRUCOES = """
Você é o Orquestrador do CardioIA. Você não calcula nem opina: apenas coordena o atendimento.
Transfira sempre para o único agente disponível na etapa atual:
- novo atendimento: Analista de Risco (que encaminha ao Especialista em Protocolos e este ao
  Planejador de Resposta);
- pergunta de acompanhamento, com risco e protocolos já calculados: Planejador de Resposta.
Não responda ao usuário diretamente.
"""

Ctx = RunContextWrapper[ContextoAtendimento]

# Predicados de gating (definidos em contexto.py, compartilhados com as tools):
# risco_pendente, protocolos_pendentes e pronto_para_planejar.
__all__ = [
    "criar_orquestrador",
    "pronto_para_planejar",
    "protocolos_pendentes",
    "risco_pendente",
]


# --- callbacks de handoff ---------------------------------------------------------
def _criar_registro_handoff(destino: str) -> Callable[[Ctx], None]:
    """Callback para handoff sem input_type (Orquestrador → especialista)."""

    def registrar_handoff(ctx: Ctx) -> None:
        ctx.context.cadeia_agentes.append(destino)
        logger.info(
            "handoff -> %s | atendimento=%s", destino, ctx.context.atendimento_id
        )

    return registrar_handoff


def _criar_registro_nota(destino: str) -> Callable[[Ctx, NotaHandoff], None]:
    """Callback para handoff com input_type=NotaHandoff (Analista → Especialista → Planejador)."""

    def registrar_nota(ctx: Ctx, nota: NotaHandoff) -> None:
        ctx.context.cadeia_agentes.append(destino)
        ctx.context.notas_handoff.append(nota)
        logger.info(
            "handoff -> %s | atendimento=%s", destino, ctx.context.atendimento_id
        )

    return registrar_nota


def criar_orquestrador(settings: Settings | None = None) -> Agent:
    """Monta os quatro agentes e devolve o Orquestrador (agente inicial do ``Runner``)."""
    settings = settings or obter_settings()

    planejador = planejador_resposta.criar_planejador_resposta(settings)
    especialista = especialista_protocolos.criar_especialista_protocolos(
        settings,
        handoffs=[
            handoff(
                planejador,
                input_type=NotaHandoff,
                on_handoff=_criar_registro_nota(planejador.name),
                is_enabled=pronto_para_planejar,
            )
        ],
    )
    analista = analista_risco.criar_analista_risco(
        settings,
        handoffs=[
            handoff(
                especialista,
                input_type=NotaHandoff,
                on_handoff=_criar_registro_nota(especialista.name),
                is_enabled=protocolos_pendentes,
            )
        ],
    )

    return Agent(
        name=NOME,
        handoff_description=DESCRICAO_HANDOFF,
        instructions=montar_instrucoes(INSTRUCOES),
        model=settings.OPENAI_MODEL,
        model_settings=montar_model_settings(
            settings, tool_choice="required", parallel_tool_calls=False
        ),
        handoffs=[
            handoff(
                analista,
                on_handoff=_criar_registro_handoff(analista.name),
                is_enabled=risco_pendente,
            ),
            handoff(
                especialista,
                on_handoff=_criar_registro_handoff(especialista.name),
                is_enabled=protocolos_pendentes,
            ),
            handoff(
                planejador,
                on_handoff=_criar_registro_handoff(planejador.name),
                is_enabled=pronto_para_planejar,
            ),
        ],
        input_guardrails=[validar_entrada_atendimento],
        reset_tool_choice=False,
    )
