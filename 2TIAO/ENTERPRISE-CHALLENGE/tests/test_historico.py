"""Testes de integração — endpoint e persistência de histórico."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from main import app
from services import history_store
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


def test_delete_historico_remove_interacoes():
    salvar_interacao("paciente-delete", "Pergunta 1", "Resposta 1", [])
    salvar_interacao("paciente-delete", "Pergunta 2", "Resposta 2", [])

    response = client.delete("/api/historico/paciente-delete")
    assert response.status_code == 204

    depois = client.get("/api/historico/paciente-delete")
    assert depois.status_code == 200
    assert depois.json()["interacoes"] == []


def test_delete_historico_inexistente_404():
    response = client.delete("/api/historico/paciente-nunca-visto")
    assert response.status_code == 404


def test_retencao_remove_so_antigas():
    paciente = "paciente-retencao"
    antiga = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
    with history_store._conectar() as conn:
        conn.execute(
            "INSERT INTO interacoes (paciente_id, pergunta, resposta, fontes, criado_em) "
            "VALUES (?, ?, ?, ?, ?)",
            (paciente, "Pergunta antiga", "Resposta antiga", "[]", antiga),
        )
    salvar_interacao(paciente, "Pergunta recente", "Resposta recente", [])

    removidas = history_store.aplicar_regra_retencao(30)

    assert removidas >= 1
    restantes = history_store.listar_historico(paciente)
    assert [r["pergunta"] for r in restantes] == ["Pergunta recente"]


def test_historico_rejeita_paciente_id_invalido():
    assert client.get("/api/historico/id.invalido").status_code == 422
    assert client.delete("/api/historico/id.invalido").status_code == 422
