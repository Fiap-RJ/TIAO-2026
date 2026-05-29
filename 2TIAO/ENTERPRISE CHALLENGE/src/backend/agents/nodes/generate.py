"""Nó de geração — invoca o LLM via LangChain com prompt especializado."""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AgentState
from core.config import settings
from prompts import compor_prompt_completo


def _build_llm() -> ChatGoogleGenerativeAI:
    """Constrói a instância do LLM com as configurações centralizadas."""
    return ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
        max_output_tokens=settings.LLM_MAX_TOKENS,
        convert_system_message_to_human=True,
    )


def generate(state: AgentState) -> dict:
    """Gera a resposta do assistente usando o contexto recuperado e prompt especializado."""
    docs_content = "\n\n".join([d.page_content for d in state.context])

    # Extrai metadados para detecção automática de painel
    context_metadata = [d.metadata for d in state.context]

    # Compõe o system prompt (base + especialização por painel)
    system_prompt = compor_prompt_completo(state.question, context_metadata)

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

    # Invoca o LLM via LangChain
    llm = _build_llm()
    response = llm.invoke(messages)

    return {"answer": response.content}
