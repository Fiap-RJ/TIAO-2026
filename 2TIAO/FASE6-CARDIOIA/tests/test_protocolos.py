"""
Testes de ``services.protocolos``
=================================

Comparação estrita nos limiares de P01–P09, P10 ⇔ ALTO, resultado do
``novo_caso`` e fidelidade dos textos ao enunciado.
"""

import pytest

from domain.schemas import DadosPaciente
from services.protocolos import BASE_PROTOCOLOS, listar_base, selecionar_protocolos

# Paciente "neutro": nenhum gatilho de protocolo nem regra do alvo verdadeira.
NEUTRO = {
    "idade_media": 50,
    "carga_sistema": 50,
    "tempo_espera": 30,
    "fc_media": 80,
    "spo2_media": 97,
    "pa_sistolica": 120,
    "temperatura": 24,
    "densidade_eventos": 2,
    "eventos_24h": 1,
    "disponibilidade_recursos": 80,
}

TEXTOS_ENUNCIADO = [
    "Se SPO2 < 88% → iniciar suporte respiratório imediato",
    "Se carga do sistema > 85% → abrir unidades temporárias",
    "Se FC > 120 → iniciar monitoramento intensivo",
    "Se eventos_24h > 5 → ativar equipe de resposta rápida",
    "Se disponibilidade_recursos < 30% → redistribuir insumos",
    "Se tempo_espera > 90 min → priorizar triagem emergencial",
    "Se temperatura > 38°C média → iniciar protocolo infeccioso",
    "Se densidade_eventos > 6 → ativar plano de contingência",
    "Se PA sistólica < 90 → iniciar protocolo de choque",
    "Se risco sistêmico alto → ativar estado de emergência",
]

INTEIROS = {"densidade_eventos", "eventos_24h"}


def _ids(dados: dict, classificacao: str = "BAIXO") -> list[str]:
    resultado = selecionar_protocolos(
        DadosPaciente.model_validate(dados), classificacao
    )
    return [p.id for p in resultado.protocolos]


def test_paciente_neutro_nao_aciona_nada():
    resultado = selecionar_protocolos(DadosPaciente.model_validate(NEUTRO), "BAIXO")
    assert resultado.protocolos == []
    assert resultado.sinais_de_atencao == []


@pytest.mark.parametrize("protocolo", BASE_PROTOCOLOS[:9], ids=lambda p: p.id)
def test_limiar_estrito(protocolo):
    passo = 1 if protocolo.variavel in INTEIROS else 0.01
    alem = (
        protocolo.limiar + passo
        if protocolo.operador == ">"
        else protocolo.limiar - passo
    )
    assert protocolo.id not in _ids({**NEUTRO, protocolo.variavel: protocolo.limiar})
    assert _ids({**NEUTRO, protocolo.variavel: alem}) == [protocolo.id]


@pytest.mark.parametrize(
    ("classificacao", "aciona"), [("BAIXO", False), ("MODERADO", False), ("ALTO", True)]
)
def test_p10_se_e_somente_se_alto(classificacao, aciona):
    assert ("P10" in _ids(NEUTRO, classificacao)) is aciona


def test_novo_caso(novo_caso):
    resultado = selecionar_protocolos(novo_caso, "ALTO")
    assert [p.id for p in resultado.protocolos] == ["P02", "P05", "P08", "P10"]
    assert [s.variavel for s in resultado.sinais_de_atencao] == [
        "tempo_espera",
        "fc_media",
        "spo2_media",
        "eventos_24h",
    ]
    spo2 = resultado.sinais_de_atencao[2]
    assert (
        spo2.valor,
        spo2.limiar_risco,
        spo2.limiar_protocolo,
        spo2.protocolo_id,
    ) == (
        89,
        92,
        88,
        "P01",
    )
    assert resultado.protocolos[0].justificativa == "carga_sistema=92 > 85"


def test_sinal_some_quando_protocolo_aciona(novo_caso_dict):
    # SpO2 87 aciona P01 e deixa de ser sinal de atenção.
    resultado = selecionar_protocolos(
        DadosPaciente.model_validate({**novo_caso_dict, "spo2_media": 87}), "ALTO"
    )
    assert "P01" in [p.id for p in resultado.protocolos]
    assert "spo2_media" not in [s.variavel for s in resultado.sinais_de_atencao]


def test_base_tem_dez_itens_com_texto_literal():
    assert [p.id for p in BASE_PROTOCOLOS] == [f"P{i:02d}" for i in range(1, 11)]
    assert [p.texto for p in BASE_PROTOCOLOS] == TEXTOS_ENUNCIADO


def test_listar_base_devolve_copias():
    base = listar_base()
    base[0].texto = "alterado"
    assert BASE_PROTOCOLOS[0].texto == TEXTOS_ENUNCIADO[0]
