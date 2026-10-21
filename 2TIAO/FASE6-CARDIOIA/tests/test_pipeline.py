"""
Testes do pipeline com ``Runner.run`` mockado (sem rede)
========================================================

Mapeamento de exceções → fallback/erro, inicialização idempotente do SDK,
cadeia de agentes por turno e modo ``sem_llm`` (R10.4, R13.4, R15.1–R15.3,
CA11, CA12 parte). Os casos de ``UserError`` encadeado reproduzem o embrulho
real do SDK para exceções levantadas dentro de tools.
"""

import asyncio
import json
from unittest.mock import AsyncMock

import openai
import pytest
from agents import (
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    MaxTurnsExceeded,
    ModelBehaviorError,
    OutputGuardrailTripwireTriggered,
    UserError,
)
from agents.guardrail import InputGuardrailResult, OutputGuardrailResult

import pipeline
from agentes.guardrails import validar_entrada_atendimento, validar_recomendacao_final
from core.erros import (
    ConfiguracaoError,
    EntradaBloqueadaError,
    ErroFluxoAgentes,
    ModeloIndisponivelError,
)
from domain.schemas import RecomendacaoFinal
from services.protocolos import selecionar_protocolos
from services.recomendacao import montar_recomendacao_deterministica
from services.risco import avaliar_risco

IDS_NOVO_CASO = ["P02", "P05", "P08", "P10"]


class ResultadoFalso:
    """Imita ``RunResult.final_output_as`` (mesma checagem de tipo do SDK)."""

    def __init__(self, final_output):
        self.final_output = final_output

    def final_output_as(self, cls, raise_if_incorrect_type=False):
        if raise_if_incorrect_type and not isinstance(self.final_output, cls):
            raise TypeError(f"Final output is not of type {cls.__name__}")
        return self.final_output


@pytest.fixture
def chave_falsa(settings_limpas, monkeypatch):
    """Chave fictícia + ``set_default_openai_key`` interceptado (sem tocar no SDK global)."""
    settings_limpas.setenv("OPENAI_API_KEY", "chave-falsa-de-teste")
    chamadas = []
    monkeypatch.setattr(
        pipeline,
        "set_default_openai_key",
        lambda chave, use_for_tracing: chamadas.append(1),
    )
    return chamadas


def _mock_runner(monkeypatch, **kwargs) -> AsyncMock:
    mock = AsyncMock(**kwargs)
    monkeypatch.setattr(pipeline.Runner, "run", mock)
    return mock


def _executar(contexto, **kwargs):
    return asyncio.run(
        pipeline.executar_atendimento(contexto.paciente, contexto=contexto, **kwargs)
    )


def _recomendacao_llm(contexto) -> RecomendacaoFinal:
    rec = montar_recomendacao_deterministica(
        contexto.avaliacao_risco, contexto.resultado_protocolos
    )
    return rec.model_copy(
        update={
            "acoes_operacionais": ["Ação redigida pelo LLM"],
            "explicacao": "Texto do LLM.",
        }
    )


def _assert_fallback(resposta, motivo):
    assert resposta.origem == "fallback_deterministico"
    assert resposta.motivo_fallback == motivo
    assert resposta.avaliacao_risco.probabilidade == 0.99
    assert resposta.avaliacao_risco.classificacao == "ALTO"
    assert [p.id for p in resposta.protocolos] == IDS_NOVO_CASO
    assert 1 <= len(resposta.acoes_operacionais) <= 8
    assert resposta.aviso_legal.startswith("Aviso: o CardioIA")


# --- fallback ---------------------------------------------------------------------
@pytest.mark.parametrize(
    ("excecao", "motivo"),
    [
        (MaxTurnsExceeded("limite"), "MaxTurnsExceeded"),
        (ModelBehaviorError("json inválido"), "ModelBehaviorError"),
        # A requisição HTTP é irrelevante aqui; None evita depender do cliente HTTP interno.
        (openai.APIConnectionError(request=None), "APIConnectionError"),
        (openai.APITimeoutError(request=None), "APITimeoutError"),
    ],
)
def test_falhas_recuperaveis_viram_fallback(
    chave_falsa, monkeypatch, contexto_falso, excecao, motivo
):
    _mock_runner(monkeypatch, side_effect=excecao)
    _assert_fallback(_executar(contexto_falso), motivo)


