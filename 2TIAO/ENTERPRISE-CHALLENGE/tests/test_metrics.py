"""Testes de integração — endpoint de métricas do pipeline."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_metrics_expoe_as_quatro_chaves():
    response = client.get("/metrics/")
    assert response.status_code == 200

    body = response.json()
    assert set(body) >= {
        "total_requisicoes",
        "latencia_media_ms",
        "taxa_bloqueio_guardrail_percentual",
        "ultimas_violacoes",
    }
    assert isinstance(body["total_requisicoes"], int)
    assert isinstance(body["latencia_media_ms"], (int, float))
    assert isinstance(body["taxa_bloqueio_guardrail_percentual"], (int, float))
    assert isinstance(body["ultimas_violacoes"], list)
