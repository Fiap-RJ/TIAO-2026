"""Testes unitários — limite de palavras do modo resumido."""

import pytest

from services.formatacao import limitar_corpo, limitar_palavras

_FRASE = "Esta frase de exemplo tem exatamente dez palavras no total."  # 10 palavras


def _texto(n_frases: int) -> str:
    return " ".join([_FRASE] * n_frases)


def test_texto_longo_e_cortado_no_fim_de_frase():
    texto = _texto(20)  # 200 palavras
    resultado = limitar_palavras(texto, 120)

    assert len(resultado.split()) <= 150
    assert len(resultado.split()) <= 120
    assert resultado.endswith(".")


def test_texto_curto_fica_intacto():
    texto = _texto(13)  # 130 palavras <= 120 * 1.25
    assert limitar_palavras(texto, 120) == texto


def test_texto_sem_pontuacao_recebe_reticencias():
    texto = " ".join(["palavra"] * 200)
    resultado = limitar_palavras(texto, 120)

    assert len(resultado.split()) <= 120
    assert resultado.endswith("…")


def test_quebras_de_linha_sao_preservadas():
    texto = "\n".join([_FRASE] * 20)
    resultado = limitar_palavras(texto, 120)

    assert "\n" in resultado
    assert resultado.endswith(".")


def test_limite_invalido():
    with pytest.raises(ValueError):
        limitar_palavras("texto", 0)


_FECHAMENTO = (
    "⚠️ Importante: Este assistente é informativo e não substitui consulta médica. "
    "A genética indica tendências, não certezas.\n\n"
    "Você quer que eu explique com mais detalhes?"
)


def test_limitar_corpo_preserva_disclaimer_e_pergunta_final():
    texto = f"{_texto(20)}\n\n{_FECHAMENTO}"  # corpo de 200 palavras + fechamento
    resultado = limitar_corpo(texto, 120)

    corpo = resultado.split("⚠️")[0]
    assert len(corpo.split()) <= 120
    assert resultado.endswith(_FECHAMENTO)
    assert "não certezas." in resultado


def test_limitar_corpo_nao_conta_o_fechamento():
    texto = f"{_texto(13)}\n\n{_FECHAMENTO}"  # 130 + fechamento > 150 no total
    assert limitar_corpo(texto, 120) == texto


def test_limitar_corpo_preserva_pergunta_sem_disclaimer():
    texto = f"{_texto(20)}\n\nVocê quer que eu explique com mais detalhes?"
    resultado = limitar_corpo(texto, 120)

    assert resultado.endswith("Você quer que eu explique com mais detalhes?")
    assert len(resultado.split()) <= 120 + 8


def test_limitar_corpo_sem_fechamento_equivale_a_limitar_palavras():
    texto = _texto(20)
    assert limitar_corpo(texto, 120) == limitar_palavras(texto, 120)
