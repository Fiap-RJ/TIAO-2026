from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Representa a pergunta enviada pelo paciente/usuário.
    """

    paciente_id: str = Field(
        ..., description="ID único do paciente para busca de contexto"
    )
    mensagem: str = Field(..., description="A dúvida ou pergunta em linguagem natural")


class FonteDado(BaseModel):
    """
    Representa o trecho do laudo genético que embasou a resposta da IA.
    Fundamental para evitar alucinações e garantir a rastreabilidade.
    """

    painel: str = Field(..., description="Nome do painel genético (ex: Genera Nutri)")
    marcador: str = Field(
        ...,
        description="O marcador ou característica analisada (ex: Sensibilidade à Cafeína)",
    )
    gene: str = Field(..., description="O gene associado à característica")
    conclusao_curta: str = Field(
        ..., description="A conclusão técnica resumida presente no laudo"
    )


class ChatResponse(BaseModel):
    """
    Estrutura final da resposta enviada ao Front-end.
    """

    resposta: str = Field(
        ..., description="Resposta em linguagem clara gerada pelo Agente de IA"
    )
    fontes: List[FonteDado] = Field(
        default_factory=list, description="Lista de referências técnicas do laudo"
    )


class NivelRisco(str, Enum):
    """Escala neutra de predisposição, usada no lugar de rótulos alarmistas."""

    BAIXO = "baixo"
    MODERADO = "moderado"
    ATENCAO = "atencao"


class ResultadoRisco(BaseModel):
    """Um resultado individual (característica) dentro de um painel genético."""

    caracteristica: str = Field(..., description="Característica avaliada (ex: Acne)")
    nivel: NivelRisco = Field(..., description="Nível de predisposição em escala neutra")
    categoria_original: str = Field(
        ..., description="Categoria de impacto conforme redigida no laudo original"
    )
    conclusao_curta: str = Field(..., description="Conclusão técnica resumida")
    explicacao_detalhada: str = Field(..., description="Explicação completa presente no laudo")
    recomendacoes: List[str] = Field(default_factory=list, description="Recomendações associadas")
    gene: str = Field(default="N/A", description="Gene associado à característica")


class PainelRisco(BaseModel):
    """Um painel genético (Nutri, Fit, Skin, Farma, Aging etc.) e seus resultados."""

    nome_painel: str = Field(..., description="Nome do painel genético")
    descricao: str = Field(default="", description="Descrição do painel")
    resultados: List[ResultadoRisco] = Field(default_factory=list)


class DoencaRisco(BaseModel):
    """Entrada da escala de risco poligênico para uma doença específica."""

    doenca: str = Field(..., description="Nome da doença avaliada")
    nivel: NivelRisco = Field(..., description="Nível de risco em escala neutra")
    risco_calculado_percentual: float = Field(..., description="Risco estimado em porcentagem")
    intervalo_minimo: float = Field(..., description="Limite inferior do intervalo de risco")
    intervalo_maximo: float = Field(..., description="Limite superior do intervalo de risco")
    classificacao_original: str = Field(
        ..., description="Classificação de risco conforme redigida no laudo original"
    )


class RiscosResponse(BaseModel):
    """Estrutura consumida pelo dashboard para os cards de risco."""

    paciente_id: str = Field(..., description="ID do paciente ao qual o relatório pertence")
    paineis: List[PainelRisco] = Field(default_factory=list)
    escala_risco_genetico: List[DoencaRisco] = Field(default_factory=list)


class ComposicaoAncestralidade(BaseModel):
    """Percentual estimado de uma região de ancestralidade."""

    regiao: str = Field(..., description="Região ou população de referência")
    percentual: float = Field(..., description="Percentual estimado de ancestralidade na região")


class AncestralidadeResponse(BaseModel):
    """Estrutura consumida pelo dashboard para o resumo de ancestralidade."""

    paciente_id: str = Field(..., description="ID do paciente ao qual o relatório pertence")
    composicao: List[ComposicaoAncestralidade] = Field(default_factory=list)
    observacao: str = Field(
        default="", description="Nota contextual sobre a natureza estatística da estimativa"
    )


class InteracaoHistorico(BaseModel):
    """Uma interação (pergunta + resposta) persistida entre o paciente e o agente."""

    id: int = Field(..., description="Identificador da interação")
    paciente_id: str = Field(..., description="ID do paciente")
    pergunta: str = Field(..., description="Pergunta feita pelo paciente (já sanitizada de PII)")
    resposta: str = Field(..., description="Resposta final do agente, já validada por guardrails")
    fontes: List[FonteDado] = Field(default_factory=list)
    criado_em: str = Field(..., description="Timestamp ISO 8601 (UTC) da interação")


class HistoricoResponse(BaseModel):
    """Estrutura consumida pela tela de histórico do dashboard."""

    paciente_id: str = Field(..., description="ID do paciente")
    interacoes: List[InteracaoHistorico] = Field(default_factory=list)


class ResumoRelatorioResponse(BaseModel):
    """Resumo executivo automático do relatório genético."""

    paciente_id: str = Field(..., description="ID do paciente")
    resumo: str = Field(..., description="Resumo executivo gerado a partir dos dados do laudo")
    gerado_em: str = Field(..., description="Timestamp ISO 8601 (UTC) de geração do resumo")


class ResumoInteracoesResponse(BaseModel):
    """Resumo automático do histórico de interações do paciente com o agente."""

    paciente_id: str = Field(..., description="ID do paciente")
    resumo: str = Field(..., description="Resumo das principais dúvidas discutidas até agora")
    quantidade_interacoes: int = Field(..., description="Total de interações consideradas")
    gerado_em: str = Field(..., description="Timestamp ISO 8601 (UTC) de geração do resumo")
