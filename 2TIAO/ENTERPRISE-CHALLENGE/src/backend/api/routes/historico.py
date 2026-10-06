"""Rota de histórico — expõe as interações anteriores do paciente com o agente."""

import logging
from fastapi import APIRouter, Query, HTTPException, status

from domain.schemas import FonteDado, HistoricoResponse, InteracaoHistorico
from services.history_store import listar_historico

logger = logging.getLogger(__name__)
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

@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def apagar_historico(paciente_id: str):
    """
    Remove todo o histórico de interações do paciente.
    Cumpre o requisito da LGPD de Direito ao Esquecimento (fechamento do risco R9).
    """
    sucesso = excluir_historico_paciente(paciente_id)
    
    if not sucesso:
        raise HTTPException(status_code=404, detail="Histórico não encontrado ou já excluído.")
    
    logger.info("Histórico do paciente %s excluído com sucesso via requisição de titular (LGPD).", paciente_id)
    
    return None