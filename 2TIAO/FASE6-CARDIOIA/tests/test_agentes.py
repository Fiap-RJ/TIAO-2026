"""
Testes dos agentes, tools e guardrails (sem LLM)
================================================

Construção dos quatro agentes (inclui a checagem de assinatura de
``on_handoff`` feita pelo SDK), callbacks de handoff, gating mutuamente
exclusivo, tools com pré-condições e guardrails chamados diretamente
(R9.1, R10.2, R11.1, R13.1–R13.3, CA10, CA13).
"""

import asyncio
import json
from types import SimpleNamespace

import pytest
from agents import AgentOutputSchema, RunContextWrapper
from agents.tool_context import ToolContext

import agentes.tools as tools
from agentes.analista_risco import criar_analista_risco
from agentes.especialista_protocolos import criar_especialista_protocolos
from agentes.guardrails import (
    extrair_ultima_mensagem_usuario,
    validar_entrada_atendimento,
    validar_recomendacao_final,
)
from agentes.orquestrador import (
    criar_orquestrador,
    pronto_para_planejar,
    protocolos_pendentes,
    risco_pendente,
)
from agentes.planejador_resposta import criar_planejador_resposta
from core.config import obter_settings
from core.erros import ErroFluxoAgentes
from domain.schemas import RecomendacaoFinal
from services.recomendacao import montar_recomendacao_deterministica

DESCRICOES = {
    "Orquestrador": "Ponto de entrada do atendimento; coordena as etapas e encaminha ao "
    "especialista adequado.",
    "Analista de Risco": "Calcula a probabilidade de pico de risco com o modelo de ML.",
    "Especialista em Protocolos": "Seleciona os protocolos aplicáveis na base simulada.",
    "Planejador de Resposta": "Consolida risco e protocolos em ações operacionais e responde "
    "perguntas de acompanhamento.",
}


@pytest.fixture
def settings(settings_limpas):
    return obter_settings()


def _wrapper(contexto) -> RunContextWrapper:
    return RunContextWrapper(context=contexto)


def _invocar_tool(tool, contexto) -> str:
    ctx = ToolContext(
        context=contexto, tool_name=tool.name, tool_call_id="teste", tool_arguments="{}"
    )
    return asyncio.run(tool.on_invoke_tool(ctx, "{}"))


def _cadeia(orquestrador):
    """Agentes alcançáveis a partir do Orquestrador, na ordem do fluxo.

    ``on_invoke_handoff`` devolve o agente de destino (API pública do SDK); um
    contexto descartável absorve os efeitos dos callbacks.
    """
    descartavel = _wrapper(
        SimpleNamespace(
            atendimento_id="descartavel", cadeia_agentes=[], notas_handoff=[]
        )
    )
    nota = json.dumps({"resumo": "descartável"})
    analista = asyncio.run(
        orquestrador.handoffs[0].on_invoke_handoff(descartavel, None)
    )
    especialista = asyncio.run(
        analista.handoffs[0].on_invoke_handoff(descartavel, nota)
    )
    planejador = asyncio.run(
        especialista.handoffs[0].on_invoke_handoff(descartavel, nota)
    )
    return [orquestrador, analista, especialista, planejador]


# --- construção -------------------------------------------------------------------
def test_quatro_agentes_com_nomes_e_descricoes(settings):
    agentes = _cadeia(criar_orquestrador(settings))
    assert {a.name: a.handoff_description for a in agentes} == DESCRICOES
    assert all(a.model == "gpt-4.1-mini" for a in agentes)


def test_fabricas_individuais_constroem(settings):
    for agente in (
        criar_analista_risco(settings),
        criar_especialista_protocolos(settings),
        criar_planejador_resposta(settings),
    ):
        assert agente.name in DESCRICOES
        assert "Escopo: o CardioIA" in agente.instructions


def test_model_settings_forcam_o_fluxo(settings):
    orquestrador, analista, especialista, planejador = _cadeia(
        criar_orquestrador(settings)
    )
    for agente in (orquestrador, analista, especialista):
        assert agente.model_settings.tool_choice == "required"
        assert agente.model_settings.parallel_tool_calls is False
        assert agente.reset_tool_choice is False
    assert planejador.model_settings.tool_choice == "required"
    assert planejador.reset_tool_choice is True
    assert orquestrador.model_settings.temperature == 0.0


