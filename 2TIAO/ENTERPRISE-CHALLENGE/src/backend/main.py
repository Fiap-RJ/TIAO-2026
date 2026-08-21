"""
Genera Intelligence API — Bootstrap
====================================
Ponto de entrada da aplicação FastAPI.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import ancestralidade, chat, historico, resumos, riscos

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

app = FastAPI(
    title="Genera Intelligence API",
    description="Motor RAG e Multi-Agent para Interpretação de Laudos Genéticos (Dasa)",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["Chat Conversacional"])
app.include_router(riscos.router, prefix="/api/riscos", tags=["Dashboard — Riscos"])
app.include_router(
    ancestralidade.router, prefix="/api/ancestralidade", tags=["Dashboard — Ancestralidade"]
)
app.include_router(resumos.router, prefix="/api/resumos", tags=["Dashboard — Resumos"])
app.include_router(historico.router, prefix="/api/historico", tags=["Dashboard — Histórico"])


@app.get("/health", tags=["Monitoramento"])
def health_check():
    """Verifica se a API está operacional."""
    return {"status": "ok", "message": "Genera Intelligence API operacional."}
