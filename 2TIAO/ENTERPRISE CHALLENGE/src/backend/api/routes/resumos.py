"""Rota de resumos — expõe os resumos automáticos do relatório e das interações."""

from datetime import datetime, timezone

from fastapi import APIRouter

from domain.schemas import ResumoInteracoesResponse, ResumoRelatorioResponse
from services.history_store import contar_interacoes
from services.resumo import gerar_resumo_interacoes, gerar_resumo_relatorio

router = APIRouter()


@router.get("/relatorio/{paciente_id}", response_model=ResumoRelatorioResponse)
async def obter_resumo_relatorio(paciente_id: str) -> ResumoRelatorioResponse:
    """Resumo executivo automático do relatório genético."""
    resumo = gerar_resumo_relatorio(paciente_id)
    return ResumoRelatorioResponse(
        paciente_id=paciente_id,
        resumo=resumo,
        gerado_em=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/interacoes/{paciente_id}", response_model=ResumoInteracoesResponse)
async def obter_resumo_interacoes(paciente_id: str) -> ResumoInteracoesResponse:
    """Resumo automático do histórico de interações do paciente com o agente."""
    resumo = gerar_resumo_interacoes(paciente_id)
    return ResumoInteracoesResponse(
        paciente_id=paciente_id,
        resumo=resumo,
        quantidade_interacoes=contar_interacoes(paciente_id),
        gerado_em=datetime.now(timezone.utc).isoformat(),
    )
