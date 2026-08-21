"""Testes de integração — endpoint de riscos."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_obter_riscos_status_ok():
    response = client.get("/api/riscos/")
    assert response.status_code == 200


def test_obter_riscos_estrutura():
    response = client.get("/api/riscos/")
    body = response.json()

    assert "paciente_id" in body
    assert isinstance(body["paineis"], list)
    assert len(body["paineis"]) > 0
    assert isinstance(body["escala_risco_genetico"], list)


def test_niveis_de_risco_sao_neutros():
    """Garante que o nível exposto nunca usa rótulos alarmistas."""
    response = client.get("/api/riscos/")
    body = response.json()

    niveis_validos = {"baixo", "moderado", "atencao"}
    for painel in body["paineis"]:
        for resultado in painel["resultados"]:
            assert resultado["nivel"] in niveis_validos

    for doenca in body["escala_risco_genetico"]:
        assert doenca["nivel"] in niveis_validos


def test_categoria_original_preservada():
    """A categoria textual original do laudo continua disponível para auditoria/rastreabilidade."""
    response = client.get("/api/riscos/")
    body = response.json()

    resultado = body["paineis"][0]["resultados"][0]
    assert resultado["categoria_original"]
