"""
Schemas Pydantic — CardioIA Fase 6
==================================

Modelos de entrada, de resultados intermediários e de saída do atendimento.

- ``DadosPaciente``: entrada validada (faixas de plausibilidade, sem campos
  extras, sem NaN/infinito, sem booleanos) e com chaves normalizadas (A1).
- ``AvaliacaoRisco``, ``ProtocoloAcionado``, ``SinalAtencao`` e
  ``ResultadoProtocolos``: resultados calculados pelo código (``services``).
- ``NotaHandoff``: ``input_type`` dos handoffs entre especialistas.
- ``RecomendacaoFinal``: ``output_type`` do Planejador, gerado pelo LLM. Não tem
  defaults para que o JSON Schema seja estrito (structured outputs).
- ``RespostaAtendimento``: saída do pipeline, montada por código.
"""

import re
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from domain.constantes import AVISO_LEGAL, FEATURES, LIMIAR_DECISAO

Classificacao = Literal["BAIXO", "MODERADO", "ALTO"]
Origem = Literal["agentes", "fallback_deterministico", "sem_llm"]


def _normalizar_chave(chave: str) -> str:
    """Trim, minúsculas e espaços/hífens → ``_`` (``" FC-Media "`` → ``"fc_media"``)."""
    return re.sub(r"[\s\-]+", "_", chave.strip().lower())


class DadosPaciente(BaseModel):
    """Indicadores clínicos e operacionais de um paciente/unidade (entrada do modelo).

    As faixas são de plausibilidade, mais largas que as do treino: valores
    válidos fora de ``faixas_treino`` geram aviso (``AvaliacaoRisco.avisos``),
    não erro.
    """

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    idade_media: float = Field(..., ge=0, le=120, description="Idade média (anos)")
    carga_sistema: float = Field(..., ge=0, le=100, description="Carga do sistema (%)")
    tempo_espera: float = Field(..., ge=0, le=1440, description="Tempo de espera (min)")
    fc_media: float = Field(
        ..., ge=20, le=250, description="Frequência cardíaca média (bpm)"
    )
    spo2_media: float = Field(
        ..., ge=50, le=100, description="Saturação de O2 média (%)"
    )
    pa_sistolica: float = Field(
        ..., ge=40, le=300, description="Pressão arterial sistólica (mmHg)"
    )
    temperatura: float = Field(..., ge=0, le=45, description="Temperatura média (°C)")
    densidade_eventos: int = Field(
        ..., ge=0, le=100, description="Densidade de eventos"
    )
    eventos_24h: int = Field(..., ge=0, le=100, description="Eventos nas últimas 24 h")
    disponibilidade_recursos: float = Field(
        ..., ge=0, le=100, description="Disponibilidade de recursos (%)"
    )

    @model_validator(mode="before")
    @classmethod
    def normalizar_chaves(cls, dados: Any) -> Any:
        """Normaliza chaves (A1): trim, minúsculas, espaços/hífens → ``_``.

        Aceita, por exemplo, ``"disponibilidade recursos"`` (como no enunciado).
        Colisão (ex.: ``"disponibilidade recursos"`` e ``"disponibilidade_recursos"``
        no mesmo JSON) → ``ValueError``. Entrada que não é ``dict`` segue sem
        alteração e o Pydantic gera o erro de tipo.
        """
        if not isinstance(dados, dict):
            return dados
        normalizados: dict[Any, Any] = {}
        origem: dict[Any, Any] = {}
        for chave, valor in dados.items():
            nova = _normalizar_chave(chave) if isinstance(chave, str) else chave
            if nova in normalizados:
                raise ValueError(
                    f"chaves em colisão após normalização: {origem[nova]!r} e {chave!r} → {nova!r}"
                )
            normalizados[nova] = valor
            origem[nova] = chave
        return normalizados

    @field_validator("*", mode="before")
    @classmethod
    def rejeitar_booleanos(cls, valor: Any, info: ValidationInfo) -> Any:
        """``bool`` é subclasse de ``int`` em Python; o Pydantic lax o aceitaria como 0/1."""
        if isinstance(valor, bool):
            raise ValueError(
                f"{info.field_name}: valor booleano não é aceito; informe um número"
            )
        return valor

    def como_lista_ordenada(self) -> list[float]:
        """Valores na ordem canônica de ``FEATURES`` (a mesma do treino)."""
        return [float(getattr(self, nome)) for nome in FEATURES]


class AvaliacaoRisco(BaseModel):
    """Resultado do modelo preditivo para um paciente (calculado por código)."""

    probabilidade: float = Field(
        ..., ge=0, le=1, description="P(pico_risco=1), 4 casas"
    )
    classificacao: Classificacao = Field(
        ..., description="Faixa de risco: BAIXO, MODERADO ou ALTO"
    )
    pico_risco_previsto: bool = Field(..., description="probabilidade >= 0.5")
    limiar_decisao: float = Field(
        LIMIAR_DECISAO, description="Limiar de decisão do classificador"
    )
    modelo_versao: str = Field(
        ..., description="Versão do artefato (metadados do modelo)"
    )
    avisos: list[str] = Field(
        default_factory=list,
        description="Extrapolação das faixas de treino, versão de lib",
    )


