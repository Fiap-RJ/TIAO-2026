"""Rota de métricas — agrega e expõe dados de observabilidade do pipeline RAG."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# Em um cenário real, estas métricas viriam de um banco de dados de séries temporais
# (como Prometheus ou InfluxDB) ou da agregação dos logs JSON que criamos na Tarefa N3.
# Para este MVP, manteremos um armazenamento simples em memória.
class PipelineMetrics(BaseModel):
    total_requisicoes: int = 0
    latencia_media_ms: float = 0.0
    taxa_bloqueio_guardrail_percentual: float = 0.0
    ultimas_violacoes: list[str] = []


# Variável global para armazenar o estado das métricas em memória
_current_metrics = PipelineMetrics()


def registrar_execucao(latencia_total_ms: float, bloqueado: bool, violacoes: list[str] = None):
    """Função auxiliar para ser chamada dentro de chat.py após cada requisição."""
    global _current_metrics

    # Atualiza total
    _current_metrics.total_requisicoes += 1

    # Atualiza média móvel simples da latência
    # (Nova Média = Média Antiga + (Novo Valor - Média Antiga) / N)
    _current_metrics.latencia_media_ms += (
        latencia_total_ms - _current_metrics.latencia_media_ms
    ) / _current_metrics.total_requisicoes

    # Atualiza taxa de bloqueio
    total_bloqueios = (_current_metrics.taxa_bloqueio_guardrail_percentual / 100.0) * (
        _current_metrics.total_requisicoes - 1
    )
    if bloqueado:
        total_bloqueios += 1

    _current_metrics.taxa_bloqueio_guardrail_percentual = (
        total_bloqueios / _current_metrics.total_requisicoes
    ) * 100

    # Armazena as últimas 5 violações para o dashboard
    if violacoes:
        for v in violacoes:
            _current_metrics.ultimas_violacoes.insert(0, v)
        _current_metrics.ultimas_violacoes = _current_metrics.ultimas_violacoes[:5]


@router.get("/", response_model=PipelineMetrics)
async def get_metrics():
    """Retorna as métricas de saúde e segurança do pipeline para o Dashboard."""
    return _current_metrics
