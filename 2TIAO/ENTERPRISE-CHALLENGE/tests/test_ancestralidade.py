"""Testes de integração — endpoint de ancestralidade."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_obter_ancestralidade_status_ok():
    response = client.get("/api/ancestralidade/")
    assert response.status_code == 200


def test_obter_ancestralidade_estrutura():
    response = client.get("/api/ancestralidade/")
    body = response.json()

    assert "paciente_id" in body
    assert isinstance(body["composicao"], list)
    assert len(body["composicao"]) > 0
    assert body["observacao"]


def test_composicao_soma_proxima_de_cem_por_cento():
    response = client.get("/api/ancestralidade/")
    body = response.json()

    total = sum(item["percentual"] for item in body["composicao"])
    assert 99.0 <= total <= 100.5
