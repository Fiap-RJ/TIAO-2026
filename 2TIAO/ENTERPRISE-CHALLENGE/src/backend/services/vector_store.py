"""
Serviço de Vector Store — Genera Intelligence
==============================================
Responsável pela ingestão de dados genéticos no FAISS e carregamento do índice.
"""

import json
import logging
import os
import re
import threading
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from core.llm import ModeloRef, build_embeddings, embeddings_ativo

load_dotenv()

logger = logging.getLogger(__name__)

CURRENT_DIR = Path(__file__).parent
BACKEND_DIR = CURRENT_DIR.parent

# Path do JSON: usa env var (Docker) ou infere do layout local
_default_json = BACKEND_DIR.parent.parent / "proposta_estrutura_de_dados.json"
JSON_PATH = Path(os.getenv("GENERA_DATA_PATH", str(_default_json)))
FAISS_INDEX_PATH = Path(os.getenv("GENERA_FAISS_PATH", str(BACKEND_DIR / "faiss_index")))

# Serializa a reconstrução do índice entre threads (ver `load_vector_store`).
_LOCK_REINDEXACAO = threading.Lock()


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


def indice_slug(ref: ModeloRef) -> str:
    """Nome de diretório estável para o índice de um modelo de embeddings."""
    return f"{ref.provider}__{re.sub('[^a-z0-9]+', '-', ref.modelo.lower())}"


def diretorio_indice(ref: ModeloRef | None = None, chave: str = "demo") -> Path:
    """Diretório do índice: GENERA_FAISS_PATH/<slug do modelo de embeddings>/<chave>/."""
    ref = ref or embeddings_ativo()
    return FAISS_INDEX_PATH / indice_slug(ref) / chave


def _build_embeddings():
    """Constrói os embeddings ativos (EMBEDDINGS_PROVIDER/EMBEDDINGS_MODEL)."""
    return build_embeddings(embeddings_ativo())


def criar_e_salvar_banco_vetorial() -> Path:
    """Gera embeddings, salva o índice FAISS e grava o `meta.json` do modelo usado."""
    ref = embeddings_ativo()
    destino = diretorio_indice(ref)
    documentos = carregar_dados_json()
    embeddings = _build_embeddings()
    vector_store = FAISS.from_documents(documentos, embeddings)

    destino.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(destino))
    meta = {
        "provider": ref.provider,
        "modelo": ref.modelo,
        "slug": indice_slug(ref),
        "n_documentos": len(documentos),
        "criado_em": datetime.now(timezone.utc).isoformat(),
    }
    (destino / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    limpar_cache_indice()
    print(f"✅ Banco Vetorial salvo com {len(documentos)} documentos em {destino}")
    return destino


@lru_cache(maxsize=4)
def _carregar_indice(caminho: str) -> FAISS:
    """Carrega (uma vez por caminho) o índice FAISS do disco."""
    return FAISS.load_local(
        caminho,
        _build_embeddings(),
        allow_dangerous_deserialization=True,
    )


def limpar_cache_indice() -> None:
    """Invalida o cache de índices carregados (chamado ao reindexar)."""
    _carregar_indice.cache_clear()


def load_vector_store() -> FAISS:
    """Carrega o índice FAISS do modelo de embeddings ativo.

    Índice ausente, ou com `meta.json` ausente/de outro modelo, é reconstruído
    sob demanda — nunca se carrega um índice incompatível com os embeddings ativos.
    """
    ref = embeddings_ativo()
    destino = diretorio_indice(ref)

    if not _indice_compativel(destino, ref):
        # Requisições concorrentes (rotas `def` rodam no threadpool) não podem
        # reconstruir o mesmo índice em paralelo: só uma reindexa, e as demais
        # reconferem depois de obter o lock e reaproveitam o índice novo.
        with _LOCK_REINDEXACAO:
            if not (destino / "index.faiss").exists():
                logger.info("Índice FAISS ausente em %s — reconstruindo.", destino)
                criar_e_salvar_banco_vetorial()
            elif _slug_do_meta(destino) != indice_slug(ref):
                logger.warning(
                    "Índice FAISS em %s sem meta.json compatível com %s — reconstruindo.",
                    destino,
                    ref,
                )
                criar_e_salvar_banco_vetorial()

    return _carregar_indice(str(destino))


def _indice_compativel(destino: Path, ref: ModeloRef) -> bool:
    """Índice presente e com `meta.json` do modelo de embeddings `ref`."""
    return (destino / "index.faiss").exists() and _slug_do_meta(destino) == indice_slug(ref)


def _slug_do_meta(destino: Path) -> str | None:
    """Slug registrado no `meta.json` do índice (None se ausente ou ilegível)."""
    try:
        meta = json.loads((destino / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return meta.get("slug") if isinstance(meta, dict) else None


if __name__ == "__main__":
    criar_e_salvar_banco_vetorial()
