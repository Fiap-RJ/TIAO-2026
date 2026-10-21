"""
Agente Analista de Risco — CardioIA Fase 6
==========================================

Chama ``calcular_risco_paciente`` (modelo de ML) exatamente uma vez e
transfere ao Especialista em Protocolos com uma ``NotaHandoff``.

Fluxo forçado por código: ``tool_choice="required"`` + ``reset_tool_choice=False``
e a tool desabilitada depois de executada deixam o handoff como única opção.
"""

from agents import Agent, Handoff

from agentes.instrucoes import montar_instrucoes, montar_model_settings
from agentes.tools import calcular_risco_paciente
from core.config import Settings

NOME = "Analista de Risco"
DESCRICAO_HANDOFF = "Calcula a probabilidade de pico de risco com o modelo de ML."

INSTRUCOES = """
Você é o Analista de Risco do CardioIA.
1. Chame a tool `calcular_risco_paciente` exatamente uma vez. Nunca estime o risco por conta própria.
2. Em seguida, transfira para o Especialista em Protocolos. No campo `resumo` da transferência,
   escreva em até 300 caracteres a probabilidade e a classificação devolvidas pela tool.
Não responda ao usuário diretamente.
"""


def criar_analista_risco(
    settings: Settings, handoffs: list[Handoff] | None = None
) -> Agent:
    """Fábrica do Analista; ``handoffs`` recebe o handoff para o Especialista."""
    return Agent(
        name=NOME,
        handoff_description=DESCRICAO_HANDOFF,
        instructions=montar_instrucoes(INSTRUCOES),
        model=settings.OPENAI_MODEL,
        model_settings=montar_model_settings(
            settings, tool_choice="required", parallel_tool_calls=False
        ),
        tools=[calcular_risco_paciente],
        handoffs=list(handoffs or []),
        reset_tool_choice=False,
    )
