"""
Serviço de Resumos Automáticos — Genera Intelligence
======================================================
Camada de geração e cache dos resumos executivos consumidos pelo endpoint
/api/resumos.

Duas estratégias de geração convivem aqui:

1. Baseada em LLM (Nathalia, Sprint 3): redige o resumo em linguagem natural,
   acolhedora e simplificada, a partir dos dados do laudo/histórico.
2. Determinística (Michael, Sprint 3): agregação estruturada dos dados, sem
   chamada a LLM. Usada como *fallback* quando não há credencial de LLM
   configurada (`GOOGLE_API_KEY`/`OPENAI_API_KEY`), garantindo que o
   endpoint e o schema nunca fiquem indisponíveis — inclusive em CI e em
   ambientes de desenvolvimento sem `.env` preenchido.
"""

import json
import logging
from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage

from core.config import settings
from core.llm import build_llm, extrair_texto_resposta
from services.history_store import contar_interacoes, listar_historico
from services.report_data import JSON_PATH, carregar_relatorio

logger = logging.getLogger(__name__)

_CREDENCIAL_LLM_DISPONIVEL = bool(settings.GOOGLE_API_KEY or settings.OPENAI_API_KEY)

_SYSTEM_PROMPT_RESUMO_RELATORIO = """Você é um especialista em comunicação em saúde acolhedora.
Sua tarefa é ler os dados técnicos de um laudo genético (JSON) e criar um 'Resumo Executivo' \
para um Dashboard.

DIRETRIZES:
1. NO MÁXIMO 3 parágrafos curtos.
2. Destaque os principais resultados (ex: Nutrição, Risco Cardíaco, Pele).
3. Use uma linguagem otimista, tranquilizadora e leiga. Explique jargões.
4. NUNCA emita diagnósticos. Use 'tendências', 'predisposições' ou 'pontos de atenção'.
5. Se tudo estiver bem, enfatize a saúde geral e a importância da prevenção.
6. TERMINE COM: 'Lembre-se: Este resumo é informativo e não substitui a avaliação de um \
profissional de saúde.'
"""

_SYSTEM_PROMPT_RESUMO_INTERACOES = """Você é um assistente de saúde empático.
Analise as últimas perguntas do paciente e resuma em APENAS UMA FRASE CURTA qual o foco \
atual dele.
Formato obrigatório: 'Nas últimas conversas, você tem focado em entender mais sobre \
[TEMA 1] e [TEMA 2].'
Não invente informações que não estão no histórico.
"""


def _versao_relatorio() -> float:
    """Usa o mtime do arquivo de dados como chave de invalidação do cache."""
    return JSON_PATH.stat().st_mtime


def _resumo_relatorio_deterministico(dados: dict) -> str:
    """Fallback sem LLM: agregação estruturada dos dados do laudo."""
    paineis_geneticos = dados.get("paineis_geneticos", [])
    paineis = [p.get("nome_painel", "N/A") for p in paineis_geneticos]
    total_resultados = sum(len(p.get("resultados", [])) for p in paineis_geneticos)
    doencas = [
        item.get("doenca") for item in dados.get("escala_risco_genetico", []) if item.get("doenca")
    ]

    lista_paineis = ", ".join(paineis) if paineis else "nenhum painel disponível"
    partes = [
        f"Seu relatório reúne {total_resultados} característica(s) avaliada(s) em "
        f"{len(paineis)} painel(éis) genético(s): {lista_paineis}."
    ]
    if doencas:
        partes.append("A escala de risco poligênico avaliou: " + ", ".join(doencas) + ".")
    partes.append(
        "Este resumo é gerado automaticamente a partir dos dados do seu laudo e não substitui "
        "a leitura completa do relatório nem uma consulta médica."
    )
    return " ".join(partes)


@lru_cache(maxsize=8)
def _gerar_resumo_relatorio_cached(paciente_id: str, versao: float) -> str:
    dados = carregar_relatorio()

    if not _CREDENCIAL_LLM_DISPONIVEL:
        return _resumo_relatorio_deterministico(dados)

    try:
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT_RESUMO_RELATORIO),
            HumanMessage(content=f"DADOS DO LAUDO:\n{json.dumps(dados, ensure_ascii=False)}"),
        ]
        llm = build_llm()
        response = llm.invoke(messages)
        return extrair_texto_resposta(response.content)
    except Exception:
        logger.warning(
            "Falha ao gerar resumo do relatório via LLM, usando fallback determinístico.",
            exc_info=True,
        )
        return _resumo_relatorio_deterministico(dados)


def gerar_resumo_relatorio(paciente_id: str) -> str:
    """Resumo executivo do relatório (principais painéis e riscos avaliados)."""
    return _gerar_resumo_relatorio_cached(paciente_id, _versao_relatorio())


_cache_resumo_interacoes: dict[str, tuple[int, str]] = {}


def _resumo_interacoes_deterministico(paciente_id: str, quantidade: int) -> str:
    """Fallback sem LLM: lista os últimos temas perguntados."""
    recentes = listar_historico(paciente_id, limite=quantidade)[-5:]
    amostra = [i["pergunta"] for i in recentes if i["pergunta"]]
    return (
        f"Você já fez {quantidade} pergunta(s) ao assistente. "
        f"Últimos temas discutidos: {'; '.join(amostra)}."
    )


def gerar_resumo_interacoes(paciente_id: str) -> str:
    """Resumo do histórico de interações, recalculado apenas quando surgem novas interações."""
    quantidade = contar_interacoes(paciente_id)

    cache_hit = _cache_resumo_interacoes.get(paciente_id)
    if cache_hit and cache_hit[0] == quantidade:
        return cache_hit[1]

    if quantidade == 0:
        resumo = "Você ainda não fez nenhuma pergunta ao assistente."
    elif not _CREDENCIAL_LLM_DISPONIVEL:
        resumo = _resumo_interacoes_deterministico(paciente_id, quantidade)
    else:
        recentes = listar_historico(paciente_id, limite=quantidade)[-5:]
        texto_historico = "\n".join(
            f"- Usuário perguntou: {i['pergunta']}" for i in recentes if i["pergunta"]
        )
        try:
            messages = [
                SystemMessage(content=_SYSTEM_PROMPT_RESUMO_INTERACOES),
                HumanMessage(content=f"Últimas perguntas:\n{texto_historico}"),
            ]
            llm = build_llm()
            response = llm.invoke(messages)
            resumo = extrair_texto_resposta(response.content)
        except Exception:
            logger.warning(
                "Falha ao gerar resumo de interações via LLM, usando fallback determinístico.",
                exc_info=True,
            )
            resumo = _resumo_interacoes_deterministico(paciente_id, quantidade)

    _cache_resumo_interacoes[paciente_id] = (quantidade, resumo)
    return resumo
