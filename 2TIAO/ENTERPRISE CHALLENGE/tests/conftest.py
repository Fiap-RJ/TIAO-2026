"""Fixtures compartilhadas para testes."""

import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def _historico_em_banco_temporario(tmp_path_factory):
    """Isola os testes de histórico/resumo num banco SQLite temporário, exclusivo da sessão."""
    from services import history_store

    db_path = tmp_path_factory.mktemp("data") / "history_test.db"
    history_store.DB_PATH = db_path
    os.environ["GENERA_DB_PATH"] = str(db_path)
    yield db_path
