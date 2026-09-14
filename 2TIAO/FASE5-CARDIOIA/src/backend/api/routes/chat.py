"""Rota de chat — interface entre o front-end e o Watson Assistant."""

import logging

from flask import Blueprint, jsonify, request
from ibm_cloud_sdk_core.api_exception import ApiException

from core.config import settings
from services.watson_conversation import enviar_mensagem

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """Recebe a mensagem do paciente e retorna a resposta do Watson Assistant."""
    if not settings.watson_configurado:
        return jsonify({
            "response": "⚠️ O assistente não está configurado (credenciais do Watson ausentes)."
        }), 503

    dados = request.get_json(silent=True) or {}
    mensagem = (dados.get("message") or "").strip()

    if not mensagem:
        return jsonify({"response": "Por favor, digite uma mensagem."}), 400

    try:
        resposta = enviar_mensagem(mensagem)
    except ApiException as erro:
        logger.warning("Erro do Watson: %s", erro.message)
        return jsonify({"response": f"⚠️ Erro ao falar com o Watson: {erro.message}"}), 502
    except Exception:
        logger.exception("Falha inesperada ao falar com o Watson")
        return jsonify({
            "response": "⚠️ Não foi possível falar com o assistente agora. Tente novamente em instantes."
        }), 502

    return jsonify({"response": resposta})
