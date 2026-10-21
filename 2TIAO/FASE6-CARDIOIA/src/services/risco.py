"""
Avaliação de risco — CardioIA Fase 6
====================================

Fonte única da probabilidade e da faixa de risco:

- ``BAIXO``    : p < 0,40
- ``MODERADO`` : 0,40 ≤ p < 0,70 (contém o limiar de decisão 0,50)
- ``ALTO``     : p ≥ 0,70 (equivale ao "risco sistêmico alto" do protocolo P10)

Não importa o OpenAI Agents SDK: é chamado pelas tools dos agentes, pelo modo
``--sem-llm`` e pelo fallback determinístico.
"""

import logging
import math
from typing import Any, Protocol

from domain.constantes import FAIXA_ALTO, FAIXA_MODERADO, FEATURES, LIMIAR_DECISAO
from domain.schemas import AvaliacaoRisco, Classificacao, DadosPaciente

logger = logging.getLogger("cardioia.services.risco")


class Preditor(Protocol):
    """Interface mínima usada aqui (o ``PreditorPicoRisco`` real ou um stub de teste)."""

    avisos: list[str]

    @property
    def versao(self) -> str: ...

    @property
    def faixas_treino(self) -> dict[str, Any]: ...

    def prever_probabilidade(self, paciente: DadosPaciente) -> float: ...


def classificar_risco(probabilidade: float) -> Classificacao:
    """Converte a probabilidade em faixa. ``ValueError`` se estiver fora de [0, 1]."""
    if math.isnan(probabilidade) or not 0.0 <= probabilidade <= 1.0:
        raise ValueError(f"probabilidade fora de [0, 1]: {probabilidade}")
    if probabilidade < FAIXA_MODERADO:
        return "BAIXO"
    if probabilidade < FAIXA_ALTO:
        return "MODERADO"
    return "ALTO"


def _avisos_extrapolacao(paciente: DadosPaciente, faixas: dict[str, Any]) -> list[str]:
    """Valores válidos, mas fora do intervalo visto no treino: aviso, não erro."""
    avisos = []
    for nome in FEATURES:
        if nome not in faixas:
            continue
        minimo, maximo = faixas[nome]
        valor = getattr(paciente, nome)
        if not minimo <= valor <= maximo:
            avisos.append(
                f"{nome}={valor:g} fora da faixa de treino [{minimo:.4g}, {maximo:.4g}]: "
                "a predição é uma extrapolação"
            )
    return avisos


def avaliar_risco(paciente: DadosPaciente, preditor: Preditor) -> AvaliacaoRisco:
    """Calcula probabilidade (4 casas), faixa, pico previsto e avisos.

    A classificação usa o valor já arredondado, para que a faixa exibida seja
    sempre coerente com a probabilidade exibida.
    """
    probabilidade = round(float(preditor.prever_probabilidade(paciente)), 4)
    avaliacao = AvaliacaoRisco(
        probabilidade=probabilidade,
        classificacao=classificar_risco(probabilidade),
        pico_risco_previsto=probabilidade >= LIMIAR_DECISAO,
        limiar_decisao=LIMIAR_DECISAO,
        modelo_versao=preditor.versao,
        avisos=_avisos_extrapolacao(paciente, preditor.faixas_treino)
        + list(preditor.avisos),
    )
    logger.info(
        "risco calculado: p=%.4f classificacao=%s",
        avaliacao.probabilidade,
        avaliacao.classificacao,
    )
    return avaliacao
