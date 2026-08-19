"""Rota de ancestralidade — expõe a composição de ancestralidade do relatório."""

from fastapi import APIRouter

from domain.schemas import AncestralidadeResponse, ComposicaoAncestralidade
from services.report_data import carregar_relatorio

router = APIRouter()

_OBSERVACAO = (
    "Estimativa de ancestralidade baseada em painéis populacionais de referência. "
    "Trata-se de uma aproximação estatística, não uma genealogia exata."
)


@router.get("/", response_model=AncestralidadeResponse)
async def obter_ancestralidade() -> AncestralidadeResponse:
    """Retorna a composição de ancestralidade do relatório do paciente."""
    dados = carregar_relatorio()

    composicao = [
        ComposicaoAncestralidade(regiao=item["regiao"], percentual=item["percentual"])
        for item in dados.get("composicao_ancestralidade", [])
    ]

    return AncestralidadeResponse(
        paciente_id=dados.get("paciente_id", "N/A"),
        composicao=composicao,
        observacao=_OBSERVACAO,
    )
