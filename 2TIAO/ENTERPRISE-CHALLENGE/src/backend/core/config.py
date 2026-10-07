"""
Configurações centralizadas — Genera Intelligence
==================================================
Carrega variáveis de ambiente via Pydantic BaseSettings.
Suporta múltiplos providers de LLM (Gemini / OpenAI), escolhidos de forma
independente para geração, embeddings e juiz (LLM-as-a-Judge).
"""

from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parents[1]

Provider = Literal["gemini", "openai"]


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do .env."""

    # ─── Geração (LLM principal) ───────────────────────────────
    # Provider: "gemini" ou "openai". LLM_MODEL vazio = usa o modelo legado do
    # provider (GEMINI_MODEL / OPENAI_MODEL).
    LLM_PROVIDER: Provider = "gemini"
    LLM_MODEL: str = ""

    # ─── Embeddings ────────────────────────────────────────────
    # Independente de LLM_PROVIDER. EMBEDDINGS_MODEL vazio = usa o modelo legado
    # do provider (GEMINI_EMBEDDING_MODEL / OPENAI_EMBEDDING_MODEL). Trocar o
    # modelo de embeddings exige reindexar (`make seed`).
    EMBEDDINGS_PROVIDER: Provider = "gemini"
    EMBEDDINGS_MODEL: str = ""

    # ─── Juiz (LLM-as-a-Judge) ─────────────────────────────────
    # JUDGE_PROVIDER vazio = mesmo provider do LLM principal; JUDGE_MODEL vazio =
    # modelo legado do provider do juiz.
    JUDGE_PROVIDER: Provider | None = None
    JUDGE_MODEL: str = ""

    @field_validator("JUDGE_PROVIDER", mode="before")
    @classmethod
    def _judge_provider_vazio_e_none(cls, valor):
        """`JUDGE_PROVIDER=` (vazio no .env) equivale a não definido."""
        return None if isinstance(valor, str) and not valor.strip() else valor

    # ─── Google Gemini ─────────────────────────────────────────
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # ─── OpenAI ────────────────────────────────────────────────
    # Sem IDs de modelo fixados no código: obrigatórios (via env) ao usar openai.
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = ""
    OPENAI_EMBEDDING_MODEL: str = ""

    # ─── Parâmetros do LLM (compartilhados) ────────────────────
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # ─── Chat: limites por nível de detalhe ────────────────────
    CHAT_MAX_TOKENS_RESUMIDO: int = 400
    CHAT_MAX_TOKENS_DETALHADO: int = 1200
    CHAT_MAX_PALAVRAS_RESUMIDO: int = 120

    # ─── Parâmetros do RAG ─────────────────────────────────────
    RETRIEVER_K: int = 3

    # ─── OCR (ETL) ──────────────────────────────────────────
    # Provider: "paddle_local" (HTTP client to localhost:8100) ou "textract" (AWS).
    OCR_PROVIDER: str = "paddle_local"
    # Bearer token para autenticar requests ao endpoint /api/ocr/
    OCR_TOKEN: str = ""
    # AWS Textract region (ex.: 'us-east-1'); ignorado se OCR_PROVIDER != 'textract'
    TEXTRACT_REGION: str = "us-east-1"
    # AWS credenciais (ignoradas se OCR_PROVIDER != 'textract')
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # `src/backend/.env` é lido mesmo quando o processo roda a partir da raiz do
    # projeto (ex.: `make serve`); `.env` relativo ao cwd continua aceito.
    model_config = {
        "env_file": (str(BACKEND_DIR / ".env"), ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
