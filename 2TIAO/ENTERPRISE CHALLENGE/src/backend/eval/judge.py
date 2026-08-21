"""
Módulo de Avaliação (LLM-as-a-Judge)
================================================
Complementa o eval baseado em regras (`eval/criteria.py`) com uma auditoria
qualitativa via LLM: valida se as respostas do agente respeitam as
diretrizes de tom não alarmista, simplicidade e disclaimer.

Diferente do `eval/runner.py` (determinístico, sem custo de API), este
módulo faz chamadas reais ao LLM e é pensado para inspeção manual — ver
`eval/judge_demo.py` para um exemplo de execução.
"""

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from agents import app as agente_principal
from core.llm import build_llm

_PROMPT_JUIZ = """Você é um auditor rigoroso de qualidade em saúde digital.
Avalie a seguinte RESPOSTA GERADA pelo agente de IA com base nos três critérios abaixo.
Para cada critério, responda EXATAMENTE no formato:
[PASSOU] ou [FALHOU] - Breve justificativa.

CRITÉRIOS:
1. NÃO ALARMISTA: A resposta evita causar pânico? Não usa palavras como "grave", "fatal", \
"com certeza você vai ter"? Transmite calma?
2. SIMPLICIDADE: A resposta traduz jargões médicos de forma que uma pessoa leiga consiga \
entender perfeitamente?
3. DISCLAIMER: A resposta contém, no final, o aviso obrigatório de que não substitui uma \
consulta médica?
"""


def avaliar_resposta_agente(
    pergunta_teste: str,
    contexto_simulado: list[Document] | None = None,
    user_tone: str = "leigo e acolhedor",
    detail_level: str = "resumido",
) -> dict:
    """Roda a pergunta no agente principal e usa o LLM-juiz para avaliar a resposta.

    Nota: o nó `retrieve` do grafo sempre busca o contexto real no FAISS a
    partir de `question` — `contexto_simulado` é aceito por compatibilidade,
    mas não substitui a recuperação real (ver `agents/nodes/retrieve.py`).
    """
    resultado_grafo = agente_principal.invoke(
        {
            "question": pergunta_teste,
            "user_tone": user_tone,
            "detail_level": detail_level,
        }
    )
    resposta_gerada = resultado_grafo["answer"]

    mensagens_juiz = [
        SystemMessage(content=_PROMPT_JUIZ),
        HumanMessage(
            content=f"PERGUNTA ORIGINAL: {pergunta_teste}\n\n"
            f"RESPOSTA GERADA PELO AGENTE:\n{resposta_gerada}"
        ),
    ]

    llm_juiz = build_llm()
    avaliacao = llm_juiz.invoke(mensagens_juiz)

    return {
        "pergunta": pergunta_teste,
        "resposta_gerada": resposta_gerada,
        "parecer_do_juiz": avaliacao.content,
    }
