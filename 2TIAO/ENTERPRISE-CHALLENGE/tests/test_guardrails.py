"""Testes unitários — guardrails de comunicação responsável."""

from services.guardrails import validar_resposta


def test_resposta_neutra_recebe_disclaimer_padrao():
    resultado = validar_resposta("O painel indica metabolismo lento da cafeína.")

    assert resultado.aprovado
    assert resultado.disclaimer_adicionado
    assert "não substitui uma consulta médica" in resultado.resposta_final


def test_resposta_com_disclaimer_existente_nao_duplica():
    original = (
        "O painel indica metabolismo lento da cafeína. Consulte um médico geneticista "
        "para mais detalhes."
    )
    resultado = validar_resposta(original)

    assert resultado.aprovado
    assert not resultado.disclaimer_adicionado
    assert resultado.resposta_final == original


def test_bloqueia_diagnostico():
    resultado = validar_resposta("Você foi diagnosticado com essa condição.")

    assert not resultado.aprovado
    assert any("[DIAGNÓSTICO]" in v for v in resultado.violacoes)


def test_bloqueia_prescricao():
    resultado = validar_resposta("Recomendo que tome esse medicamento imediatamente.")

    assert not resultado.aprovado
    assert any("[PRESCRIÇÃO]" in v for v in resultado.violacoes)


def test_bloqueia_pii_na_resposta():
    resultado = validar_resposta("Seu CPF é 123.456.789-00, conforme cadastro.")

    assert not resultado.aprovado
    assert any("[PII]" in v for v in resultado.violacoes)


def test_deteccao_ampliada_de_tom_alarmista():
    """Termos como 'grave'/'perigoso' (citados na governança) devem ser detectados, sem bloquear."""
    resultado = validar_resposta("Essa é uma condição grave e muito perigosa para sua saúde.")

    assert resultado.aprovado  # tom alarmista não bloqueia, apenas é sinalizado
    assert any("[ALARMISMO]" in v for v in resultado.violacoes)


def test_disclaimer_de_risco_poligenico_e_adicionado():
    resposta = (
        "Sua escala de risco genético mostra risco aumentado para essa condição. "
        "Consulte um médico geneticista."
    )
    resultado = validar_resposta(resposta)

    assert resultado.aprovado
    assert "Risco Poligênico" in resultado.resposta_final


def test_disclaimer_de_risco_poligenico_nao_duplica():
    resposta = (
        "Sua escala de risco genético mostra risco aumentado. Consulte um médico geneticista. "
        "⚠️ **Nota sobre Risco Poligênico:** já incluída manualmente aqui."
    )
    resultado = validar_resposta(resposta)

    assert resultado.resposta_final.count("Risco Poligênico") == 1
