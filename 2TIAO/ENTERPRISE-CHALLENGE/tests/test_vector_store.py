"""Testes do índice FAISS por modelo de embeddings (sem rede: embeddings falsos)."""

import json
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from langchain_core.embeddings import FakeEmbeddings

from core.config import settings
from core.llm import ModeloRef
from services import vector_store


@pytest.fixture(autouse=True)
def _indice_isolado(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "EMBEDDINGS_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "EMBEDDINGS_MODEL", "")
    monkeypatch.setattr(settings, "GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
    monkeypatch.setattr(vector_store, "FAISS_INDEX_PATH", tmp_path)
    monkeypatch.setattr(vector_store, "build_embeddings", lambda ref=None: FakeEmbeddings(size=16))
    vector_store.limpar_cache_indice()
    yield tmp_path
    vector_store.limpar_cache_indice()


def test_diretorio_por_slug(tmp_path):
    ref = ModeloRef("gemini", "models/gemini-embedding-001")
    esperado = tmp_path / "gemini__models-gemini-embedding-001" / "demo"
    assert vector_store.diretorio_indice(ref) == esperado
    assert vector_store.diretorio_indice() == esperado


def test_criar_grava_indice_e_meta():
    destino = vector_store.criar_e_salvar_banco_vetorial()

    assert (destino / "index.faiss").exists()
    meta = json.loads((destino / "meta.json").read_text(encoding="utf-8"))
    assert meta["provider"] == "gemini"
    assert meta["modelo"] == "models/gemini-embedding-001"
    assert meta["n_documentos"] == len(vector_store.carregar_dados_json())
    assert meta["criado_em"]


def test_load_usa_cache_e_tem_todos_os_documentos():
    vector_store.criar_e_salvar_banco_vetorial()

    primeiro = vector_store.load_vector_store()
    segundo = vector_store.load_vector_store()

    assert primeiro is segundo
    assert primeiro.index.ntotal == len(vector_store.carregar_dados_json())


def test_load_reconstroi_quando_indice_ausente():
    destino = vector_store.diretorio_indice()
    assert not destino.exists()

    store = vector_store.load_vector_store()

    assert (destino / "index.faiss").exists()
    assert store.index.ntotal == len(vector_store.carregar_dados_json())


def test_load_reconstroi_quando_meta_incompativel():
    destino = vector_store.criar_e_salvar_banco_vetorial()
    meta_path = destino / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["slug"] = "openai__outro-modelo"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")

    vector_store.load_vector_store()

    meta_corrigido = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta_corrigido["slug"] == "gemini__models-gemini-embedding-001"


def test_load_concorrente_reconstroi_uma_vez(monkeypatch):
    criar_original = vector_store.criar_e_salvar_banco_vetorial
    chamadas: list[int] = []

    def _criar_lento():
        chamadas.append(1)
        time.sleep(0.2)  # janela para as outras threads chegarem ao lock
        return criar_original()

    monkeypatch.setattr(vector_store, "criar_e_salvar_banco_vetorial", _criar_lento)

    with ThreadPoolExecutor(max_workers=4) as executor:
        stores = list(executor.map(lambda _: vector_store.load_vector_store(), range(4)))

    assert len(chamadas) == 1
    assert all(s.index.ntotal == len(vector_store.carregar_dados_json()) for s in stores)


def test_reindexar_invalida_cache():
    vector_store.criar_e_salvar_banco_vetorial()
    antes = vector_store.load_vector_store()

    vector_store.criar_e_salvar_banco_vetorial()

    assert vector_store.load_vector_store() is not antes
