"""
Configurações centralizadas — Genera Intelligence
==================================================
Carrega variáveis de ambiente via Pydantic BaseSettings.
Suporta múltiplos providers de LLM (Gemini / OpenAI).
"""

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do .env."""

    # Provider: "gemini" ou "openai"
    LLM_PROVIDER: Literal["gemini", "openai"] = "gemini"

    # Google Gemini
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Parâmetros do LLM (compartilhados)
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # Parâmetros do RAG
    RETRIEVER_K: int = 3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
