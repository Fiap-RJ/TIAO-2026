"""Fixtures compartilhadas para testes.

Testes herméticos: as chaves de LLM são zeradas em `os.environ` ANTES de qualquer
import do app. Variável de ambiente tem prioridade sobre o `.env` no
pydantic-settings (e `load_dotenv()` não sobrescreve variável já definida), então
nenhum teste usa a chave real do `src/backend/.env`. Para rodar o teste ponta a
ponta com credenciais reais, exporte `GENERA_E2E=1`.
"""

import os

if os.getenv("GENERA_E2E") != "1":
    os.environ["GOOGLE_API_KEY"] = ""
    os.environ["OPENAI_API_KEY"] = ""

import pytest  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _historico_em_banco_temporario(tmp_path_factory):
    """Isola os testes de histórico/resumo num banco SQLite temporário, exclusivo da sessão."""
    from services import history_store

    db_path = tmp_path_factory.mktemp("data") / "history_test.db"
    history_store.DB_PATH = db_path
    os.environ["GENERA_DB_PATH"] = str(db_path)
    yield db_path
