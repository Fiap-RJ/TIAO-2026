"""Testes do nó `generate` — max_tokens e limite de palavras por modo (LLM falso)."""

import importlib

import pytest
from langchain_core.messages import AIMessage

from agents.state import AgentState
from core.config import settings

# `agents.nodes` reexporta a função `generate`; importa o módulo explicitamente.
generate_module = importlib.import_module("agents.nodes.generate")

_TEXTO_LONGO = " ".join(["Esta frase de exemplo tem exatamente dez palavras no total."] * 20)


class _LLMFake:
    def __init__(self):
        self.mensagens = None

    def invoke(self, mensagens):
        self.mensagens = mensagens
        return AIMessage(content=_TEXTO_LONGO)


@pytest.fixture
def chamadas(monkeypatch):
    registro: list[dict] = []
    llm = _LLMFake()

    def _fake_build_llm(**kwargs):
        registro.append(kwargs)
        return llm

    monkeypatch.setattr(generate_module, "build_llm", _fake_build_llm)
    return registro, llm


def test_resumido_limita_tokens_e_palavras(chamadas):
    registro, llm = chamadas
    resultado = generate_module.generate(AgentState(question="q", detail_level="resumido"))

    assert registro[-1]["max_tokens"] == settings.CHAT_MAX_TOKENS_RESUMIDO
    assert len(resultado["answer"].split()) <= 150
    assert "Você quer que eu explique com mais detalhes?" in llm.mensagens[0].content


def test_resumido_preserva_disclaimer_e_pergunta_final(chamadas, monkeypatch):
    _, llm = chamadas
    fechamento = (
        "⚠️ Importante: Este assistente é informativo e não substitui consulta médica. "
        "A genética indica tendências, não certezas.\n\n"
        "Você quer que eu explique com mais detalhes?"
    )
    monkeypatch.setattr(
        llm, "invoke", lambda mensagens: AIMessage(content=f"{_TEXTO_LONGO}\n\n{fechamento}")
    )

    resultado = generate_module.generate(AgentState(question="q", detail_level="resumido"))

    assert resultado["answer"].endswith(fechamento)
    assert len(resultado["answer"].split("⚠️")[0].split()) <= settings.CHAT_MAX_PALAVRAS_RESUMIDO


def test_detalhado_usa_mais_tokens_e_nao_corta(chamadas):
    registro, llm = chamadas
    resultado = generate_module.generate(AgentState(question="q", detail_level="detalhado"))

    assert registro[-1]["max_tokens"] == settings.CHAT_MAX_TOKENS_DETALHADO
    assert resultado["answer"] == _TEXTO_LONGO
    assert "NÃO termine com a pergunta" in llm.mensagens[0].content


def test_modo_desconhecido_cai_no_resumido(chamadas):
    registro, _ = chamadas
    generate_module.generate(AgentState(question="q", detail_level="outro"))
    assert registro[-1]["max_tokens"] == settings.CHAT_MAX_TOKENS_RESUMIDO
