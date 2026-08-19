"""
Serviço de Resumos Automáticos — Genera Intelligence
======================================================
Camada de geração e cache dos resumos executivos consumidos pelo endpoint
/api/resumos.

A geração aqui é determinística (agregação estruturada dos dados do
laudo/histórico, sem chamada a LLM), servindo de contrato estável para o
front-end: endpoint e schema não mudam quando a geração baseada em LLM
(responsabilidade da Nathalia) substituir estas funções por um resumo
redigido de forma mais natural.
"""

from functools import lru_cache

from services.history_store import contar_interacoes, listar_historico
from services.report_data import JSON_PATH, carregar_relatorio


def _versao_relatorio() -> float:
    """Usa o mtime do arquivo de dados como chave de invalidação do cache."""
    return JSON_PATH.stat().st_mtime


@lru_cache(maxsize=8)
def _gerar_resumo_relatorio_cached(paciente_id: str, versao: float) -> str:
    dados = carregar_relatorio()

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


def gerar_resumo_relatorio(paciente_id: str) -> str:
    """Resumo executivo do relatório (principais painéis e riscos avaliados)."""
    return _gerar_resumo_relatorio_cached(paciente_id, _versao_relatorio())


_cache_resumo_interacoes: dict[str, tuple[int, str]] = {}


def gerar_resumo_interacoes(paciente_id: str) -> str:
    """Resumo do histórico de interações, recalculado apenas quando surgem novas interações."""
    quantidade = contar_interacoes(paciente_id)

    cache_hit = _cache_resumo_interacoes.get(paciente_id)
    if cache_hit and cache_hit[0] == quantidade:
        return cache_hit[1]

    if quantidade == 0:
        resumo = "Você ainda não fez nenhuma pergunta ao assistente."
    else:
        recentes = listar_historico(paciente_id, limite=quantidade)[-5:]
        amostra = [i["pergunta"] for i in recentes if i["pergunta"]]
        resumo = (
            f"Você já fez {quantidade} pergunta(s) ao assistente. "
            f"Últimos temas discutidos: {'; '.join(amostra)}."
        )

    _cache_resumo_interacoes[paciente_id] = (quantidade, resumo)
    return resumo
