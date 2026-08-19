"""
Teste de integração ponta a ponta — chat -> guardrail -> histórico.

Requer o índice FAISS gerado (`make seed`) e uma credencial de LLM válida
(GOOGLE_API_KEY ou OPENAI_API_KEY em .env), pois exercita o pipeline real
do agente. É pulado automaticamente quando esses pré-requisitos não estão
disponíveis (ex.: ambiente de CI sem segredos configurados).
"""

import pytest
from fastapi.testclient import TestClient

from core.config import settings
from main import app
from services.report_data import BACKEND_DIR

_FAISS_INDEX_DISPONIVEL = (BACKEND_DIR / "faiss_index").exists()
_CREDENCIAL_DISPONIVEL = bool(settings.GOOGLE_API_KEY or settings.OPENAI_API_KEY)

pytestmark = pytest.mark.skipif(
    not (_FAISS_INDEX_DISPONIVEL and _CREDENCIAL_DISPONIVEL),
    reason="Requer índice FAISS (`make seed`) e credencial de LLM configurada (.env).",
)

client = TestClient(app)


def test_fluxo_completo_chat_persiste_e_aparece_no_historico():
    paciente_id = "paciente-e2e"

    resposta_chat = client.post(
        "/api/chat/",
        json={
            "paciente_id": paciente_id,
            "mensagem": "O que meu painel Nutri diz sobre sensibilidade à cafeína?",
        },
    )
    assert resposta_chat.status_code == 200
    corpo_chat = resposta_chat.json()
    assert corpo_chat["resposta"]

    resposta_historico = client.get(f"/api/historico/{paciente_id}")
    interacoes = resposta_historico.json()["interacoes"]
    assert len(interacoes) >= 1
    assert interacoes[-1]["resposta"] == corpo_chat["resposta"]