class Protocolo(BaseModel):
    """Item da base simulada de protocolos (P01–P10, texto literal do enunciado)."""

    id: str = Field(..., description="Identificador: P01..P10")
    texto: str = Field(..., description="Texto literal do enunciado")
    variavel: str = Field(..., description="Feature avaliada ou 'classificacao_risco'")
    operador: Literal[">", "<", "=="] = Field(
        ..., description="Operador de comparação estrita"
    )
    limiar: float | str = Field(..., description="Limiar numérico ou 'ALTO' (P10)")


class ProtocoloAcionado(BaseModel):
    """Protocolo cujo gatilho foi atingido, com a justificativa da comparação."""

    id: str = Field(..., description="Identificador do protocolo")
    texto: str = Field(..., description="Texto literal do protocolo")
    variavel: str = Field(..., description="Variável avaliada")
    valor_observado: float | str = Field(
        ..., description="Valor do paciente ou a classificação"
    )
    limiar: float | str = Field(..., description="Limiar do protocolo")
    justificativa: str = Field(
        ..., description="Comparação que acionou, ex.: 'carga_sistema=92 > 85'"
    )


class SinalAtencao(BaseModel):
    """Feature acima do limiar de risco do alvo, mas abaixo do gatilho do protocolo (A3)."""

    variavel: str = Field(..., description="Feature observada")
    valor: float = Field(..., description="Valor do paciente")
    limiar_risco: float = Field(..., description="Limiar da regra de geração do alvo")
    limiar_protocolo: float = Field(
        ..., description="Limiar do protocolo correspondente"
    )
    protocolo_id: str = Field(..., description="Protocolo que aciona nessa variável")
    mensagem: str = Field(..., description="Descrição legível do sinal")


class ResultadoProtocolos(BaseModel):
    """Saída da seleção determinística de protocolos."""

    protocolos: list[ProtocoloAcionado] = Field(
        ..., description="Acionados, ordenados por id"
    )
    sinais_de_atencao: list[SinalAtencao] = Field(
        ..., description="Ordenados por FEATURES"
    )


class NotaHandoff(BaseModel):
    """Nota passada pelo agente de origem no handoff (``input_type``)."""

    resumo: str = Field(
        ...,
        max_length=300,
        description="Resumo do que foi feito e o que passar adiante",
    )


class RecomendacaoFinal(BaseModel):
    """Saída estruturada do Planejador de Resposta (gerada pelo LLM).

    Sem defaults e sem o aviso legal: o schema precisa ser estrito para
    structured outputs, e o aviso é invariante de código (acrescentado pelo
    pipeline).
    """

    probabilidade_prevista: float = Field(
        ...,
        ge=0,
        le=1,
        description="Probabilidade copiada exatamente do resumo do atendimento",
    )
    classificacao_risco: Classificacao = Field(
        ..., description="Classificação copiada exatamente do resumo do atendimento"
    )
    protocolos_sugeridos: list[Annotated[str, Field(pattern=r"^P(0[1-9]|10)$")]] = (
        Field(
            ...,
            max_length=10,
            description="IDs dos protocolos acionados, exatamente os do resumo",
        )
    )
    acoes_operacionais: list[Annotated[str, Field(max_length=300)]] = Field(
        ..., min_length=1, max_length=8, description="De 1 a 8 ações operacionais"
    )
    explicacao: str = Field(
        ..., max_length=1500, description="Explicação clara e informativa"
    )


class RespostaAtendimento(BaseModel):
    """Resposta final do pipeline, montada por código a partir do contexto."""

    atendimento_id: str = Field(
        ..., description="Identificador do atendimento (uuid4 hex)"
    )
    gerado_em: datetime = Field(..., description="Momento da geração (UTC)")
    paciente: DadosPaciente = Field(..., description="Entrada validada e normalizada")
    avaliacao_risco: AvaliacaoRisco = Field(..., description="Resultado do modelo")
    protocolos: list[ProtocoloAcionado] = Field(..., description="Protocolos acionados")
    sinais_de_atencao: list[SinalAtencao] = Field(..., description="Sinais de atenção")
    acoes_operacionais: list[str] = Field(
        ..., description="Ações operacionais sugeridas"
    )
    explicacao: str = Field(..., description="Explicação da recomendação")
    cadeia_agentes: list[str] = Field(..., description="Agentes que atuaram no turno")
    origem: Origem = Field(..., description="Quem redigiu a recomendação")
    violacoes_guardrail: list[str] = Field(
        default_factory=list, description="Violações detectadas pelo guardrail de saída"
    )
    # Exibido pela CLI como "ORIGEM: fallback_deterministico (motivo)".
    motivo_fallback: str | None = Field(
        None, description="Causa do fallback determinístico (None nas demais origens)"
    )
    aviso_legal: str = Field(
        AVISO_LEGAL, description="Aviso legal fixo, acrescentado por código"
    )
