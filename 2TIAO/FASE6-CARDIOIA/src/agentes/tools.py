"""
Tools dos agentes — CardioIA Fase 6
===================================

Wrappers finos sobre ``services``, expostos ao LLM com ``@function_tool``.

Invariantes:

- nenhuma tool recebe parâmetros do LLM: os números de entrada do modelo
  vêm do contexto local (``ctx.context``), então o LLM não pode alterá-los;
- ``failure_error_function=None``: uma exceção interrompe a execução em vez de
  virar texto para o LLM. O SDK a relança como ``UserError(...) from exc``, e o
  pipeline desembrulha a causa (``ErroFluxoAgentes`` → fallback;
  ``ModeloIndisponivelError`` → exit 2);
- ``is_enabled`` esconde a tool depois de executada: junto com
  ``tool_choice="required"``, isso força a ordem do fluxo por código.

As docstrings (pt-BR) são a descrição que o LLM vê.
"""

import json
import logging

from agents import RunContextWrapper, function_tool

from agentes.contexto import ContextoAtendimento, protocolos_pendentes, risco_pendente
from core.erros import ErroFluxoAgentes
from services.protocolos import listar_base, selecionar_protocolos
from services.risco import avaliar_risco

logger = logging.getLogger("cardioia.agentes.tools")

Ctx = RunContextWrapper[ContextoAtendimento]


@function_tool(failure_error_function=None, is_enabled=risco_pendente)
def calcular_risco_paciente(ctx: Ctx) -> str:
    """Calcula a probabilidade de pico de risco do paciente do atendimento com o modelo de ML.

    Usa os dados já validados do contexto (não recebe parâmetros) e devolve a
    probabilidade, a classificação (BAIXO, MODERADO ou ALTO), se há pico previsto
    e avisos. Deve ser chamada uma única vez por atendimento.
    """
    contexto = ctx.context
    if contexto.avaliacao_risco is not None:
        raise ErroFluxoAgentes(
            "calcular_risco_paciente chamada com o risco já calculado"
        )
    contexto.avaliacao_risco = avaliar_risco(contexto.paciente, contexto.preditor)
    logger.info(
        "tool calcular_risco_paciente | atendimento=%s | p=%.4f %s",
        contexto.atendimento_id,
        contexto.avaliacao_risco.probabilidade,
        contexto.avaliacao_risco.classificacao,
    )
    return contexto.avaliacao_risco.model_dump_json()


@function_tool(failure_error_function=None, is_enabled=protocolos_pendentes)
def consultar_protocolos_aplicaveis(ctx: Ctx) -> str:
    """Seleciona, na base simulada P01–P10, os protocolos acionados para o paciente.

    Usa os dados do paciente e a classificação de risco já calculada (não recebe
    parâmetros). Devolve os protocolos acionados, com a justificativa de cada um,
    e os sinais de atenção (variáveis acima do limiar de risco, mas abaixo do
    gatilho do protocolo).
    """
    contexto = ctx.context
    if contexto.avaliacao_risco is None or contexto.resultado_protocolos is not None:
        raise ErroFluxoAgentes(
            "consultar_protocolos_aplicaveis exige risco calculado e protocolos pendentes"
        )
    contexto.resultado_protocolos = selecionar_protocolos(
        contexto.paciente, contexto.avaliacao_risco.classificacao
    )
    logger.info(
        "tool consultar_protocolos_aplicaveis | atendimento=%s | protocolos=%s",
        contexto.atendimento_id,
        [p.id for p in contexto.resultado_protocolos.protocolos],
    )
    return contexto.resultado_protocolos.model_dump_json()


@function_tool(failure_error_function=None)
def obter_resumo_atendimento(ctx: Ctx) -> str:
    """Devolve o resumo do atendimento: dados do paciente, avaliação de risco, protocolos
    acionados, sinais de atenção e notas dos agentes anteriores.

    Só leitura. Use exatamente estes valores na recomendação final.
    """
    contexto = ctx.context
    if contexto.avaliacao_risco is None or contexto.resultado_protocolos is None:
        raise ErroFluxoAgentes(
            "obter_resumo_atendimento chamada antes de risco e protocolos"
        )
    resumo = {
        "atendimento_id": contexto.atendimento_id,
        "paciente": contexto.paciente.model_dump(),
        "avaliacao_risco": contexto.avaliacao_risco.model_dump(),
        "protocolos_acionados": [
            p.model_dump() for p in contexto.resultado_protocolos.protocolos
        ],
        "sinais_de_atencao": [
            s.model_dump() for s in contexto.resultado_protocolos.sinais_de_atencao
        ],
        "notas_handoff": [n.resumo for n in contexto.notas_handoff],
    }
    logger.info(
        "tool obter_resumo_atendimento | atendimento=%s", contexto.atendimento_id
    )
    return json.dumps(resumo, ensure_ascii=False)


@function_tool(failure_error_function=None)
def listar_base_protocolos(ctx: Ctx) -> str:
    """Lista a base simulada completa de protocolos (P01–P10), com variável, operador e
    limiar de cada um. Só leitura; útil para explicar por que um protocolo não foi acionado.
    """
    logger.info(
        "tool listar_base_protocolos | atendimento=%s", ctx.context.atendimento_id
    )
    return json.dumps([p.model_dump() for p in listar_base()], ensure_ascii=False)
