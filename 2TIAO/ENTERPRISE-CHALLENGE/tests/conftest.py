"""Fixtures compartilhadas para testes.

Testes herméticos: as chaves de LLM são zeradas em `os.environ` ANTES de qualquer
import do app. Variável de ambiente tem prioridade sobre o `.env` no
pydantic-settings (e `load_dotenv()` não sobrescreve variável já definida), então
nenhum teste usa a chave real do `src/backend/.env`. Para rodar o teste ponta a
ponta com credenciais reais, exporte `GENERA_E2E=1`.
"""

import os
import sqlite3
from pathlib import Path

if os.getenv("GENERA_E2E") != "1":
    os.environ["GOOGLE_API_KEY"] = ""
    os.environ["OPENAI_API_KEY"] = ""

import pytest  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _historico_em_banco_temporario(tmp_path_factory):
    """Isola os testes de histórico/resumo num banco SQLite temporário, exclusivo da sessão."""
    from services.persistence.factory import reset_repo

    db_path = tmp_path_factory.mktemp("data") / "history_test.db"
    os.environ["GENERA_DB_PATH"] = str(db_path)
    # Reset the repository factory to pick up the new DB path from env
    reset_repo()
    yield db_path
    # Cleanup
    reset_repo()


@pytest.fixture(autouse=True)
def _limpar_banco_entre_testes():
    """Limpa a tabela de histórico entre cada teste para evitar poluição de dados."""
    yield
    # Após cada teste, limpa interações
    from services.persistence.factory import get_history_repo
    from services.persistence.sqlite_repo import SQLiteHistoryRepository

    repo = get_history_repo()
    if isinstance(repo, SQLiteHistoryRepository):
        try:
            conn = sqlite3.connect(repo.db_path)
            conn.execute("DELETE FROM interacoes")
            conn.commit()
            conn.close()
        except Exception:
            pass  # Ignore errors during cleanup