def test_guardrail_de_saida_vira_fallback_com_violacoes(
    chave_falsa, monkeypatch, contexto_falso
):
    resultado = OutputGuardrailResult(
        guardrail=validar_recomendacao_final,
        agent_output=None,
        agent=None,
        output=GuardrailFunctionOutput(
            output_info={"violacoes": ["V3 protocolos divergentes"]},
            tripwire_triggered=True,
        ),
    )
    _mock_runner(monkeypatch, side_effect=OutputGuardrailTripwireTriggered(resultado))
    resposta = _executar(contexto_falso)
    _assert_fallback(resposta, "guardrail_saida")
    assert resposta.violacoes_guardrail == ["V3 protocolos divergentes"]


def test_execucao_terminada_fora_do_planejador_vira_fallback(
    chave_falsa, monkeypatch, contexto_falso
):
    _mock_runner(monkeypatch, return_value=ResultadoFalso("texto livre"))
    _assert_fallback(_executar(contexto_falso), "TypeError")


def test_guardrail_de_entrada_vira_entrada_bloqueada(
    chave_falsa, monkeypatch, contexto_falso
):
    resultado = InputGuardrailResult(
        guardrail=validar_entrada_atendimento,
        output=GuardrailFunctionOutput(
            output_info={"motivo": "pedido de dose"}, tripwire_triggered=True
        ),
    )
    _mock_runner(monkeypatch, side_effect=InputGuardrailTripwireTriggered(resultado))
    with pytest.raises(EntradaBloqueadaError) as exc:
        _executar(contexto_falso, pergunta="qual dose?")
    assert exc.value.motivo == "pedido de dose"


# --- UserError encadeado (embrulho real do SDK) -------------------------------------
def _user_error_de(causa: Exception) -> UserError:
    try:
        try:
            raise causa
        except Exception as interna:
            raise UserError(f"Error running tool x: {interna}") from interna
    except UserError as externa:
        return externa


def test_user_error_de_fluxo_vira_fallback(chave_falsa, monkeypatch, contexto_falso):
    _mock_runner(
        monkeypatch, side_effect=_user_error_de(ErroFluxoAgentes("fora de ordem"))
    )
    _assert_fallback(_executar(contexto_falso), "fluxo_fora_de_ordem")


def test_user_error_de_modelo_e_desembrulhado(chave_falsa, monkeypatch, contexto_falso):
    _mock_runner(
        monkeypatch, side_effect=_user_error_de(ModeloIndisponivelError("sem modelo"))
    )
    with pytest.raises(ModeloIndisponivelError, match="sem modelo"):
        _executar(contexto_falso)


def test_user_error_sem_causa_e_relancado(chave_falsa, monkeypatch, contexto_falso):
    _mock_runner(
        monkeypatch, side_effect=UserError("on_handoff must take one argument")
    )
    with pytest.raises(UserError):
        _executar(contexto_falso)


# --- configuração e SDK ---------------------------------------------------------------
def test_sem_chave_levanta_antes_de_inicializar(
    settings_limpas, monkeypatch, contexto_falso
):
    chamadas = []
    monkeypatch.setattr(
        pipeline, "set_default_openai_key", lambda *a, **k: chamadas.append(1)
    )
    mock = _mock_runner(monkeypatch)
    with pytest.raises(ConfiguracaoError, match="src/.env"):
        _executar(contexto_falso)
    assert chamadas == []
    mock.assert_not_called()


def test_inicializar_sdk_uma_unica_vez(chave_falsa, monkeypatch, contexto_falso):
    def resposta_valida(*args, context, **kwargs):
        pipeline._completar_contexto(context)
        return ResultadoFalso(_recomendacao_llm(context))

    _mock_runner(monkeypatch, side_effect=resposta_valida)
    _executar(contexto_falso)
    _executar(contexto_falso)
    assert chave_falsa == [1]


