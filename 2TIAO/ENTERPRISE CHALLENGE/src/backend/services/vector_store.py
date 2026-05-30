"""
Serviço de Vector Store — Genera Intelligence
==============================================
Responsável pela ingestão de dados genéticos no FAISS e carregamento do índice.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from core.config import settings
from core.llm import build_embeddings

load_dotenv()

CURRENT_DIR = Path(__file__).parent
BACKEND_DIR = CURRENT_DIR.parent

# Path do JSON: usa env var (Docker) ou infere do layout local
_default_json = BACKEND_DIR.parent.parent / "proposta_estrutura_de_dados.json"
JSON_PATH = Path(os.getenv("GENERA_DATA_PATH", str(_default_json)))
FAISS_INDEX_PATH = Path(os.getenv("GENERA_FAISS_PATH", str(BACKEND_DIR / "faiss_index")))


def _carregar_paineis(dados: dict) -> list[Document]:
    """Converte os painéis genéticos em documentos para o vector store."""
    documentos = []
    for painel in dados.get("paineis_geneticos", []):
        for resultado in painel.get("resultados", []):
            conteudo = (
                f"Painel: {painel.get('nome_painel')}. "
                f"Característica: {resultado['caracteristica']}. "
                f"Conclusão: {resultado['conclusao_curta']}. "
                f"Explicação: {resultado['explicacao_detalhada']}. "
                f"Recomendações: {'; '.join(resultado.get('recomendacoes', []))}."
            )
            metadados = {
                "painel": painel.get("nome_painel"),
                "caracteristica": resultado.get("caracteristica"),
                "gene": resultado.get("dados_tecnicos", {}).get("gene", "N/A"),
                "snp": resultado.get("dados_tecnicos", {}).get("snp", "N/A"),
                "genotipo": resultado.get("dados_tecnicos", {}).get("genotipo", "N/A"),
                "conclusao_curta": resultado.get("conclusao_curta"),
                "categoria_impacto": resultado.get("categoria_impacto", "N/A"),
            }
            documentos.append(Document(page_content=conteudo, metadata=metadados))
    return documentos


def _carregar_escala_risco(dados: dict) -> list[Document]:
    """Converte a escala de risco genético em documentos para o vector store."""
    documentos = []
    for risco in dados.get("escala_risco_genetico", []):
        marcadores_texto = "; ".join(
            f"SNP {m.get('snp', 'N/A')} (gene {m.get('gene', 'N/A')}, "
            f"genótipo {m.get('genotipo', 'N/A')}, alelo de risco {m.get('alelo_risco', 'N/A')})"
            for m in risco.get("marcadores_associados", [])
        )

        intervalo = risco.get("intervalo_risco", {})
        conteudo = (
            f"Escala de Risco Genético — Doença: {risco.get('doenca')}. "
            f"Risco calculado: {risco.get('risco_calculado_porcentagem')}% "
            f"(intervalo: {intervalo.get('minimo', 'N/A')}% a {intervalo.get('maximo', 'N/A')}%). "
            f"Classificação: {risco.get('classificacao_risco')}. "
            f"Marcadores associados: {marcadores_texto}."
        )
        metadados = {
            "painel": "Escala de Risco Genético",
            "caracteristica": risco.get("doenca"),
            "gene": ", ".join(m.get("gene", "N/A") for m in risco.get("marcadores_associados", [])),
            "conclusao_curta": (
                f"{risco.get('classificacao_risco')} — {risco.get('risco_calculado_porcentagem')}%"
            ),
            "categoria_impacto": risco.get("classificacao_risco", "N/A"),
        }
        documentos.append(Document(page_content=conteudo, metadata=metadados))
    return documentos


def carregar_dados_json() -> list[Document]:
    """Carrega e converte todos os dados do JSON em documentos indexáveis."""
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        dados = json.load(f)

    documentos = []
    documentos.extend(_carregar_paineis(dados))
    documentos.extend(_carregar_escala_risco(dados))
    return documentos


def _build_embeddings():
    """Constrói a instância de embeddings via factory (respeita LLM_PROVIDER)."""
    return build_embeddings()


def criar_e_salvar_banco_vetorial():
    """Gera embeddings e salva o índice FAISS localmente."""
    documentos = carregar_dados_json()
    embeddings = _build_embeddings()
    vector_store = FAISS.from_documents(documentos, embeddings)
    vector_store.save_local(str(FAISS_INDEX_PATH))
    print(f"✅ Banco Vetorial salvo com {len(documentos)} documentos em {FAISS_INDEX_PATH}")


def load_vector_store() -> FAISS:
    """Carrega o índice FAISS do disco."""
    embeddings = _build_embeddings()
    return FAISS.load_local(
        str(FAISS_INDEX_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )


if __name__ == "__main__":
    criar_e_salvar_banco_vetorial()
