"""Testes de contrato — POST /api/chat/ sem LLM (agente substituído por um fake)."""

import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from main import app

client = TestClient(app)

_DOC = Document(
    page_content="x",
    metadata={
        "painel": "Genera Nutri",
        "caracteristica": "Cafeína",
        "gene": "CYP1A2",
        "conclusao_curta": "Metabolismo lento",
    },
)


class _AgenteFake:
    def __init__(self, contexto=None, erro=None, **extra):
        self.contexto = [_DOC] if contexto is None else contexto
        self.erro = erro
        self.extra = extra
        self.chamadas: list[dict] = []

    def invoke(self, entrada: dict) -> dict:
        self.chamadas.append(entrada)
        if self.erro:
            raise self.erro
        return {
            "question": entrada["question"],
            "answer": "Texto. Consulte um médico geneticista.",
            "context": self.contexto,
            **self.extra,
        }


@pytest.fixture
def agente(monkeypatch):
    def _instalar(**kwargs) -> _AgenteFake:
        fake = _AgenteFake(**kwargs)
        monkeypatch.setattr("api.routes.chat.agent_app", fake)
        return fake

    return _instalar


def _perguntar(paciente_id="paciente-chat", **extra):
    return client.post(
        "/api/chat/", json={"paciente_id": paciente_id, "mensagem": "cafeína?", **extra}
    )


def test_contrato_basico(agente):
    agente()
    response = _perguntar()

    assert response.status_code == 200
    body = response.json()
    assert body["resposta"]
    assert body["fontes"][0]["gene"] == "CYP1A2"
    assert body["painel_utilizado"] == "Genera Nutri"
    assert body["guardrails_acionados"] == []


def test_contexto_vazio_usa_painel_geral(agente):
    agente(contexto=[])
    assert _perguntar().json()["painel_utilizado"] == "Geral"


def test_interacao_vai_para_o_historico(agente):
    agente()
    _perguntar(paciente_id="paciente-chat-historico")

    interacoes = client.get("/api/historico/paciente-chat-historico").json()["interacoes"]
    assert len(interacoes) == 1
    assert interacoes[0]["fontes"][0]["gene"] == "CYP1A2"


def test_erro_no_pipeline_retorna_500_generico_e_nao_salva(agente):
    agente(erro=RuntimeError("segredo-interno"))
    response = _perguntar(paciente_id="paciente-chat-erro")

    assert response.status_code == 500
    assert "segredo-interno" not in response.json()["detail"]
    assert "request_id=" in response.json()["detail"]
    assert client.get("/api/historico/paciente-chat-erro").json()["interacoes"] == []


def test_metricas_contam_a_requisicao(agente):
    agente()
    antes = client.get("/metrics/").json()["total_requisicoes"]
    _perguntar()
    assert client.get("/metrics/").json()["total_requisicoes"] == antes + 1


def test_bloqueio_propaga_para_resposta_e_metricas(agente):
    violacoes = ["[DIAGNÓSTICO] Termo proibido detectado: 'seu diagnóstico é'"]
    agente(violacoes=violacoes, bloqueado=True)

    body = _perguntar().json()

    assert body["guardrails_acionados"] == violacoes
    metricas = client.get("/metrics/").json()
    assert metricas["taxa_bloqueio_guardrail_percentual"] > 0
    assert violacoes[0] in metricas["ultimas_violacoes"]


def test_nivel_detalhe_default_resumido(agente):
    fake = agente()
    _perguntar()
    assert fake.chamadas[-1]["detail_level"] == "resumido"


def test_nivel_detalhe_detalhado(agente):
    fake = agente()
    assert _perguntar(nivel_detalhe="detalhado").status_code == 200
    assert fake.chamadas[-1]["detail_level"] == "detalhado"


def test_nivel_detalhe_invalido_422(agente):
    fake = agente()
    assert _perguntar(nivel_detalhe="medio").status_code == 422
    assert fake.chamadas == []


def test_paciente_id_invalido_422(agente):
    fake = agente()
    assert _perguntar(paciente_id="a b").status_code == 422
    assert fake.chamadas == []
