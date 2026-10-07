"""
Implementação Postgres do repositório de histórico.
Usa psycopg2 (conexão via DATABASE_URL).
"""

import json
import logging
from datetime import datetime, timedelta, timezone

from services.persistence.repo import HistoryRepository

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS interacoes (
    id SERIAL PRIMARY KEY,
    paciente_id TEXT NOT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    fontes JSONB NOT NULL DEFAULT '[]'::jsonb,
    criado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_interacoes_paciente ON interacoes (paciente_id, criado_em);
"""


class PostgresHistoryRepository(HistoryRepository):
    """Repositório de histórico usando Postgres."""

    def __init__(self, database_url: str):
        """Inicializa com a connection string do Postgres.

        Args:
            database_url: URL de conexão ao Postgres (ex: postgresql://user:pass@host/db)

        Raises:
            ImportError: Se psycopg2 não estiver instalado
        """
        try:
            import psycopg2  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "psycopg2-binary is required for Postgres support. "
                "Install it with: pip install psycopg2-binary"
            ) from e

        self.database_url = database_url
        self._conn = None

    def _get_connection(self):
        """Obtém ou cria uma conexão com o Postgres."""
        import psycopg2

        try:
            if self._conn is None or self._conn.closed:
                self._conn = psycopg2.connect(self.database_url)
            return self._conn
        except Exception as e:
            logger.error("Erro ao conectar ao Postgres: %s", e)
            raise

    def inicializar(self) -> None:
        """Cria a tabela de histórico caso ainda não exista. Idempotente."""
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(_SCHEMA)
            conn.commit()
            logger.debug("Postgres database initialized")
        except Exception as e:
            logger.error("Erro ao inicializar banco Postgres: %s", e)
            raise

    def insert(
        self, paciente_id: str, pergunta: str, resposta: str, fontes: list[dict]
    ) -> None:
        """Persiste uma interação pergunta/resposta do paciente com o agente."""
        self.inicializar()
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO interacoes (paciente_id, pergunta, resposta, fontes, criado_em) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (
                        paciente_id,
                        pergunta,
                        resposta,
                        json.dumps(fontes, ensure_ascii=False),
                        datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                    ),
                )
            conn.commit()
        except Exception as e:
            logger.error("Erro ao inserir interação: %s", e)
            raise

    def get_by_patient(self, paciente_id: str, limite: int = 100) -> list[dict]:
        """Retorna as interações do paciente, da mais antiga para a mais recente."""
        self.inicializar()
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, paciente_id, pergunta, resposta, fontes, criado_em "
                    "FROM interacoes WHERE paciente_id = %s ORDER BY criado_em ASC LIMIT %s",
                    (paciente_id, limite),
                )
                linhas = cursor.fetchall()

            # Mapeia os resultados para dicts (psycopg2 retorna tuplas por padrão)
            return [
                {
                    "id": linha[0],
                    "paciente_id": linha[1],
                    "pergunta": linha[2],
                    "resposta": linha[3],
                    "fontes": json.loads(linha[4]) if isinstance(linha[4], str) else linha[4],
                    "criado_em": linha[5],
                }
                for linha in linhas
            ]
        except Exception as e:
            logger.error("Erro ao recuperar histórico: %s", e)
            raise

    def count_by_patient(self, paciente_id: str) -> int:
        """Conta quantas interações o paciente já teve com o agente."""
        self.inicializar()
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM interacoes WHERE paciente_id = %s",
                    (paciente_id,),
                )
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error("Erro ao contar interações: %s", e)
            raise

    def delete_by_patient(self, paciente_id: str) -> bool:
        """Exclui todo o histórico de um paciente específico (Direito de Exclusão - LGPD)."""
        try:
            self.inicializar()
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM interacoes WHERE paciente_id = %s", (paciente_id,))
                rowcount = cursor.rowcount
            conn.commit()
            return rowcount > 0
        except Exception as e:
            logger.error("Erro ao excluir histórico do paciente %s: %s", paciente_id, e)
            return False

    def apply_retention_policy(self, dias_retencao: int = 30) -> int:
        """Remove interações mais antigas que o período de retenção estabelecido."""
        corte = (
            datetime.now(timezone.utc) - timedelta(days=dias_retencao)
        ).isoformat(timespec="microseconds")
        try:
            self.inicializar()
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM interacoes WHERE criado_em < %s", (corte,))
                rowcount = cursor.rowcount
            conn.commit()
            return rowcount
        except Exception as e:
            logger.error("Erro ao purgar dados antigos do histórico: %s", e)
            return 0
