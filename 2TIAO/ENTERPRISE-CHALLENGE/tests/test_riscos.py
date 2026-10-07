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


def test_obter_riscos_por_paciente_ecoa_id():
    response = client.get("/api/riscos/uuid-123")
    assert response.status_code == 200

    body = response.json()
    demo = client.get("/api/riscos/").json()
    assert body["paciente_id"] == "uuid-123"
    assert len(body["paineis"]) == len(demo["paineis"])
    assert len(body["escala_risco_genetico"]) == len(demo["escala_risco_genetico"])


def test_obter_riscos_rejeita_paciente_id_invalido():
    assert client.get("/api/riscos/id.invalido").status_code == 422
    assert client.get("/api/riscos/" + "a" * 65).status_code == 422


def test_obter_riscos_rejeita_path_traversal():
    assert client.get("/api/riscos/..%2F..").status_code == 422
