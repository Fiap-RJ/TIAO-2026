"""
Factory de LLM e Embeddings — Genera Intelligence
==================================================
Instancia o provider correto (Gemini ou OpenAI) com base na configuração.
"""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from core.config import settings


def build_llm() -> BaseChatModel:
    """Constrói a instância do LLM de acordo com o provider configurado."""
    if settings.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

    # Default: Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
        max_output_tokens=settings.LLM_MAX_TOKENS,
        convert_system_message_to_human=True,
    )


def build_embeddings() -> Embeddings:
    """Constrói a instância de embeddings de acordo com o provider configurado."""
    if settings.LLM_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

    # Default: Gemini
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        task_type="RETRIEVAL_DOCUMENT",
    )
