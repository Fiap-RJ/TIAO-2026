"""
Serviço de Conversação — CardioIA
====================================
Gerencia a sessão do Watson Assistant por conversa (reaproveitada entre
mensagens via cookie do Flask) e o envio de mensagens, incluindo a
recriação automática da sessão quando ela expira.
"""

from flask import session
from ibm_cloud_sdk_core.api_exception import ApiException

from core.config import settings
from services.watson_client import assistant

SESSAO_EXPIRADA = 404


def criar_nova_sessao() -> str:
    """Cria uma sessão nova no Watson e a guarda na sessão Flask (cookie assinado)."""
    nova = assistant.create_session(assistant_id=settings.WA_ASSISTANT_ID).get_result()
    session["watson_session_id"] = nova["session_id"]
    return nova["session_id"]


def obter_sessao_atual() -> str:
    """Reaproveita a sessão do Watson entre mensagens da mesma conversa, criando uma
    nova apenas se ainda não existir. Preserva o contexto do diálogo entre turnos."""
    session_id = session.get("watson_session_id")
    if session_id:
        return session_id
    return criar_nova_sessao()


def extrair_texto_resposta(resultado_watson: dict) -> str:
    """Extrai o primeiro texto de resposta do Watson, com fallback defensivo."""
    generic = resultado_watson.get("output", {}).get("generic", [])
    for item in generic:
        if item.get("response_type") == "text" and item.get("text"):
            return item["text"]
    return "Desculpe, não entendi sua mensagem. Você pode reformular?"


def _enviar(session_id: str, mensagem: str) -> dict:
    return assistant.message(
        assistant_id=settings.WA_ASSISTANT_ID,
        session_id=session_id,
        input={"message_type": "text", "text": mensagem},
    ).get_result()


def enviar_mensagem(mensagem: str) -> str:
    """Envia a mensagem do paciente ao Watson e retorna o texto de resposta.

    Reaproveita a sessão da conversa; se ela tiver expirado (Watson responde 404
    "Invalid Session" após alguns minutos de inatividade), recria a sessão e
    tenta reenviar a mensagem uma única vez antes de desistir.
    """
    session_id = obter_sessao_atual()

    try:
        resultado = _enviar(session_id, mensagem)
    except ApiException as erro:
        if erro.code != SESSAO_EXPIRADA:
            raise
        session_id = criar_nova_sessao()
        resultado = _enviar(session_id, mensagem)

    return extrair_texto_resposta(resultado)
