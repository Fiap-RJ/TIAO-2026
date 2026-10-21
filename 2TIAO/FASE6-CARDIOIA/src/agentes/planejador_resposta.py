"""
Agente Planejador de Resposta — CardioIA Fase 6
===============================================

Lê o resumo do atendimento (``obter_resumo_atendimento``), copia exatamente
probabilidade, classificação e IDs dos protocolos e redige ações operacionais
e explicação. A saída é estruturada (``output_type=RecomendacaoFinal``) e
conferida pelo ``output_guardrail`` ``validar_recomendacao_final``.

``tool_choice="required"`` com ``reset_tool_choice=True`` (padrão): obriga a
ler o resumo e depois libera a resposta final. Também responde às perguntas
de acompanhamento do modo interativo.
"""

from agents import Agent

from agentes.guardrails import validar_recomendacao_final
from agentes.instrucoes import montar_instrucoes, montar_model_settings
from agentes.tools import listar_base_protocolos, obter_resumo_atendimento
from core.config import Settings
from domain.schemas import RecomendacaoFinal

NOME = "Planejador de Resposta"
DESCRICAO_HANDOFF = "Consolida risco e protocolos em ações operacionais e responde perguntas de acompanhamento."

INSTRUCOES = """
Você é o Planejador de Resposta do CardioIA.
1. Chame a tool `obter_resumo_atendimento` antes de responder. Se precisar explicar por que um
   protocolo não foi acionado, consulte também `listar_base_protocolos`.
2. Preencha a recomendação final copiando EXATAMENTE do resumo:
   - `probabilidade_prevista` = avaliacao_risco.probabilidade;
   - `classificacao_risco` = avaliacao_risco.classificacao;
   - `protocolos_sugeridos` = os IDs de protocolos_acionados, todos e somente eles, sem repetir.
3. Em `acoes_operacionais`, escreva de 1 a 8 ações operacionais curtas (até 300 caracteres cada),
   derivadas dos protocolos acionados e dos sinais de atenção (ex.: abrir unidades temporárias,
   redistribuir insumos, acompanhar uma variável). Ações de gestão da unidade, não clínicas.
4. Em `explicacao` (até 1500 caracteres), explique de forma clara o risco, os protocolos e os
   sinais de atenção, citando os valores e limiares exatos do resumo. Se a última mensagem do
   usuário for uma pergunta de acompanhamento, responda a ela em `explicacao`, usando o resumo
   e o histórico da conversa, e mantenha os demais campos iguais aos do resumo.
Proibido: diagnóstico, indicação de medicamento ou tratamento.
Nunca use as palavras prescrição, prescrever, dose, dosagem ou posologia, nem para negar.
O aviso legal é adicionado pelo sistema.
"""


def criar_planejador_resposta(settings: Settings) -> Agent:
    """Fábrica do Planejador (agente final do fluxo; sem handoffs)."""
    return Agent(
        name=NOME,
        handoff_description=DESCRICAO_HANDOFF,
        instructions=montar_instrucoes(INSTRUCOES),
        model=settings.OPENAI_MODEL,
        model_settings=montar_model_settings(settings, tool_choice="required"),
        tools=[obter_resumo_atendimento, listar_base_protocolos],
        output_type=RecomendacaoFinal,
        output_guardrails=[validar_recomendacao_final],
    )
