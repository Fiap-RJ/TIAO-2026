"""
Agente Especialista em Protocolos — CardioIA Fase 6
===================================================

Chama ``consultar_protocolos_aplicaveis`` (seleção determinística na base
P01–P10) e transfere ao Planejador de Resposta com uma ``NotaHandoff``.
Nunca acrescenta protocolos fora do retorno da tool.
"""

from agents import Agent, Handoff

from agentes.instrucoes import montar_instrucoes, montar_model_settings
from agentes.tools import consultar_protocolos_aplicaveis
from core.config import Settings

NOME = "Especialista em Protocolos"
DESCRICAO_HANDOFF = "Seleciona os protocolos aplicáveis na base simulada."

INSTRUCOES = """
Você é o Especialista em Protocolos do CardioIA.
1. Chame a tool `consultar_protocolos_aplicaveis` exatamente uma vez. Nunca acrescente nem
   remova protocolos: valem somente os que a tool devolver.
2. Em seguida, transfira para o Planejador de Resposta. No campo `resumo` da transferência,
   escreva em até 300 caracteres os IDs dos protocolos acionados e os sinais de atenção.
Não responda ao usuário diretamente.
"""


def criar_especialista_protocolos(
    settings: Settings, handoffs: list[Handoff] | None = None
) -> Agent:
    """Fábrica do Especialista; ``handoffs`` recebe o handoff para o Planejador."""
    return Agent(
        name=NOME,
        handoff_description=DESCRICAO_HANDOFF,
        instructions=montar_instrucoes(INSTRUCOES),
        model=settings.OPENAI_MODEL,
        model_settings=montar_model_settings(
            settings, tool_choice="required", parallel_tool_calls=False
        ),
        tools=[consultar_protocolos_aplicaveis],
        handoffs=list(handoffs or []),
        reset_tool_choice=False,
    )
