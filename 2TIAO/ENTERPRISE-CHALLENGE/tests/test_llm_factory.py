"""Testes unitários — factory de providers (sem rede, sem chave real)."""

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI

from core.config import settings
from core.llm import (
    ConfiguracaoLLMInvalida,
    ModeloRef,
    build_embeddings,
    build_judge_llm,
    build_llm,
    juiz_ativo,
    modelo_ativo,
)
from services.vector_store import indice_slug


@pytest.fixture(autouse=True)
def _config_padrao(monkeypatch):
    """Parte sempre dos defaults do código, independentemente do `.env` local."""
    monkeypatch.setattr(settings, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "LLM_MODEL", "")
    monkeypatch.setattr(settings, "EMBEDDINGS_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "EMBEDDINGS_MODEL", "")
    monkeypatch.setattr(settings, "JUDGE_PROVIDER", None)
    monkeypatch.setattr(settings, "JUDGE_MODEL", "")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.1-flash-lite")
    monkeypatch.setattr(settings, "GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "")
    monkeypatch.setattr(settings, "OPENAI_EMBEDDING_MODEL", "")
    monkeypatch.setattr(settings, "GOOGLE_API_KEY", "fake-google")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-fake")


def test_parse_valido():
    assert ModeloRef.parse("openai:modelo-x") == ModeloRef("openai", "modelo-x")


def test_parse_divide_so_no_primeiro_dois_pontos():
    assert ModeloRef.parse("gemini:models/x:y") == ModeloRef("gemini", "models/x:y")


@pytest.mark.parametrize("texto", ["semdoispontos", "anthropic:x", "openai:"])
def test_parse_invalido(texto):
    with pytest.raises(ConfiguracaoLLMInvalida):
        ModeloRef.parse(texto)


def test_build_llm_openai_com_ref():
    llm = build_llm(ModeloRef("openai", "modelo-x"), max_tokens=10)

    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "modelo-x"
    assert llm.max_tokens == 10


def test_build_llm_default_e_gemini():
    llm = build_llm()

    assert isinstance(llm, ChatGoogleGenerativeAI)
    assert llm.model.endswith(settings.GEMINI_MODEL)


def test_build_llm_gemini_usa_max_output_tokens():
    llm = build_llm(max_tokens=123)
    assert llm.max_output_tokens == 123


def test_openai_sem_modelo_falha_cedo(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")

    with pytest.raises(ConfiguracaoLLMInvalida, match="LLM_MODEL"):
        build_llm()


def test_openai_sem_chave_falha_cedo(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")

    with pytest.raises(ConfiguracaoLLMInvalida, match="OPENAI_API_KEY"):
        build_llm(ModeloRef("openai", "modelo-x"))


def test_llm_model_vence_o_legado(monkeypatch):
    monkeypatch.setattr(settings, "LLM_MODEL", "outro-gemini")
    assert modelo_ativo() == ModeloRef("gemini", "outro-gemini")


def test_embeddings_nao_seguem_llm_provider(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(settings, "OPENAI_MODEL", "modelo-x")

    assert isinstance(build_embeddings(), GoogleGenerativeAIEmbeddings)


def test_indice_slug_estavel():
    ref = ModeloRef("gemini", "models/gemini-embedding-001")
    assert indice_slug(ref) == "gemini__models-gemini-embedding-001"
    assert indice_slug(ref) == indice_slug(ModeloRef("gemini", "models/gemini-embedding-001"))


def test_juiz_openai_mesmo_com_llm_gemini(monkeypatch):
    monkeypatch.setattr(settings, "JUDGE_PROVIDER", "openai")
    monkeypatch.setattr(settings, "JUDGE_MODEL", "juiz-x")

    juiz = build_judge_llm()

    assert isinstance(juiz, ChatOpenAI)
    assert juiz.model_name == "juiz-x"
    assert juiz.temperature == 0
    assert juiz_ativo() == (ModeloRef("openai", "juiz-x"), False)


def test_juiz_vazio_usa_llm_principal():
    assert juiz_ativo() == (modelo_ativo(), True)
    assert isinstance(build_judge_llm(), ChatGoogleGenerativeAI)