def test_temperatura_vazia_e_omitida(settings_limpas):
    settings_limpas.setenv("OPENAI_TEMPERATURE", "")
    planejador = criar_planejador_resposta(obter_settings())
    assert planejador.model_settings.temperature is None


def test_planejador_tem_saida_estruturada_e_guardrail(settings):
    planejador = criar_planejador_resposta(settings)
    assert planejador.output_type is RecomendacaoFinal
    assert planejador.output_guardrails == [validar_recomendacao_final]
    assert AgentOutputSchema(RecomendacaoFinal).is_strict_json_schema()
    assert (
        "Nunca use as palavras prescrição, prescrever, dose, dosagem ou posologia"
        in (planejador.instructions)
    )


def test_orquestrador_tem_guardrail_de_entrada_bloqueante(settings):
    orquestrador = criar_orquestrador(settings)
    assert orquestrador.input_guardrails == [validar_entrada_atendimento]
    assert validar_entrada_atendimento.run_in_parallel is False
    assert [h.agent_name for h in orquestrador.handoffs] == [
        "Analista de Risco",
        "Especialista em Protocolos",
        "Planejador de Resposta",
    ]


# --- callbacks de handoff -----------------------------------------------------------
def test_callbacks_registram_cadeia_e_notas(settings, contexto_falso):
    orquestrador, analista, especialista, _ = _cadeia(criar_orquestrador(settings))
    ctx = _wrapper(contexto_falso)

    destino = asyncio.run(orquestrador.handoffs[0].on_invoke_handoff(ctx, None))
    assert destino.name == "Analista de Risco"
    asyncio.run(
        analista.handoffs[0].on_invoke_handoff(ctx, json.dumps({"resumo": "p=0,99"}))
    )
    asyncio.run(
        especialista.handoffs[0].on_invoke_handoff(ctx, json.dumps({"resumo": "P02"}))
    )

    assert contexto_falso.cadeia_agentes == [
        "Orquestrador",
        "Analista de Risco",
        "Especialista em Protocolos",
        "Planejador de Resposta",
    ]
    assert [n.resumo for n in contexto_falso.notas_handoff] == ["p=0,99", "P02"]


# --- gating -------------------------------------------------------------------------
def test_predicados_mutuamente_exclusivos(contexto_falso):
    ctx = _wrapper(contexto_falso)
    predicados = (risco_pendente, protocolos_pendentes, pronto_para_planejar)

    def estado():
        return [p(ctx, None) for p in predicados]

    assert estado() == [True, False, False]
    _invocar_tool(tools.calcular_risco_paciente, contexto_falso)
    assert estado() == [False, True, False]
    _invocar_tool(tools.consultar_protocolos_aplicaveis, contexto_falso)
    assert estado() == [False, False, True]


def test_tools_sem_parametros_do_llm():
    for tool in (
        tools.calcular_risco_paciente,
        tools.consultar_protocolos_aplicaveis,
        tools.obter_resumo_atendimento,
        tools.listar_base_protocolos,
    ):
        assert tool.params_json_schema.get("properties") == {}
        assert tool.description


def test_tools_preenchem_o_contexto_e_respeitam_a_ordem(contexto_falso):
    with pytest.raises(ErroFluxoAgentes):
        _invocar_tool(tools.consultar_protocolos_aplicaveis, contexto_falso)
    with pytest.raises(ErroFluxoAgentes):
        _invocar_tool(tools.obter_resumo_atendimento, contexto_falso)

    risco = json.loads(_invocar_tool(tools.calcular_risco_paciente, contexto_falso))
    assert risco["classificacao"] == "ALTO"
    with pytest.raises(ErroFluxoAgentes):
        _invocar_tool(tools.calcular_risco_paciente, contexto_falso)

    protocolos = json.loads(
        _invocar_tool(tools.consultar_protocolos_aplicaveis, contexto_falso)
    )
    assert [p["id"] for p in protocolos["protocolos"]] == ["P02", "P05", "P08", "P10"]

    resumo = json.loads(_invocar_tool(tools.obter_resumo_atendimento, contexto_falso))
    assert resumo["avaliacao_risco"]["probabilidade"] == 0.99
    assert (
        len(json.loads(_invocar_tool(tools.listar_base_protocolos, contexto_falso)))
        == 10
    )


