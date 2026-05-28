from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """
    Representa a pergunta enviada pelo paciente/usuário.
    """
    paciente_id: str = Field(..., description="ID único do paciente para busca de contexto")
    mensagem: str = Field(..., description="A dúvida ou pergunta em linguagem natural")


class FonteDado(BaseModel):
    """
    Representa o trecho do laudo genético que embasou a resposta da IA.
    Fundamental para evitar alucinações e garantir a rastreabilidade.
    """
    painel: str = Field(..., description="Nome do painel genético (ex: Genera Nutri)")
    marcador: str = Field(..., description="O marcador ou característica analisada (ex: Sensibilidade à Cafeína)")
    gene: str = Field(..., description="O gene associado à característica")
    conclusao_curta: str = Field(..., description="A conclusão técnica resumida presente no laudo")

class ChatResponse(BaseModel):
    """
    Estrutura final da resposta enviada ao Front-end.
    """
    resposta: str = Field(..., description="Resposta em linguagem clara gerada pelo Agente de IA")
    fontes: List[FonteDado] = Field(default_factory=list, description="Lista de referências técnicas do laudo")