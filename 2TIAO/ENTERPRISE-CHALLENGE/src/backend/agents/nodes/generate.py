"""Nó de geração — invoca o LLM via LangChain com prompt especializado."""

import time
import logging
import json
from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import AgentState
from core.llm import build_llm, extrair_texto_resposta
from prompts import compor_prompt_completo

logger = logging.getLogger(__name__)


def generate(state: AgentState) -> dict:
    """Gera a resposta do assistente usando o contexto recuperado e prompt especializado."""
    start_time = time.perf_counter()
    docs_content = "\n\n".join([d.page_content for d in state.context])

    # Extrai metadados para detecção automática de painel
    context_metadata = [d.metadata for d in state.context]

    # Compõe o system prompt (base + especialização por painel)
    system_prompt = compor_prompt_completo(state.question, context_metadata)

    # Personalização (Sprint 3): injeta o perfil de comunicação do usuário
    # (tom de voz e nível de detalhe) nas diretrizes finais do system prompt.
    tom_usuario = getattr(state, 'user_tone', 'acolhedor')
    nivel_detalhe = getattr(state, 'detail_level', 'resumido')

    system_prompt += f"""
---
DIRETRIZES DE PERSONALIZAÇÃO E COMUNICAÇÃO:
Você deve formatar sua resposta obedecendo ESTRITAMENTE ao perfil abaixo:
- Tom de voz: Adote um tom {tom_usuario}.
- Nível de detalhamento: O tamanho e a profundidade da resposta devem ser {nivel_detalhe}.
- Simplificação: Traduza jargões técnicos de genética para termos do dia a dia, mantendo o \
rigor clínico, mas garantindo que um paciente leigo entenda sem gerar alarde.
---
"""

    # Monta as mensagens no formato ChatModel
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"CONTEXTO DO LAUDO GENÉTICO (fonte única de verdade):\n\n"
                f"{docs_content}\n\n"
                f"PERGUNTA DO PACIENTE:\n{state.question}"
            )
        ),
    ]

    # Invoca o LLM (Gemini ou OpenAI, conforme LLM_PROVIDER)
    llm = build_llm()
    response = llm.invoke(messages)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(json.dumps({
        "request_id": getattr(state, "request_id", "unknown"),
        "node": "generate",
        "latency_ms": latency_ms,
        "status": "success"
    }))

    return {"answer": extrair_texto_resposta(response.content)}
