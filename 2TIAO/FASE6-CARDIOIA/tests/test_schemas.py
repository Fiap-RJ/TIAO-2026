"""
Testes de ``domain.schemas``
============================

Cobre a validação de ``DadosPaciente`` (R6.1–R6.4, CA5): normalização de
chaves, colisão, campos extras/ausentes, faixas, NaN, tipos, booleanos e
coerções aceitas. Também confere que ``RecomendacaoFinal`` gera schema estrito.
"""

import math

import pytest
from pydantic import ValidationError

from domain.constantes import FEATURES
from domain.schemas import DadosPaciente, RecomendacaoFinal


def _erros(exc: ValidationError) -> str:
    """Texto único com loc + mensagem de cada erro, para asserts por substring."""
    return " | ".join(
        f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()
    )


def test_novo_caso_com_chave_com_espaco_e_valido(novo_caso_dict):
    assert "disponibilidade recursos" in novo_caso_dict
    paciente = DadosPaciente.model_validate(novo_caso_dict)
    assert paciente.disponibilidade_recursos == 25
    assert paciente.spo2_media == 89


def test_como_lista_ordenada_segue_features(novo_caso):
    valores = novo_caso.como_lista_ordenada()
    assert len(valores) == len(FEATURES)
    assert valores == [float(getattr(novo_caso, nome)) for nome in FEATURES]


@pytest.mark.parametrize("chave", [" FC_Media ", "fc-media", "FC MEDIA"])
def test_chaves_sao_normalizadas(novo_caso_dict, chave):
    dados = dict(novo_caso_dict)
    valor = dados.pop("fc_media")
    dados[chave] = valor
    assert DadosPaciente.model_validate(dados).fc_media == valor


def test_colisao_de_chaves_e_rejeitada(novo_caso_dict):
    dados = dict(novo_caso_dict)
    dados["disponibilidade_recursos"] = 30
    with pytest.raises(ValidationError) as exc:
        DadosPaciente.model_validate(dados)
    assert "colisão" in _erros(exc.value)


def test_campo_extra_e_rejeitado_com_nome(novo_caso_dict):
    with pytest.raises(ValidationError) as exc:
        DadosPaciente.model_validate({**novo_caso_dict, "peso": 80})
    assert "peso" in _erros(exc.value)


def test_campo_ausente_e_rejeitado(novo_caso_dict):
    dados = dict(novo_caso_dict)
    del dados["fc_media"]
    with pytest.raises(ValidationError) as exc:
        DadosPaciente.model_validate(dados)
    assert "fc_media" in _erros(exc.value)


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("spo2_media", 150),
        ("spo2_media", math.nan),
        ("spo2_media", math.inf),
        ("spo2_media", "abc"),
        ("eventos_24h", 5.5),
        ("fc_media", -1),
    ],
)
def test_valores_invalidos_sao_rejeitados(novo_caso_dict, campo, valor):
    with pytest.raises(ValidationError) as exc:
        DadosPaciente.model_validate({**novo_caso_dict, campo: valor})
    assert campo in _erros(exc.value)


@pytest.mark.parametrize(
    ("campo", "valor"), [("fc_media", True), ("eventos_24h", False)]
)
def test_booleanos_sao_rejeitados(novo_caso_dict, campo, valor):
    with pytest.raises(ValidationError) as exc:
        DadosPaciente.model_validate({**novo_caso_dict, campo: valor})
    texto = _erros(exc.value)
    assert campo in texto
    assert "booleano" in texto


def test_inteiro_aceita_float_sem_parte_fracionaria(novo_caso_dict):
    paciente = DadosPaciente.model_validate({**novo_caso_dict, "eventos_24h": 5.0})
    assert paciente.eventos_24h == 5
    assert isinstance(paciente.eventos_24h, int)


def test_string_numerica_e_aceita(novo_caso_dict):
    paciente = DadosPaciente.model_validate({**novo_caso_dict, "spo2_media": "92"})
    assert paciente.spo2_media == 92.0


def test_entrada_que_nao_e_objeto_e_rejeitada():
    with pytest.raises(ValidationError):
        DadosPaciente.model_validate([1, 2, 3])


def test_recomendacao_final_tem_schema_estrito():
    from agents import AgentOutputSchema

    assert AgentOutputSchema(RecomendacaoFinal).is_strict_json_schema()


def test_recomendacao_final_valida_padrao_de_ids():
    base = {
        "probabilidade_prevista": 0.9,
        "classificacao_risco": "ALTO",
        "acoes_operacionais": ["Abrir unidades temporárias"],
        "explicacao": "Texto.",
    }
    RecomendacaoFinal.model_validate({**base, "protocolos_sugeridos": ["P01", "P10"]})
    with pytest.raises(ValidationError):
        RecomendacaoFinal.model_validate({**base, "protocolos_sugeridos": ["P11"]})
    with pytest.raises(ValidationError):
        RecomendacaoFinal.model_validate({**base, "acoes_operacionais": []})
