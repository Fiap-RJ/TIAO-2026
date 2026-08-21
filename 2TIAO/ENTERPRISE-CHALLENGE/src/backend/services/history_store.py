"""
Serviço de Persistência de Histórico — Genera Intelligence
============================================================
Persiste as interações entre paciente e agente em SQLite, para alimentar a
tela de histórico do dashboard e os resumos de interações.

Nota de governança (ver document/governanca_e_riscos.md): a pergunta
armazenada já passou pelo nó de sanitização (remoção de PII) antes de
chegar aqui — ver agents/nodes/sanitize.py — mas o texto da resposta e o
conteúdo genético referenciado ainda são dados sensíveis (LGPD, Art. 5º,
II). O banco é local, não é versionado (ver .gitignore) e deve ser tratado
como dado sensível em qualquer ambiente real de produção.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

CURRENT_DIR = Path(__file__).parent
BACKEND_DIR = CURRENT_DIR.parent
DEFAULT_DB_PATH = BACKEND_DIR / "data" / "history.db"
DB_PATH = Path(os.getenv("GENERA_DB_PATH", str(DEFAULT_DB_PATH)))

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


@contextmanager
def _conectar():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def inicializar_banco() -> None:
    """Cria a tabela de histórico caso ainda não exista. Idempotente."""
    with _conectar() as conn:
        conn.executescript(_SCHEMA)


def salvar_interacao(paciente_id: str, pergunta: str, resposta: str, fontes: list[dict]) -> None:
    """Persiste uma interação pergunta/resposta do paciente com o agente."""
    inicializar_banco()
    with _conectar() as conn:
        conn.execute(
            "INSERT INTO interacoes (paciente_id, pergunta, resposta, fontes, criado_em) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                paciente_id,
                pergunta,
                resposta,
                json.dumps(fontes, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def listar_historico(paciente_id: str, limite: int = 100) -> list[dict]:
    """Retorna as interações do paciente, da mais antiga para a mais recente."""
    inicializar_banco()
    with _conectar() as conn:
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


def contar_interacoes(paciente_id: str) -> int:
    """Conta quantas interações o paciente já teve com o agente."""
    inicializar_banco()
    with _conectar() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) AS total FROM interacoes WHERE paciente_id = ?",
            (paciente_id,),
        )
        return cursor.fetchone()["total"]
