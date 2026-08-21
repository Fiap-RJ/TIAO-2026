"""Rota de histórico — expõe as interações anteriores do paciente com o agente."""

from fastapi import APIRouter, Query

from domain.schemas import FonteDado, HistoricoResponse, InteracaoHistorico
from services.history_store import listar_historico

router = APIRouter()


@router.get("/{paciente_id}", response_model=HistoricoResponse)
async def obter_historico(
    paciente_id: str, limite: int = Query(default=100, ge=1, le=500)
) -> HistoricoResponse:
    """Histórico de interações do paciente com o agente, da mais antiga para a mais recente."""
    registros = listar_historico(paciente_id, limite=limite)

    interacoes = [
        InteracaoHistorico(
            id=registro["id"],
            paciente_id=registro["paciente_id"],
            pergunta=registro["pergunta"],
            resposta=registro["resposta"],
            fontes=[FonteDado(**fonte) for fonte in registro["fontes"]],
            criado_em=registro["criado_em"],
        )
        for registro in registros
    ]

    return HistoricoResponse(paciente_id=paciente_id, interacoes=interacoes)
