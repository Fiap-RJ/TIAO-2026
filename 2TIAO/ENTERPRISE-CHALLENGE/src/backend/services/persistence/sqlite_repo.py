"""
Implementação SQLite do repositório de histórico.
Usa sqlite3 padrão da stdlib.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from services.persistence.repo import HistoryRepository

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS interacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id TEXT NOT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    fontes TEXT NOT NULL DEFAULT '[]',
    criado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_interacoes_paciente ON interacoes (paciente_id, criado_em);
"""


class SQLiteHistoryRepository(HistoryRepository):
    """Repositório de histórico usando SQLite."""

    def __init__(self, db_path: str | Path):
        """Inicializa com o caminho do banco SQLite.

        Args:
            db_path: Caminho para o arquivo .db SQLite
        """
        self.db_path = Path(db_path)

    @contextmanager
    def _conectar(self):
        """Context manager para conexões SQLite com auto-commit e row factory."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def inicializar(self) -> None:
        """Cria a tabela de histórico caso ainda não exista. Idempotente."""
        with self._conectar() as conn:
            conn.executescript(_SCHEMA)
        logger.debug("SQLite database initialized at %s", self.db_path)

    def insert(
        self, paciente_id: str, pergunta: str, resposta: str, fontes: list[dict]
    ) -> None:
        """Persiste uma interação pergunta/resposta do paciente com o agente."""
        self.inicializar()
        with self._conectar() as conn:
            conn.execute(
                "INSERT INTO interacoes (paciente_id, pergunta, resposta, fontes, criado_em) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    paciente_id,
                    pergunta,
                    resposta,
                    json.dumps(fontes, ensure_ascii=False),
                    datetime.now(timezone.utc).isoformat(timespec="microseconds"),
                ),
            )

    def get_by_patient(self, paciente_id: str, limite: int = 100) -> list[dict]:
        """Retorna as interações do paciente, da mais antiga para a mais recente."""
        self.inicializar()
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT id, paciente_id, pergunta, resposta, fontes, criado_em "
                "FROM interacoes WHERE paciente_id = ? ORDER BY criado_em ASC LIMIT ?",
                (paciente_id, limite),
            )
            linhas = cursor.fetchall()

        return [
            {
                "id": linha["id"],
                "paciente_id": linha["paciente_id"],
                "pergunta": linha["pergunta"],
                "resposta": linha["resposta"],
                "fontes": json.loads(linha["fontes"]),
                "criado_em": linha["criado_em"],
            }
            for linha in linhas
        ]

    def count_by_patient(self, paciente_id: str) -> int:
        """Conta quantas interações o paciente já teve com o agente."""
        self.inicializar()
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM interacoes WHERE paciente_id = ?",
                (paciente_id,),
            )
            return cursor.fetchone()["total"]

    def delete_by_patient(self, paciente_id: str) -> bool:
        """Exclui todo o histórico de um paciente específico (Direito de Exclusão - LGPD)."""
        try:
            self.inicializar()
            with self._conectar() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM interacoes WHERE paciente_id = ?", (paciente_id,)
                )
                return cursor.rowcount > 0
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
            with self._conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM interacoes WHERE criado_em < ?", (corte,))
                return cursor.rowcount
        except Exception as e:
            logger.error("Erro ao purgar dados antigos do histórico: %s", e)
            return 0