def test_argumentos_do_runner(chave_falsa, monkeypatch, contexto_falso):
    def resposta_valida(agente, *, context, **kwargs):
        pipeline._completar_contexto(context)
        return ResultadoFalso(_recomendacao_llm(context))

    mock = _mock_runner(monkeypatch, side_effect=resposta_valida)
    sessao = object()
    resposta = _executar(contexto_falso, sessao=sessao)

    agente = mock.call_args.args[0]
    kwargs = mock.call_args.kwargs
    assert agente.name == "Orquestrador"
    assert kwargs["context"] is contexto_falso
    assert kwargs["session"] is sessao
    assert kwargs["max_turns"] == 12
    assert kwargs["run_config"].workflow_name == "CardioIA-Fase6"
    assert kwargs["run_config"].group_id == contexto_falso.atendimento_id
    assert kwargs["run_config"].tracing_disabled is True
    assert contexto_falso.atendimento_id in kwargs["input"]
    assert (
        json.dumps(contexto_falso.paciente.model_dump(), ensure_ascii=False)
        in kwargs["input"]
    )

    # Valores exibidos vêm do contexto; ações e explicação vêm do LLM.
    assert resposta.origem == "agentes"
    assert resposta.motivo_fallback is None
    assert resposta.acoes_operacionais == ["Ação redigida pelo LLM"]
    assert [p.id for p in resposta.protocolos] == IDS_NOVO_CASO


# --- cadeia por turno -------------------------------------------------------------------
def test_cadeia_reiniciada_por_turno(chave_falsa, monkeypatch, contexto_falso):
    """O mock aciona os handoffs reais do Orquestrador, como o SDK faria."""
    nota = json.dumps({"resumo": "nota"})

    async def simular_sdk(orquestrador, *, input, context, **kwargs):
        from agents import RunContextWrapper

        ctx = RunContextWrapper(context=context)
        if context.avaliacao_risco is None:  # turno 1: fluxo completo
            analista = await orquestrador.handoffs[0].on_invoke_handoff(ctx, None)
            context.avaliacao_risco = avaliar_risco(context.paciente, context.preditor)
            especialista = await analista.handoffs[0].on_invoke_handoff(ctx, nota)
            context.resultado_protocolos = selecionar_protocolos(
                context.paciente, context.avaliacao_risco.classificacao
            )
            await especialista.handoffs[0].on_invoke_handoff(ctx, nota)
        else:  # acompanhamento: só o Planejador está habilitado
            await orquestrador.handoffs[2].on_invoke_handoff(ctx, None)
        return ResultadoFalso(_recomendacao_llm(context))

    monkeypatch.setattr(pipeline.Runner, "run", simular_sdk)
    primeira = _executar(contexto_falso)
    segunda = _executar(
        contexto_falso, pergunta="por que o protocolo de SpO2 não foi acionado?"
    )

    assert primeira.cadeia_agentes == [
        "Orquestrador",
        "Analista de Risco",
        "Especialista em Protocolos",
        "Planejador de Resposta",
    ]
    assert segunda.cadeia_agentes == ["Orquestrador", "Planejador de Resposta"]
    assert len(contexto_falso.notas_handoff) == 2
    assert (
        contexto_falso.preditor.chamadas == 1
    )  # risco não é recalculado no acompanhamento


# --- sem LLM ------------------------------------------------------------------------------
def test_sem_llm_nao_chama_o_runner(settings_limpas, monkeypatch, contexto_falso):
    mock = _mock_runner(monkeypatch)
    resposta = _executar(contexto_falso, usar_llm=False)
    mock.assert_not_called()
    assert resposta.origem == "sem_llm"
    assert resposta.cadeia_agentes == ["Orquestrador"]
    assert [p.id for p in resposta.protocolos] == IDS_NOVO_CASO


def test_versao_sync_reaproveita_o_event_loop(chave_falsa, monkeypatch, novo_caso):
    """Os turnos do modo interativo rodam no mesmo loop: o cliente HTTP global do SDK
    fica preso ao loop em que abriu as conexões ("Event loop is closed" com loop novo)."""
    loops = []

    async def resposta_valida(*args, context, **kwargs):
        loops.append(asyncio.get_running_loop())
        pipeline._completar_contexto(context)
        return ResultadoFalso(_recomendacao_llm(context))

    monkeypatch.setattr(pipeline.Runner, "run", resposta_valida)
    pipeline.executar_atendimento_sync(novo_caso)
    pipeline.executar_atendimento_sync(novo_caso)
    assert len(loops) == 2
    assert loops[0] is loops[1]
    assert not loops[0].is_closed()


def test_sem_llm_com_preditor_real(settings_limpas, novo_caso):
    resposta = pipeline.executar_atendimento_sync(novo_caso, usar_llm=False)
    assert resposta.origem == "sem_llm"
    assert resposta.avaliacao_risco.probabilidade >= 0.70
    assert [p.id for p in resposta.protocolos] == IDS_NOVO_CASO
