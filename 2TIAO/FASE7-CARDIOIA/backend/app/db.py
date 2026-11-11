"""Persistência SQLite e dados de demonstração."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .config import DATABASE_PATH
from .security import hash_password


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def initialize() -> None:
    with connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, nome TEXT NOT NULL, email TEXT UNIQUE NOT NULL, senha_hash TEXT NOT NULL, salt TEXT NOT NULL, perfil TEXT NOT NULL, paciente_id TEXT);
        CREATE TABLE IF NOT EXISTS pacientes (id TEXT PRIMARY KEY, nome TEXT NOT NULL, idade INTEGER NOT NULL, leito TEXT NOT NULL, indicadores_json TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS leituras (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_id TEXT NOT NULL, temperatura REAL NOT NULL, fc REAL NOT NULL, spo2 REAL NOT NULL, estado TEXT NOT NULL, ts TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS avaliacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, paciente_id TEXT NOT NULL, resultado_json TEXT NOT NULL, gerado_em TEXT NOT NULL);
        """)
        if conn.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]:
            return
        pacientes = [
            ("p-001", "João Batista", 62, "UTI-C 04", {"carga_sistema": 76, "tempo_espera": 38, "pa_sistolica": 138, "densidade_eventos": 3, "eventos_24h": 4, "disponibilidade_recursos": 54}),
            ("p-002", "Maria Aparecida", 57, "UTI-C 07", {"carga_sistema": 42, "tempo_espera": 18, "pa_sistolica": 124, "densidade_eventos": 1, "eventos_24h": 1, "disponibilidade_recursos": 77}),
        ]
        conn.executemany("INSERT INTO pacientes VALUES (?, ?, ?, ?, ?)", [(a, b, c, d, json.dumps(e)) for a, b, c, d, e in pacientes])
        usuarios = [("u-medico", "Dra. Helena Prado", "medico@cardioia.com", "medico", None), ("u-paciente", "João Batista", "paciente@cardioia.com", "paciente", "p-001")]
        for usuario_id, nome, email, perfil, paciente_id in usuarios:
            salt = f"cardioia-{usuario_id}"
            conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (usuario_id, nome, email, hash_password("cardioia", salt), salt, perfil, paciente_id))


def user_by_email(email: str):
    with connection() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()


def patients_for(usuario: dict):
    with connection() as conn:
        query, args = ("SELECT * FROM pacientes", ()) if usuario["perfil"] == "medico" else ("SELECT * FROM pacientes WHERE id = ?", (usuario["paciente_id"],))
        return conn.execute(query, args).fetchall()


def patient_by_id(paciente_id: str):
    with connection() as conn:
        return conn.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,)).fetchone()


def add_reading(payload: dict) -> None:
    with connection() as conn:
        conn.execute("INSERT INTO leituras (paciente_id, temperatura, fc, spo2, estado, ts) VALUES (?, ?, ?, ?, ?, ?)", (payload["paciente_id"], payload["temperatura"], payload["fc"], payload["spo2"], payload["estado"], payload["ts"]))


def readings(paciente_id: str, limit: int = 60):
    with connection() as conn:
        rows = conn.execute("SELECT temperatura, fc, spo2, estado, ts FROM leituras WHERE paciente_id = ? ORDER BY id DESC LIMIT ?", (paciente_id, limit)).fetchall()
    return list(reversed(rows))


def save_assessment(paciente_id: str, resultado: dict) -> None:
    with connection() as conn:
        conn.execute("INSERT INTO avaliacoes (paciente_id, resultado_json, gerado_em) VALUES (?, ?, ?)", (paciente_id, json.dumps(resultado, default=str), resultado["gerado_em"]))


def latest_assessment(paciente_id: str):
    with connection() as conn:
        row = conn.execute("SELECT resultado_json FROM avaliacoes WHERE paciente_id = ? ORDER BY id DESC LIMIT 1", (paciente_id,)).fetchone()
    return json.loads(row["resultado_json"]) if row else None
