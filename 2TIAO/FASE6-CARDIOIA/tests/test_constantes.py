"""
Testes de ``domain.constantes``
===============================

Regexes de termos prescritivos usadas pelo guardrail de entrada
(``PEDIDOS_PRESCRICAO``) e pela verificação V5 da saída
(``TERMOS_PRESCRITIVOS``) — R13.3, CA13 — e coerência básica das constantes.
"""

import pytest

from domain.constantes import (
    AVISO_LEGAL,
    FAIXA_ALTO,
    FAIXA_MODERADO,
    FEATURES,
    LIMIAR_DECISAO,
    PEDIDOS_PRESCRICAO,
    REGRAS_ALVO,
    TERMOS_PRESCRITIVOS,
)


@pytest.mark.parametrize(
    "texto",
    [
        "Qual a prescrição?",
        "PRESCREVA algo",
        "qual dose de medicamento devo aplicar?",
        "Dosagens?",
        "posologia",
        "qual remédio usar?",
        "Posso tomar dipirona?",
    ],
)
def test_pedidos_prescricao_casam(texto):
    assert PEDIDOS_PRESCRICAO.search(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "por que o protocolo de SpO2 não foi acionado?",
        "Qual a probabilidade de pico de risco?",
        "Explique os sinais de atenção.",
    ],
)
def test_perguntas_legitimas_nao_casam(texto):
    assert not PEDIDOS_PRESCRICAO.search(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "conforme prescrição",
        "administrar 5 mg",
        "não prescrevemos",
        "aplicar 2,5 ml",
        "ajustar a dose",
    ],
)
def test_termos_prescritivos_casam(texto):
    # Rigidez intencional: até a negação ("não prescrevemos") é violação.
    assert TERMOS_PRESCRITIVOS.search(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "Abrir unidades temporárias e redistribuir insumos.",
        "Acompanhar spo2_media (valor 89; protocolo P01 aciona em < 88).",
        "Carga do sistema em 92% acima de 85%.",
    ],
)
def test_textos_operacionais_nao_casam(texto):
    assert not TERMOS_PRESCRITIVOS.search(texto)


def test_textos_da_base_de_protocolos_nao_casam():
    from services.protocolos import BASE_PROTOCOLOS

    for protocolo in BASE_PROTOCOLOS:
        assert not TERMOS_PRESCRITIVOS.search(protocolo.texto), protocolo.id


def test_template_deterministico_nao_casa(novo_caso):
    from domain.schemas import AvaliacaoRisco
    from services.protocolos import selecionar_protocolos
    from services.recomendacao import montar_recomendacao_deterministica

    avaliacao = AvaliacaoRisco(
        probabilidade=0.99,
        classificacao="ALTO",
        pico_risco_previsto=True,
        modelo_versao="t",
    )
    rec = montar_recomendacao_deterministica(
        avaliacao, selecionar_protocolos(novo_caso, "ALTO")
    )
    for texto in [*rec.acoes_operacionais, rec.explicacao]:
        assert not TERMOS_PRESCRITIVOS.search(texto), texto


def test_constantes_coerentes():
    assert len(FEATURES) == 10
    assert len(set(FEATURES)) == 10
    assert set(REGRAS_ALVO) <= set(FEATURES)
    assert 0 < FAIXA_MODERADO < LIMIAR_DECISAO < FAIXA_ALTO < 1
    # O aviso legal contém "prescreve"; por isso V5 nunca é aplicada a ele.
    assert TERMOS_PRESCRITIVOS.search(AVISO_LEGAL)
