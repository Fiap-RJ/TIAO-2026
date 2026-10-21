"""
Testes de ``services.recomendacao``
===================================

Verificações V1–V5 da saída do LLM e recomendação determinística
(R13.2, R13.4, CA10, CA13).
"""

import pytest

from domain.schemas import AvaliacaoRisco, RecomendacaoFinal
from services.protocolos import selecionar_protocolos
from services.recomendacao import (
    ACAO_SEM_PROTOCOLOS,
    montar_recomendacao_deterministica,
    verificar_recomendacao,
)

AVALIACAO = AvaliacaoRisco(
    probabilidade=0.99,
    classificacao="ALTO",
    pico_risco_previsto=True,
    modelo_versao="rf-v1",
)


@pytest.fixture
def resultado(novo_caso):
    return selecionar_protocolos(novo_caso, "ALTO")


def _rec(**alteracoes) -> RecomendacaoFinal:
    base = {
        "probabilidade_prevista": 0.99,
        "classificacao_risco": "ALTO",
        "protocolos_sugeridos": ["P02", "P05", "P08", "P10"],
        "acoes_operacionais": ["Abrir unidades temporárias", "Redistribuir insumos"],
        "explicacao": "Risco alto (0,99); SpO2 89 não atinge o gatilho de P01 (< 88).",
    }
    return RecomendacaoFinal.model_validate({**base, **alteracoes})


def test_saida_correta_sem_violacoes(resultado):
    assert verificar_recomendacao(_rec(), AVALIACAO, resultado) == []


def test_tolerancia_de_probabilidade(resultado):
    assert (
        verificar_recomendacao(
            _rec(probabilidade_prevista=0.9904), AVALIACAO, resultado
        )
        == []
    )


@pytest.mark.parametrize(
    ("alteracoes", "codigo", "trecho"),
    [
        ({"probabilidade_prevista": 0.91}, "V1", "0.91"),
        ({"classificacao_risco": "MODERADO"}, "V2", "MODERADO"),
        ({"protocolos_sugeridos": ["P02", "P05", "P08"]}, "V3", "faltantes ['P10']"),
        (
            {"protocolos_sugeridos": ["P01", "P02", "P05", "P08", "P10"]},
            "V3",
            "extras ['P01']",
        ),
        ({"protocolos_sugeridos": ["P02", "P02", "P05", "P08", "P10"]}, "V4", "P02"),
        ({"acoes_operacionais": ["administrar 5 mg"]}, "V5", "acoes_operacionais[0]"),
        ({"explicacao": "Seguir conforme prescrição."}, "V5", "explicacao"),
    ],
)
def test_violacoes_especificas(resultado, alteracoes, codigo, trecho):
    violacoes = verificar_recomendacao(_rec(**alteracoes), AVALIACAO, resultado)
    assert len(violacoes) == 1
    assert violacoes[0].startswith(codigo)
    assert trecho in violacoes[0]


def test_contexto_incompleto_e_violacao():
    violacoes = verificar_recomendacao(_rec(), None, None)
    assert violacoes and "contexto incompleto" in violacoes[0]


def test_deterministica_do_novo_caso(resultado):
    rec = montar_recomendacao_deterministica(AVALIACAO, resultado)
    assert 1 <= len(rec.acoes_operacionais) <= 8
    assert rec.acoes_operacionais[:4] == [
        "Abrir unidades temporárias",
        "Redistribuir insumos",
        "Ativar plano de contingência",
        "Ativar estado de emergência",
    ]
    assert "Acompanhar spo2_media (valor 89; protocolo P01 aciona em < 88)" in (
        rec.acoes_operacionais
    )
    assert rec.protocolos_sugeridos == ["P02", "P05", "P08", "P10"]
    assert verificar_recomendacao(rec, AVALIACAO, resultado) == []


def test_deterministica_sem_protocolos(novo_caso_dict):
    from domain.schemas import DadosPaciente

    neutro = {**novo_caso_dict}
    neutro.update(
        carga_sistema=50,
        tempo_espera=30,
        fc_media=80,
        spo2_media=97,
        densidade_eventos=2,
        eventos_24h=1,
        **{"disponibilidade recursos": 80},
    )
    resultado = selecionar_protocolos(DadosPaciente.model_validate(neutro), "BAIXO")
    avaliacao = AVALIACAO.model_copy(
        update={
            "probabilidade": 0.05,
            "classificacao": "BAIXO",
            "pico_risco_previsto": False,
        }
    )
    rec = montar_recomendacao_deterministica(avaliacao, resultado)
    assert rec.acoes_operacionais == [ACAO_SEM_PROTOCOLOS]
    assert rec.protocolos_sugeridos == []
    assert verificar_recomendacao(rec, avaliacao, resultado) == []
