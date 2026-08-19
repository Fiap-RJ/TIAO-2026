"""Rota de riscos — expõe os dados de risco por categoria para o dashboard."""

from fastapi import APIRouter

from domain.schemas import DoencaRisco, NivelRisco, PainelRisco, ResultadoRisco, RiscosResponse
from services.report_data import carregar_relatorio

router = APIRouter()

# Traduz a categoria textual do laudo em um nível neutro (nunca "perigo"/vermelho puro).
_MAPA_NIVEL_PAINEL: dict[str, NivelRisco] = {
    "cuidados relevantes": NivelRisco.BAIXO,
    "pontos de atenção": NivelRisco.MODERADO,
    "intervenção médica recomendada": NivelRisco.ATENCAO,
}

_MAPA_NIVEL_ESCALA: dict[str, NivelRisco] = {
    "risco reduzido": NivelRisco.BAIXO,
    "risco médio": NivelRisco.MODERADO,
    "risco aumentado": NivelRisco.ATENCAO,
}


def _classificar(categoria: str | None, mapa: dict[str, NivelRisco]) -> NivelRisco:
    """Categorias não mapeadas caem em MODERADO — nunca no nível mais alto por padrão."""
    return mapa.get((categoria or "").strip().lower(), NivelRisco.MODERADO)


@router.get("/", response_model=RiscosResponse)
async def obter_riscos() -> RiscosResponse:
    """Retorna os riscos por painel e a escala de risco poligênico, com nível normalizado."""
    dados = carregar_relatorio()

    paineis = [
        PainelRisco(
            nome_painel=painel.get("nome_painel", "N/A"),
            descricao=painel.get("descricao", ""),
            resultados=[
                ResultadoRisco(
                    caracteristica=resultado["caracteristica"],
                    nivel=_classificar(resultado.get("categoria_impacto"), _MAPA_NIVEL_PAINEL),
                    categoria_original=resultado.get("categoria_impacto", "N/A"),
                    conclusao_curta=resultado.get("conclusao_curta", ""),
                    explicacao_detalhada=resultado.get("explicacao_detalhada", ""),
                    recomendacoes=resultado.get("recomendacoes", []),
                    gene=resultado.get("dados_tecnicos", {}).get("gene", "N/A"),
                )
                for resultado in painel.get("resultados", [])
            ],
        )
        for painel in dados.get("paineis_geneticos", [])
    ]

    escala_risco = [
        DoencaRisco(
            doenca=item["doenca"],
            nivel=_classificar(item.get("classificacao_risco"), _MAPA_NIVEL_ESCALA),
            risco_calculado_percentual=item.get("risco_calculado_porcentagem", 0.0),
            intervalo_minimo=item.get("intervalo_risco", {}).get("minimo", 0.0),
            intervalo_maximo=item.get("intervalo_risco", {}).get("maximo", 0.0),
            classificacao_original=item.get("classificacao_risco", "N/A"),
        )
        for item in dados.get("escala_risco_genetico", [])
    ]

    return RiscosResponse(
        paciente_id=dados.get("paciente_id", "N/A"),
        paineis=paineis,
        escala_risco_genetico=escala_risco,
    )
