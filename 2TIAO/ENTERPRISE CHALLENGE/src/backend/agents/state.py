"""
Estado tipado do grafo LangGraph.
Define o contrato de dados que flui entre os nós do pipeline RAG.
"""

from langchain_core.documents import Document
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Estado compartilhado entre todos os nós do grafo."""

    question: str = Field(default="", description="Pergunta do paciente (sanitizada).")
    context: list[Document] = Field(
        default_factory=list,
        description="Documentos recuperados do banco vetorial FAISS.",
    )
    answer: str = Field(default="", description="Resposta final gerada pelo LLM e validada.")

    model_config = {"arbitrary_types_allowed": True}
