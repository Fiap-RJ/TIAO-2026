"""
Exceções de domínio — CardioIA Fase 6
=====================================

Exceções próprias da aplicação. Este módulo não importa o OpenAI Agents SDK
(``agents``): as camadas ``domain``, ``ml`` e ``services`` precisam continuar
utilizáveis sem LLM. O ``pipeline`` é quem traduz as exceções do SDK para
estas classes (ou as desembrulha, quando o SDK as envolve em ``UserError``).

Mapeamento para códigos de saída da CLI (ver ``main.py``):

- ``EntradaInvalidaError`` → 1 (entrada inválida)
- ``ConfiguracaoError`` e ``ModeloIndisponivelError`` → 2 (configuração/ambiente)
- ``EntradaBloqueadaError`` → 3 (bloqueado pelo guardrail de entrada)
- ``ErroFluxoAgentes`` → não chega à CLI: o pipeline aciona o fallback
"""


class CardioIAError(Exception):
    """Base de todas as exceções da aplicação."""


class ConfiguracaoError(CardioIAError):
    """Variável de ambiente inválida ou ausente no modo que a exige.

    A mensagem cita o nome da variável e o valor esperado, mas nunca o valor
    de ``OPENAI_API_KEY``.
    """


class ModeloIndisponivelError(CardioIAError):
    """Artefato do modelo ausente, corrompido ou incompatível com ``FEATURES``."""


class EntradaInvalidaError(CardioIAError):
    """Arquivo do paciente que não é um objeto JSON utilizável."""


class EntradaBloqueadaError(CardioIAError):
    """Mensagem bloqueada pelo guardrail de entrada (ex.: pedido de dose).

    O atributo ``motivo`` traz a explicação exibida ao usuário.
    """

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class ErroFluxoAgentes(CardioIAError):
    """Tool chamada fora da ordem prevista (pré-condição de contexto violada)."""
