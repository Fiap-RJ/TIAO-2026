"""
Configurações centralizadas — CardioIA
========================================
Carrega as variáveis de ambiente uma única vez (.env) e expõe como um objeto
único, para que nenhum outro módulo chame `os.getenv` diretamente.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuração da aplicação, lida do `.env`."""

    WA_API_KEY: str = os.getenv("WA_API_KEY", "")
    WA_URL: str = os.getenv("WA_URL", "")
    WA_ASSISTANT_ID: str = os.getenv("WA_ASSISTANT_ID", "")
    WA_VERSION: str = "2021-06-14"

    FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "chave_padrao_caso_nao_encontre")

    @property
    def watson_configurado(self) -> bool:
        """True se as três credenciais do Watson estiverem presentes."""
        return bool(self.WA_API_KEY and self.WA_URL and self.WA_ASSISTANT_ID)


settings = Settings()
