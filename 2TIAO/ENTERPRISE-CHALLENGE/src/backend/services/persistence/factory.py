"""
Factory para criar instâncias do repositório de histórico.
Seleciona a implementação (SQLite ou Postgres) baseado na configuração.
"""

import logging
from pathlib import Path

from core.config import settings
from services.persistence.postgres_repo import PostgresHistoryRepository
from services.persistence.repo import HistoryRepository
from services.persistence.sqlite_repo import SQLiteHistoryRepository

logger = logging.getLogger(__name__)

# Cache da instância singleton
_repo_instance: HistoryRepository | None = None


def get_history_repo() -> HistoryRepository:
    """Factory para obter a instância correta do repositório de histórico.

    Seleciona entre SQLite (padrão) e Postgres baseado em DB_TYPE.
    Levanta erro claro se Postgres foi solicitado mas psycopg2 não está instalado.

    Returns:
        HistoryRepository: Instância do repositório (singleton)

    Raises:
        ValueError: Se DB_TYPE for inválido ou DATABASE_URL vazio para Postgres
        ImportError: Se Postgres foi solicitado mas psycopg2 não está disponível
    """
    global _repo_instance

    if _repo_instance is not None:
        return _repo_instance

    db_type = settings.DB_TYPE.lower()

    if db_type == "sqlite":
        db_path = Path(settings.GENERA_DB_PATH)
        _repo_instance = SQLiteHistoryRepository(db_path)
        logger.info("Using SQLite repository at %s", db_path)

    elif db_type == "postgres":
        database_url = settings.DATABASE_URL.strip()
        if not database_url:
            raise ValueError(
                "DATABASE_URL must be set when DB_TYPE=postgres. "
                "Example: postgresql://user:password@localhost/genera"
            )
        try:
            _repo_instance = PostgresHistoryRepository(database_url)
            logger.info("Using Postgres repository")
        except ImportError as e:
            raise ImportError(
                "psycopg2-binary is required for Postgres support. "
                "Install with: pip install psycopg2-binary"
            ) from e

    else:
        raise ValueError(
            f"Invalid DB_TYPE={db_type!r}. Must be 'sqlite' or 'postgres'."
        )

    return _repo_instance


def reset_repo() -> None:
    """Reset the repository singleton (useful for testing)."""
    global _repo_instance
    _repo_instance = None
