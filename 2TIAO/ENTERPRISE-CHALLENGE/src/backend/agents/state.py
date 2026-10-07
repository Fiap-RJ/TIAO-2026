"""
Estado tipado do grafo LangGraph.
Define o contrato de dados que flui entre os nós do pipeline RAG.
"""

import uuid

from langchain_core.documents import Document
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Estado compartilhado entre todos os nós do grafo."""

    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="ID único para rastreamento da requisição nos logs.",
    )
    question: str = Field(default="", description="Pergunta do paciente (sanitizada).")
    context: list[Document] = Field(
        default_factory=list,
        description="Documentos recuperados do banco vetorial FAISS.",
    )
    answer: str = Field(default="", description="Resposta final gerada pelo LLM e validada.")

    # Resultado do nó `guardrail` — consumido pela rota de chat e pelas métricas.
    violacoes: list[str] = Field(
        default_factory=list,
        description="Violações de guardrail detectadas na resposta (ex: [DIAGNÓSTICO] ...).",
    )
    bloqueado: bool = Field(
        default=False,
        description="True quando o guardrail bloqueou a resposta original do LLM.",
    )

    # Personalização (Sprint 3) — perfil de comunicação aplicado pelo nó `generate`.
    user_tone: str = Field(
        default="empático e didático",
        description="Tom de voz que a IA deve adotar ao responder (ex: empático, técnico, direto).",
    )
    detail_level: str = Field(
        default="resumido",
        description="Nível de profundidade da resposta (ex: resumido, detalhado).",
    )

    model_config = {"arbitrary_types_allowed": True}
