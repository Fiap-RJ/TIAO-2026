"""Nó de recuperação — busca semântica no banco vetorial FAISS."""
import time
import logging
import json
from agents.state import AgentState
from core.config import settings
from services.vector_store import load_vector_store

logger = logging.getLogger(__name__)

def retrieve(state: AgentState) -> dict:
    """Recupera os documentos mais relevantes do laudo genético via similaridade semântica."""
    start_time = time.perf_counter()
    vector_store = load_vector_store()
    docs = vector_store.similarity_search(state.question, k=settings.RETRIEVER_K)
    
    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(json.dumps({
        "request_id": getattr(state, "request_id", "unknown"),
        "node": "retrieve",
        "latency_ms": latency_ms,
        "docs_retrieved": len(docs),
        "status": "success"
    }))
    
    return {"context": docs}
