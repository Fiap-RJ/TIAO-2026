"""
Factory do cliente Watson Assistant — CardioIA
=================================================
Instancia o SDK (AssistantV2) já autenticado e configurado, isolando o resto
da aplicação de detalhes do `ibm-watson`/`ibm-cloud-sdk-core`.
"""

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2

from core.config import settings


def build_assistant_client() -> AssistantV2:
    """Constrói o cliente autenticado do Watson Assistant a partir das settings."""
    authenticator = IAMAuthenticator(settings.WA_API_KEY)
    assistant = AssistantV2(version=settings.WA_VERSION, authenticator=authenticator)
    assistant.set_service_url(settings.WA_URL)
    return assistant


assistant = build_assistant_client()