def test_is_enabled_das_tools(contexto_falso):
    ctx = _wrapper(contexto_falso)
    assert tools.calcular_risco_paciente.is_enabled(ctx, None) is True
    assert tools.consultar_protocolos_aplicaveis.is_enabled(ctx, None) is False
    _invocar_tool(tools.calcular_risco_paciente, contexto_falso)
    assert tools.calcular_risco_paciente.is_enabled(ctx, None) is False
    assert tools.consultar_protocolos_aplicaveis.is_enabled(ctx, None) is True


# --- guardrail de entrada -------------------------------------------------------------
def _entrada(contexto, mensagem):
    resultado = asyncio.run(
        validar_entrada_atendimento.guardrail_function(
            _wrapper(contexto), None, mensagem
        )
    )
    return resultado.tripwire_triggered, resultado.output_info["motivo"]


@pytest.mark.parametrize(
    "mensagem",
    [
        "qual dose de medicamento devo aplicar?",
        "Qual a prescrição?",
        "",
        "   ",
        "x" * 2001,
    ],
)
def test_guardrail_de_entrada_bloqueia(contexto_falso, mensagem):
    disparou, motivo = _entrada(contexto_falso, mensagem)
    assert disparou is True
    assert motivo


def test_guardrail_de_entrada_aceita_pergunta_legitima(contexto_falso):
    assert _entrada(
        contexto_falso, "por que o protocolo de SpO2 não foi acionado?"
    ) == (
        False,
        None,
    )
    assert _entrada(contexto_falso, "x" * 2000)[0] is False


def test_guardrail_de_entrada_aceita_lista_de_itens(contexto_falso):
    historico = [
        {"role": "user", "content": "Novo atendimento"},
        {"role": "assistant", "content": "ok"},
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "qual dose aplicar?"}],
        },
    ]
    assert _entrada(contexto_falso, historico)[0] is True
    historico[-1] = {
        "role": "user",
        "content": "por que o protocolo de SpO2 não foi acionado?",
    }
    assert _entrada(contexto_falso, historico)[0] is False
    assert (
        extrair_ultima_mensagem_usuario([{"role": "assistant", "content": "x"}]) == ""
    )


def test_guardrail_de_entrada_sem_paciente(contexto_falso):
    contexto_falso.paciente = None
    assert _entrada(contexto_falso, "Novo atendimento")[0] is True


# --- guardrail de saída ---------------------------------------------------------------
def _saida(contexto, recomendacao):
    resultado = asyncio.run(
        validar_recomendacao_final.guardrail_function(
            _wrapper(contexto), None, recomendacao
        )
    )
    return resultado.tripwire_triggered, resultado.output_info["violacoes"]


def _preparar(contexto):
    _invocar_tool(tools.calcular_risco_paciente, contexto)
    _invocar_tool(tools.consultar_protocolos_aplicaveis, contexto)
    return montar_recomendacao_deterministica(
        contexto.avaliacao_risco, contexto.resultado_protocolos
    )


def test_guardrail_de_saida_aceita_recomendacao_correta(contexto_falso):
    assert _saida(contexto_falso, _preparar(contexto_falso)) == (False, [])


def test_guardrail_de_saida_dispara_na_recomendacao_adulterada(contexto_falso):
    adulterada = _preparar(contexto_falso).model_copy(
        update={
            "protocolos_sugeridos": ["P01", "P02", "P05"],
            "probabilidade_prevista": 0.91,
        }
    )
    disparou, violacoes = _saida(contexto_falso, adulterada)
    assert disparou is True
    assert {v[:2] for v in violacoes} == {"V1", "V3"}


def test_guardrail_de_saida_com_contexto_incompleto(contexto_falso):
    rec = RecomendacaoFinal(
        probabilidade_prevista=0.99,
        classificacao_risco="ALTO",
        protocolos_sugeridos=["P02"],
        acoes_operacionais=["Abrir unidades temporárias"],
        explicacao="Texto.",
    )
    assert _saida(contexto_falso, rec)[0] is True
