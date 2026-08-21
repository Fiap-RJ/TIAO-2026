"""
Módulo de Prompts — Genera Intelligence
========================================
Compõe prompts especializados por painel genético.
Todos os prompts são constantes Python — sem I/O de filesystem.
"""

from prompts.base import SYSTEM_BASE
from prompts.specialists import (
    AGENT_FARMA,
    AGENT_FIT,
    AGENT_NUTRI,
    AGENT_RISCO,
    AGENT_SKIN,
)

# Mapeamento de palavras-chave → prompt especializado
_PANEL_PROMPT_MAP: dict[str, str] = {
    "genera skin": AGENT_SKIN,
    "genera fit": AGENT_FIT,
    "genera nutri": AGENT_NUTRI,
    "genera farma": AGENT_FARMA,
    "escala de risco": AGENT_RISCO,
    "risco genético": AGENT_RISCO,
    "câncer": AGENT_RISCO,
    "doença": AGENT_RISCO,
}


def _detectar_painel(question: str, context_metadata: list[dict]) -> str | None:
    """
    Detecta qual painel genético é mais relevante para a pergunta,
    baseando-se nos metadados dos documentos recuperados e na pergunta do usuário.

    Retorna o prompt especializado ou None para usar apenas o base.
    """
    # Prioridade 1: metadados dos documentos recuperados
    paineis_encontrados = set()
    for meta in context_metadata:
        painel = meta.get("painel", "").lower()
        if painel:
            paineis_encontrados.add(painel)

    for painel in paineis_encontrados:
        for key, prompt in _PANEL_PROMPT_MAP.items():
            if key in painel:
                return prompt

    # Prioridade 2: palavras-chave na pergunta do usuário
    question_lower = question.lower()
    for key, prompt in _PANEL_PROMPT_MAP.items():
        if key in question_lower:
            return prompt

    return None


def compor_prompt_completo(question: str, context_metadata: list[dict]) -> str:
    """
    Compõe o system prompt final combinando:
    1. Prompt base (regras gerais invioláveis)
    2. Prompt especializado do painel detectado (se aplicável)
    """
    prompt_especializado = _detectar_painel(question, context_metadata)

    if prompt_especializado:
        return (
            f"{SYSTEM_BASE}\n\n"
            f"═══════════════════════════════════════════\n"
            f"ESPECIALIZAÇÃO DO AGENTE\n"
            f"═══════════════════════════════════════════\n\n"
            f"{prompt_especializado}"
        )

    return SYSTEM_BASE
