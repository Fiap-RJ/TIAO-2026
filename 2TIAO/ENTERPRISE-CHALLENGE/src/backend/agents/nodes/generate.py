"""Nó de geração — invoca o LLM via LangChain com prompt especializado."""

import json
import logging
import time

from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import AgentState
from core.config import settings
from core.llm import build_llm, extrair_texto_resposta
from prompts import compor_prompt_completo
from services.formatacao import limitar_corpo

logger = logging.getLogger(__name__)

_DISCLAIMER = (
    '"⚠️ Importante: Este assistente é informativo e não substitui consulta médica. '
    'A genética indica tendências, não certezas."'
)

_ESTRUTURA_RESUMIDO = f"""\
- Formato (modo RESUMIDO): seja conciso, NUNCA ultrapasse {{max_palavras}} palavras e \
formate a resposta ESTRITAMENTE nesta estrutura:
  - Resposta direta: vá direto ao ponto sobre o que o laudo diz, de forma simples.
  - O que fazer: uma orientação prática e acolhedora baseada no laudo (sem prescrever).
  - Disclaimer curto: {_DISCLAIMER}
  - Fechamento: termine SEMPRE com a pergunta: "Você quer que eu explique com mais detalhes?\""""

_ESTRUTURA_DETALHADO = f"""\
- Formato (modo DETALHADO): explique com mais profundidade, em até ~300 palavras. Pode \
detalhar genes, marcadores e mecanismos usando analogias do cotidiano, sempre ancorado no laudo.
  - Inclua obrigatoriamente o disclaimer: {_DISCLAIMER}
  - NÃO termine com a pergunta "Você quer que eu explique com mais detalhes?"."""


def generate(state: AgentState) -> dict:
    """Gera a resposta do assistente usando o contexto recuperado e prompt especializado."""
    start_time = time.perf_counter()
    docs_content = "\n\n".join([d.page_content for d in state.context])

    # Extrai metadados para detecção automática de painel
    context_metadata = [d.metadata for d in state.context]

    # Compõe o system prompt (base + especialização por painel)
    system_prompt = compor_prompt_completo(state.question, context_metadata)

    # Personalização: tom de voz e nível de detalhe (resumido | detalhado).
    tom_usuario = getattr(state, "user_tone", "acolhedor")
    modo = state.detail_level if state.detail_level in ("resumido", "detalhado") else "resumido"
    if modo == "resumido":
        estrutura = _ESTRUTURA_RESUMIDO.format(max_palavras=settings.CHAT_MAX_PALAVRAS_RESUMIDO)
        max_tokens = settings.CHAT_MAX_TOKENS_RESUMIDO
    else:
        estrutura = _ESTRUTURA_DETALHADO
        max_tokens = settings.CHAT_MAX_TOKENS_DETALHADO

    system_prompt += f"""
---
DIRETRIZES DE PERSONALIZAÇÃO E COMUNICAÇÃO:
Você deve formatar sua resposta obedecendo ESTRITAMENTE ao perfil abaixo:
- Tom de voz: Adote um tom {tom_usuario}.
{estrutura}
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

    # Invoca o LLM (provider/modelo conforme LLM_PROVIDER/LLM_MODEL)
    llm = build_llm(max_tokens=max_tokens)
    response = llm.invoke(messages)
    resposta = extrair_texto_resposta(response.content)

    # Limite real de tamanho no modo resumido: só o corpo é contado/cortado; o
    # fechamento (disclaimer + pergunta final) é preservado. Se o LLM omitir o
    # disclaimer, o nó `guardrail` (executado em seguida) o reinsere.
    if modo == "resumido":
        resposta = limitar_corpo(resposta, settings.CHAT_MAX_PALAVRAS_RESUMIDO)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "request_id": getattr(state, "request_id", "unknown"),
                "node": "generate",
                "modo": modo,
                "latency_ms": latency_ms,
                "status": "success",
            }
        )
    )

    return {"answer": resposta}
