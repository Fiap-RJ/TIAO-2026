"""
Interface abstrata para repositório de histórico.
Define o contrato que todas as implementações (SQLite, Postgres, etc.) devem cumprir.
"""

from abc import ABC, abstractmethod


class HistoryRepository(ABC):
    """Interface abstrata para persistência de interações do paciente."""

    @abstractmethod
    def inicializar(self) -> None:
        """Inicializa o banco de dados (cria tabelas, índices, etc.). Idempotente."""
        pass

    @abstractmethod
    def insert(
        self, paciente_id: str, pergunta: str, resposta: str, fontes: list[dict]
    ) -> None:
        """Persiste uma interação pergunta/resposta do paciente com o agente."""
        pass

    @abstractmethod
    def get_by_patient(
        self, paciente_id: str, limite: int = 100
    ) -> list[dict]:
        """Retorna as interações do paciente, da mais antiga para a mais recente."""
        pass

    @abstractmethod
    def delete_by_patient(self, paciente_id: str) -> bool:
        """Exclui todo o histórico de um paciente específico (Direito de Exclusão - LGPD)."""
        pass

    @abstractmethod
    def count_by_patient(self, paciente_id: str) -> int:
        """Conta quantas interações o paciente já teve com o agente."""
        pass

    @abstractmethod
    def apply_retention_policy(self, dias_retencao: int = 30) -> int:
        """Remove interações mais antigas que o período de retenção estabelecido."""
        pass
