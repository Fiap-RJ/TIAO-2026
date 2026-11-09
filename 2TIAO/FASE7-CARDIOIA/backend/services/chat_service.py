"""
Serviço de Chat Integrador — CardioIA Fase 7
============================================
Orquestra o chat de triagem conversacional com tripla camada de resiliência:
1. IBM Watson Assistant (Fase 5) com tratamento de sessão expirada (404).
2. OpenAI GPT (Fase 6) com guardrails de escopo (sem prescrição/dosagem).
3. Fallback Determinístico de Emergência (diretrizes clínicas SBC/SAMU 192).
"""

import logging
import os
import re
from typing import Optional

from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2
from openai import OpenAI

logger = logging.getLogger("cardioia.services.chat")

SESSAO_EXPIRADA = 404

# Regex de proteção clínica herdada dos guardrails da Fase 6
RE_PRESCRICAO = re.compile(
    r"\b(prescri[çc]|prescrever|dose|dosagem|posologia|rem[eé]dio|medicamento|mg|comprimido)\b",
    re.IGNORECASE,
)


class ChatIntegradorService:
    """Gerencia o atendimento conversacional mantendo o contrato FastAPI."""

    def __init__(self):
        self.wa_client: Optional[AssistantV2] = None
        self.wa_assistant_id: Optional[str] = os.getenv("WA_ASSISTANT_ID")
        self.openai_client: Optional[OpenAI] = None
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self._inicializar_watson()
        self._inicializar_openai()

    def _inicializar_watson(self):
        """Inicializa o SDK do Watson V2 com base nas credenciais de ambiente."""
        api_key = os.getenv("WA_API_KEY")
        url = os.getenv("WA_URL")
        version = os.getenv("WA_VERSION", "2021-06-14")

        if api_key and url and self.wa_assistant_id:
            try:
                auth = IAMAuthenticator(api_key)
                self.wa_client = AssistantV2(version=version, authenticator=auth)
                self.wa_client.set_service_url(url)
                logger.info("Cliente IBM Watson Assistant inicializado com sucesso.")
            except Exception as e:
                logger.error("Erro ao autenticar cliente IBM Watson: %s", e)
                self.wa_client = None

    def _inicializar_openai(self):
        """Inicializa o cliente OpenAI para reserva operacional."""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("Cliente OpenAI (reserva) inicializado com sucesso.")
            except Exception as e:
                logger.error("Erro ao autenticar cliente OpenAI: %s", e)
                self.openai_client = None

    # --- Métodos do Watson Assistant ---
    def _criar_sessao_watson(self) -> Optional[str]:
        """Gera um session_id limpo na nuvem da IBM."""
        try:
            res = self.wa_client.create_session(
                assistant_id=self.wa_assistant_id
            ).get_result()
            return res.get("session_id")
        except Exception as e:
            logger.warning("Falha ao gerar session_id no Watson: %s", e)
            return None

    def _extrair_texto_watson(self, resultado: dict) -> str:
        """Extrai as respostas de texto do nó de diálogo do Watson."""
        mensagens = resultado.get("output", {}).get("generic", [])
        textos = [
            m.get("text")
            for m in mensagens
            if m.get("response_type") == "text" and m.get("text")
        ]
        if textos:
            return " ".join(textos)
        return "Compreendi o relato. Pode me fornecer mais detalhes sobre o que está sentindo?"

    def _tentar_watson(self, mensagem: str, session_id: Optional[str]) -> Optional[dict]:
        """Envia mensagem ao Watson tratando expiração de sessão (404)."""
        if not self.wa_client or not self.wa_assistant_id:
            return None

        # Garante session_id ativo
        sid = session_id or self._criar_sessao_watson()
        if not sid:
            return None

        try:
            res = self.wa_client.message(
                assistant_id=self.wa_assistant_id,
                session_id=sid,
                input={"message_type": "text", "text": mensagem},
            ).get_result()
            return {
                "origem": "watson",
                "resposta": self._extrair_texto_watson(res),
                "session_id": sid,
            }
        except ApiException as erro:
            # Caso a sessão tenha expirado no Watson (código HTTP 404), recria uma nova
            if erro.code == SESSAO_EXPIRADA:
                logger.info("Sessão Watson expirada (404). Recriando sessão e reenviando...")
                sid = self._criar_sessao_watson()
                if sid:
                    try:
                        res = self.wa_client.message(
                            assistant_id=self.wa_assistant_id,
                            session_id=sid,
                            input={"message_type": "text", "text": mensagem},
                        ).get_result()
                        return {
                            "origem": "watson",
                            "resposta": self._extrair_texto_watson(res),
                            "session_id": sid,
                        }
                    except Exception as e:
                        logger.warning("Falha no reenvio ao Watson após recriar sessão: %s", e)
            else:
                logger.warning("Erro de API no Watson: %s", erro)
        except Exception as e:
            logger.warning("Watson indisponível ou falhou: %s", e)

        return None

    # --- Métodos de Fallback (OpenAI e Determinístico) ---
    def _tentar_openai(self, mensagem: str, session_id: Optional[str]) -> Optional[dict]:
        """Executa a triagem conversacional com modelo OpenAI caso o Watson falhe."""
        if not self.openai_client:
            return None

        # Validação de escopo inspirada no guardrail da Fase 6
        if RE_PRESCRICAO.search(mensagem):
            return {
                "origem": "openai_guardrail",
                "resposta": (
                    "O CardioIA é uma ferramenta de apoio informativo e não indica medicamentos, "
                    "prescrições ou dosagens. Para orientações farmacológicas, consulte um médico."
                ),
                "session_id": session_id,
            }

        try:
            instrucoes = (
                "Você é o assistente virtual de triagem cardiológica do CardioIA (projeto acadêmico FIAP). "
                "Escopo: informativo e de apoio à decisão operacional. "
                "Nunca faça diagnóstico definitivo nem receite medicamentos/doses. "
                "Responda sempre em português do Brasil com empatia e clareza, orientando a busca por "
                "atendimento presencial caso haja sinais de alerta (dor torácica, falta de ar severa, síncope)."
            )

            completion = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": instrucoes},
                    {"role": "user", "content": mensagem},
                ],
                max_tokens=300,
                temperature=0.3,
            )
            return {
                "origem": "openai_fallback",
                "resposta": completion.choices[0].message.content,
                "session_id": session_id,
            }
        except Exception as e:
            logger.warning("OpenAI falhou durante o fallback: %s", e)
            return None

    def _fallback_deterministico(self, session_id: Optional[str]) -> dict:
        """Garante resposta mesmo com todas as APIs cognitivas offline."""
        return {
            "origem": "fallback_deterministico",
            "resposta": (
                "Aviso do Sistema CardioIA: Nossos serviços de inteligência conversacional estão "
                "temporariamente indisponíveis. Se você ou alguém próximo estiver apresentando dor ou "
                "aperto no peito irradiando para os braços, falta de ar súbita, palpitações ou tontura extrema, "
                "dirija-se imediatamente à unidade de emergência cardiológica mais próxima ou acione o SAMU (192)."
            ),
            "session_id": session_id,
        }

    # --- Ponto de Entrada Principal ---
    def processar_mensagem(self, mensagem: str, session_id: Optional[str] = None) -> dict:
        """Orquestra a triagem: Watson -> Fallback OpenAI -> Fallback Determinístico."""
        # 1. Tenta Watson Assistant
        resposta = self._tentar_watson(mensagem, session_id)
        if resposta:
            return resposta

        # 2. Tenta OpenAI
        logger.info("Acionando fallback da OpenAI para a mensagem de triagem...")
        resposta = self._tentar_openai(mensagem, session_id)
        if resposta:
            return resposta

        # 3. Fallback Determinístico
        logger.warning("Acionando fallback determinístico de segurança clínica...")
        return self._fallback_deterministico(session_id)


# Instância única para consumo das rotas FastAPI
chat_service = ChatIntegradorService()