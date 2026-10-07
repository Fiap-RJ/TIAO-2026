"""Rota de ancestralidade — expõe a composição de ancestralidade do relatório."""

from fastapi import APIRouter

from api.params import PacienteIdPath
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
    return _montar_ancestralidade(None)


# `:path` faz IDs com "/" (ex.: "..%2F..") chegarem à validação (422), em vez de 404.
@router.get("/{paciente_id:path}", response_model=AncestralidadeResponse)
async def obter_ancestralidade_paciente(paciente_id: PacienteIdPath) -> AncestralidadeResponse:
    """Ancestralidade do paciente informado.

    Nesta fase devolve o laudo de DEMONSTRAÇÃO ecoando o `paciente_id` pedido;
    a troca para o laudo do próprio paciente vem com o ETL de laudos.
    """
    return _montar_ancestralidade(paciente_id)


def _montar_ancestralidade(paciente_id: str | None) -> AncestralidadeResponse:
    """Monta a resposta de ancestralidade; `None` usa o ID do próprio laudo."""
    dados = carregar_relatorio()

    composicao = [
        ComposicaoAncestralidade(regiao=item["regiao"], percentual=item["percentual"])
        for item in dados.get("composicao_ancestralidade", [])
    ]

    return AncestralidadeResponse(
        paciente_id=paciente_id or dados.get("paciente_id", "N/A"),
        composicao=composicao,
        observacao=_OBSERVACAO,
    )
