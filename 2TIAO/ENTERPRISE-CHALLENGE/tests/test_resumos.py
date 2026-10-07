"""Testes de integração — endpoint de resumos."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

PACIENTE_ID = "paciente-teste-resumos"


def test_resumo_relatorio_status_ok():
    response = client.get(f"/api/resumos/relatorio/{PACIENTE_ID}")
    assert response.status_code == 200


def test_resumo_relatorio_estrutura():
    response = client.get(f"/api/resumos/relatorio/{PACIENTE_ID}")
    body = response.json()

    assert body["paciente_id"] == PACIENTE_ID
    assert body["resumo"]
    assert body["gerado_em"]


def test_resumo_interacoes_sem_historico():
    response = client.get(f"/api/resumos/interacoes/{PACIENTE_ID}")
    assert response.status_code == 200

    body = response.json()
    assert body["quantidade_interacoes"] == 0
    assert "não fez" in body["resumo"].lower() or "nao fez" in body["resumo"].lower()


def test_resumos_rejeitam_paciente_id_invalido():
    assert client.get("/api/resumos/relatorio/id.invalido").status_code == 422
    assert client.get("/api/resumos/interacoes/id.invalido").status_code == 422
