"""Nó de sanitização — remove PII do input do usuário antes do processamento."""

from agents.state import AgentState
from services.pii_redaction import sanitizar_input_usuario


def sanitize(state: AgentState) -> dict:
    """Remove dados pessoais identificáveis da pergunta do paciente."""
    pergunta_limpa = sanitizar_input_usuario(state.question)
    return {"question": pergunta_limpa}
