"""
Builder do grafo LangGraph — Genera Intelligence
=================================================
Monta e compila o pipeline RAG:
    sanitize → retrieve → generate → guardrail → END
"""

from langgraph.graph import END, StateGraph

from agents.nodes import generate, guardrail, retrieve, sanitize
from agents.state import AgentState


def build_graph():
    """Constrói e compila o grafo do agente médico RAG."""
    workflow = StateGraph(AgentState)

    # Registra os nós
    workflow.add_node("sanitize", sanitize)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_node("guardrail", guardrail)

    # Define o fluxo linear
    workflow.set_entry_point("sanitize")
    workflow.add_edge("sanitize", "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", "guardrail")
    workflow.add_edge("guardrail", END)

    return workflow.compile()
