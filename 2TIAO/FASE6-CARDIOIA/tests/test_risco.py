"""
Testes de ``services.risco``
============================

Fronteiras das faixas BAIXO/MODERADO/ALTO e do limiar de decisão 0,50.
"""

import math

import pytest

from domain.schemas import DadosPaciente
from services.risco import avaliar_risco, classificar_risco


@pytest.mark.parametrize(
    ("probabilidade", "esperado"),
    [
        (0.0, "BAIXO"),
        (0.3999, "BAIXO"),
        (0.40, "MODERADO"),
        (0.6999, "MODERADO"),
        (0.70, "ALTO"),
        (1.0, "ALTO"),
    ],
)
def test_faixas(probabilidade, esperado):
    assert classificar_risco(probabilidade) == esperado


@pytest.mark.parametrize("probabilidade", [-0.1, 1.1, math.nan])
def test_fora_de_intervalo(probabilidade):
    with pytest.raises(ValueError):
        classificar_risco(probabilidade)


@pytest.mark.parametrize(("probabilidade", "pico"), [(0.4999, False), (0.50, True)])
def test_pico_risco_previsto_no_limiar(criar_contexto_falso, probabilidade, pico):
    contexto = criar_contexto_falso(probabilidade)
    avaliacao = avaliar_risco(contexto.paciente, contexto.preditor)
    assert avaliacao.pico_risco_previsto is pico
    assert avaliacao.classificacao == "MODERADO"
    assert avaliacao.limiar_decisao == 0.5


def test_arredonda_quatro_casas_e_classifica_o_arredondado(criar_contexto_falso):
    contexto = criar_contexto_falso(0.699996)
    avaliacao = avaliar_risco(contexto.paciente, contexto.preditor)
    assert avaliacao.probabilidade == 0.7
    assert avaliacao.classificacao == "ALTO"


def test_aviso_de_extrapolacao(criar_contexto_falso, novo_caso_dict):
    contexto = criar_contexto_falso(0.9)
    contexto.preditor.faixas_treino = {
        "spo2_media": [83.4, 100.0],
        "fc_media": [50.0, 150.0],
    }
    paciente = DadosPaciente.model_validate({**novo_caso_dict, "spo2_media": 60})
    avaliacao = avaliar_risco(paciente, contexto.preditor)
    assert len(avaliacao.avisos) == 1
    assert "spo2_media" in avaliacao.avisos[0]


def test_avisos_de_versao_do_preditor_sao_repassados(contexto_falso):
    contexto_falso.preditor.avisos = ["Modelo treinado com scikit-learn 0.0.1"]
    avaliacao = avaliar_risco(contexto_falso.paciente, contexto_falso.preditor)
    assert avaliacao.avisos == ["Modelo treinado com scikit-learn 0.0.1"]
    assert avaliacao.modelo_versao == "stub-teste"


def test_novo_caso_com_modelo_real(contexto):
    avaliacao = avaliar_risco(contexto.paciente, contexto.preditor)
    assert avaliacao.probabilidade >= 0.70
    assert avaliacao.classificacao == "ALTO"
    assert avaliacao.avisos == []
