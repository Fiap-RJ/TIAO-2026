"""
Configuração de logging — CardioIA Fase 6
=========================================

Centraliza o formato de log no padrão da Fase 5
(``data | nível | logger | mensagem``). Os módulos da aplicação usam loggers
``cardioia.<módulo>``. O logger do SDK (``openai.agents``) fica em WARNING
para não poluir a saída com o detalhe interno de cada chamada ao LLM.

Nunca registre a chave da OpenAI nem o prompt completo.
"""

import logging

FORMATO_LOG = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configurar_logging(nivel: str = "INFO") -> None:
    """Configura o logging raiz no nível informado (ex.: ``"INFO"``, ``"DEBUG"``).

    ``force=True`` permite reconfigurar o nível em execuções sucessivas no
    mesmo processo (testes e modo interativo).
    """
    logging.basicConfig(level=nivel.upper(), format=FORMATO_LOG, force=True)
    # O SDK é verboso em INFO; só avisos e erros dele interessam ao operador.
    logging.getLogger("openai.agents").setLevel(logging.WARNING)
