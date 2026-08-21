"""Nó de recuperação — busca semântica no banco vetorial FAISS."""

from agents.state import AgentState
from core.config import settings
from services.vector_store import load_vector_store


def retrieve(state: AgentState) -> dict:
    """Recupera os documentos mais relevantes do laudo genético via similaridade semântica."""
    vector_store = load_vector_store()
    docs = vector_store.similarity_search(state.question, k=settings.RETRIEVER_K)
    return {"context": docs}
