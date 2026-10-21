"""
Trechos comuns das instruções e configuração de modelo — CardioIA Fase 6
========================================================================

Texto compartilhado pelas instruções dos quatro agentes (regra de escopo
informativo) e a montagem do ``ModelSettings`` a partir de ``Settings``.
"""

from typing import Any

from agents import ModelSettings
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from core.config import Settings

REGRA_ESCOPO = (
    "Escopo: o CardioIA é um sistema acadêmico, informativo e de apoio à decisão "
    "operacional, com dados sintéticos. Não faça diagnóstico, não indique medicamentos "
    "nem tratamentos e não invente valores: use somente os dados devolvidos pelas tools. "
    "Responda sempre em português do Brasil."
)


def montar_instrucoes(texto: str) -> str:
    """Prefixo recomendado pelo SDK para sistemas com handoff + regra de escopo + texto do agente."""
    return f"{RECOMMENDED_PROMPT_PREFIX}\n\n{REGRA_ESCOPO}\n\n{texto.strip()}"


def montar_model_settings(settings: Settings, **extras: Any) -> ModelSettings:
    """``ModelSettings`` com a temperatura configurada (omitida se ``OPENAI_TEMPERATURE`` vazio)."""
    if settings.OPENAI_TEMPERATURE is not None:
        extras["temperature"] = settings.OPENAI_TEMPERATURE
    return ModelSettings(**extras)
