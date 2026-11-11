from fastapi.testclient import TestClient

from app import db
from app import main
from app.main import app


def login(client: TestClient, email: str, senha: str = "cardioia") -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "senha": senha})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_complete_telemetry_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "cardioia.db")
    monkeypatch.setattr(main, "DEVICE_KEY", "chave-de-teste")
    with TestClient(app) as client:
        medico = login(client, "medico@cardioia.com")
        assert client.get("/api/pacientes", headers=medico).status_code == 200
        unauthorized = client.post("/api/leituras", json={"paciente_id": "p-001", "temperatura": 38.5, "fc": 125, "spo2": 90})
        assert unauthorized.status_code == 401
        reading = client.post("/api/leituras", headers={"X-Device-Key": "chave-de-teste"}, json={"paciente_id": "p-001", "temperatura": 38.5, "fc": 125, "spo2": 90, "estado": "critico", "ts": "2026-11-09T12:00:00Z"})
        assert reading.status_code == 201
        assert reading.json()["reavaliado"] is True
        status = client.get("/api/pacientes/p-001/status", headers=medico)
        assert status.status_code == 200
        assert status.json()["avaliacao"]["origem"] == "sem_llm"
        assert status.json()["leituras"][-1]["estado"] == "critico"


def test_patient_cannot_access_another_patient(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "cardioia.db")
    with TestClient(app) as client:
        paciente = login(client, "paciente@cardioia.com")
        assert client.get("/api/pacientes/p-002/status", headers=paciente).status_code == 403
        assert client.post("/api/pacientes/p-001/avaliar", headers=paciente).status_code == 403


def test_chat_contract_works_without_external_provider(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "cardioia.db")
    with TestClient(app) as client:
        medico = login(client, "medico@cardioia.com")
        response = client.post("/api/chat", headers=medico, json={"mensagem": "Estou com cansaço", "paciente_id": "p-001", "sessao_id": None})
        assert response.status_code == 200
        assert response.json()["origem"] in {"watson", "openai", "fallback"}
        assert response.json()["sessao_id"]


def test_startup_seeds_history_and_assessment(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "cardioia.db")
    with TestClient(app) as client:
        medico = login(client, "medico@cardioia.com")
        pacientes = client.get("/api/pacientes", headers=medico).json()
        assert all(p["ultima_leitura"] and p["classificacao"] for p in pacientes)


def test_risk_goes_back_down_after_normal_readings(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DATABASE_PATH", tmp_path / "cardioia.db")
    monkeypatch.setattr(main, "DEVICE_KEY", "chave-de-teste")
    chave = {"X-Device-Key": "chave-de-teste"}
    with TestClient(app) as client:
        medico = login(client, "medico@cardioia.com")
        for _ in range(5):
            client.post("/api/leituras", headers=chave, json={"paciente_id": "p-001", "temperatura": 38.6, "fc": 130, "spo2": 89})
        pico = client.get("/api/pacientes/p-001/status", headers=medico).json()["avaliacao"]["avaliacao_risco"]
        for _ in range(5):
            client.post("/api/leituras", headers=chave, json={"paciente_id": "p-001", "temperatura": 36.6, "fc": 78, "spo2": 97})
        normal = client.get("/api/pacientes/p-001/status", headers=medico).json()["avaliacao"]["avaliacao_risco"]
        assert normal["probabilidade"] < pico["probabilidade"]
