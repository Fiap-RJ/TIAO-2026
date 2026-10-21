"""
Integração com o LLM real (``pytest -m llm``)
=============================================

Faz chamadas reais à OpenAI; é pulado sem ``OPENAI_API_KEY`` (ambiente ou
``src/.env``). Confere o fluxo completo de handoffs, a igualdade dos valores
com o modo ``--sem-llm`` e o turno de acompanhamento na mesma sessão.
"""

import pytest
from agents import SQLiteSession

import pipeline
from agentes.contexto import ContextoAtendimento
from core.config import obter_settings
from ml.preditor import obter_preditor

pytestmark = pytest.mark.llm

CADEIA_COMPLETA = [
    "Orquestrador",
    "Analista de Risco",
    "Especialista em Protocolos",
    "Planejador de Resposta",
]


def _limpar() -> None:
    obter_settings.cache_clear()
    obter_preditor.cache_clear()
    pipeline._reiniciar_sdk_para_testes()


@pytest.fixture
def settings_reais():
    """Configuração real (inclui ``src/.env``); pula se não houver chave."""
    _limpar()
    settings = obter_settings()
    if not settings.openai_configurado:
        pytest.skip(
            "OPENAI_API_KEY ausente: configure src/.env para rodar pytest -m llm"
        )
    yield settings
    _limpar()


def test_fluxo_completo_com_llm(settings_reais, novo_caso):
    sem_llm = pipeline.executar_atendimento_sync(novo_caso, usar_llm=False)
    resposta = pipeline.executar_atendimento_sync(novo_caso)

    assert resposta.origem == "agentes", resposta.motivo_fallback
    assert resposta.cadeia_agentes == CADEIA_COMPLETA
    assert {p.id for p in resposta.protocolos} == {"P02", "P05", "P08", "P10"}
    assert (
        resposta.avaliacao_risco.probabilidade == sem_llm.avaliacao_risco.probabilidade
    )
    assert (
        resposta.avaliacao_risco.classificacao == sem_llm.avaliacao_risco.classificacao
    )


def test_acompanhamento_na_mesma_sessao(settings_reais, novo_caso, tmp_path):
    contexto = ContextoAtendimento(
        atendimento_id="teste-llm-acompanhamento",
        paciente=novo_caso,
        preditor=obter_preditor(),
    )
    sessao = SQLiteSession(contexto.atendimento_id, tmp_path / "sessoes.db")

    primeira = pipeline.executar_atendimento_sync(
        novo_caso, contexto=contexto, sessao=sessao
    )
    assert primeira.origem == "agentes", primeira.motivo_fallback

    segunda = pipeline.executar_atendimento_sync(
        novo_caso,
        pergunta="por que o protocolo de SpO2 não foi acionado?",
        contexto=contexto,
        sessao=sessao,
    )
    assert segunda.origem == "agentes", segunda.motivo_fallback
    assert segunda.cadeia_agentes == ["Orquestrador", "Planejador de Resposta"]
    assert "88" in segunda.explicacao
    assert "89" in segunda.explicacao
