"""
Configurações centralizadas — Genera Intelligence
==================================================
Carrega variáveis de ambiente via Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do .env."""

    GOOGLE_API_KEY: str = ""
    MODEL_NAME: str = "gemini-2.0-flash-lite"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # Parâmetros do LLM
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # Parâmetros do RAG
    RETRIEVER_K: int = 3

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
