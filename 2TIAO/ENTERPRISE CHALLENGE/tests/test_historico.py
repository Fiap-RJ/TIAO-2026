"""Testes de integração — endpoint e persistência de histórico."""

from fastapi.testclient import TestClient

from main import app
from services.history_store import salvar_interacao

client = TestClient(app)

PACIENTE_ID = "paciente-teste-historico"


def test_historico_vazio_por_padrao():
    response = client.get(f"/api/historico/{PACIENTE_ID}")
    assert response.status_code == 200
    assert response.json()["interacoes"] == []


def test_historico_retorna_interacoes_persistidas():
    salvar_interacao(
        paciente_id=PACIENTE_ID,
        pergunta="O que significa metabolismo lento de cafeína?",
        resposta="Resposta explicativa sobre o gene CYP1A2.",
        fontes=[
            {
                "painel": "Genera Nutri",
                "marcador": "Sensibilidade à Cafeína",
                "gene": "CYP1A2",
                "conclusao_curta": "Metabolismo lento de cafeína",
            }
        ],
    )

    response = client.get(f"/api/historico/{PACIENTE_ID}")
    body = response.json()

    assert body["paciente_id"] == PACIENTE_ID
    assert len(body["interacoes"]) == 1

    interacao = body["interacoes"][0]
    assert interacao["pergunta"] == "O que significa metabolismo lento de cafeína?"
    assert interacao["fontes"][0]["gene"] == "CYP1A2"
    assert interacao["criado_em"]


def test_historico_respeita_limite():
    for i in range(5):
        salvar_interacao(
            paciente_id="paciente-limite",
            pergunta=f"Pergunta {i}",
            resposta=f"Resposta {i}",
            fontes=[],
        )

    response = client.get("/api/historico/paciente-limite", params={"limite": 2})
    assert response.status_code == 200
    assert len(response.json()["interacoes"]) == 2


def test_historico_nao_mistura_pacientes():
    salvar_interacao("paciente-a", "Pergunta do paciente A", "Resposta A", [])
    salvar_interacao("paciente-b", "Pergunta do paciente B", "Resposta B", [])

    resposta_a = client.get("/api/historico/paciente-a").json()["interacoes"]
    assert all(i["paciente_id"] == "paciente-a" for i in resposta_a)
