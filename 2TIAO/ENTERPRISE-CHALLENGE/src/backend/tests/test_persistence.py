"""Tests for persistence layer (SQLite and Postgres repositories)."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.persistence.factory import get_history_repo, reset_repo
from services.persistence.postgres_repo import PostgresHistoryRepository
from services.persistence.repo import HistoryRepository
from services.persistence.sqlite_repo import SQLiteHistoryRepository


class TestSQLiteRepository:
    """Tests for SQLite implementation."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary SQLite database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield db_path

    @pytest.fixture
    def repo(self, temp_db):
        """Create a SQLite repository instance."""
        return SQLiteHistoryRepository(temp_db)

    def test_initialization(self, repo, temp_db):
        """Test that repository initializes and creates database."""
        repo.inicializar()
        assert temp_db.exists()

    def test_insert_and_retrieve(self, repo):
        """Test inserting and retrieving an interaction."""
        repo.inicializar()

        paciente_id = "pac_001"
        pergunta = "Qual é meu risco?"
        resposta = "Seu risco é baixo."
        fontes = [{"gene": "BRCA1", "painel": "Câncer"}]

        repo.insert(paciente_id, pergunta, resposta, fontes)

        result = repo.get_by_patient(paciente_id)
        assert len(result) == 1
        assert result[0]["pergunta"] == pergunta
        assert result[0]["resposta"] == resposta
        assert result[0]["fontes"] == fontes

    def test_count_by_patient(self, repo):
        """Test counting interactions by patient."""
        repo.inicializar()

        paciente_id = "pac_001"
        assert repo.count_by_patient(paciente_id) == 0

        repo.insert(paciente_id, "Q1", "A1", [])
        assert repo.count_by_patient(paciente_id) == 1

        repo.insert(paciente_id, "Q2", "A2", [])
        assert repo.count_by_patient(paciente_id) == 2

    def test_delete_by_patient(self, repo):
        """Test deleting all interactions for a patient."""
        repo.inicializar()

        paciente_id = "pac_001"
        repo.insert(paciente_id, "Q1", "A1", [])
        repo.insert(paciente_id, "Q2", "A2", [])

        assert repo.count_by_patient(paciente_id) == 2

        success = repo.delete_by_patient(paciente_id)
        assert success is True
        assert repo.count_by_patient(paciente_id) == 0

    def test_delete_nonexistent_patient(self, repo):
        """Test deleting history for non-existent patient returns False."""
        repo.inicializar()
        success = repo.delete_by_patient("pac_nonexistent")
        assert success is False

    def test_get_by_patient_with_limit(self, repo):
        """Test retrieving interactions with limit."""
        repo.inicializar()

        paciente_id = "pac_001"
        for i in range(5):
            repo.insert(paciente_id, f"Q{i}", f"A{i}", [])

        result = repo.get_by_patient(paciente_id, limite=2)
        assert len(result) == 2

    def test_apply_retention_policy(self, repo):
        """Test retention policy removes old records."""
        repo.inicializar()

        paciente_id = "pac_001"
        repo.insert(paciente_id, "Q1", "A1", [])

        # Default is 30 days, so recent record should not be deleted
        deleted = repo.apply_retention_policy(dias_retencao=30)
        assert deleted == 0

    def test_fontes_json_serialization(self, repo):
        """Test that fontes JSON is properly serialized and deserialized."""
        repo.inicializar()

        fontes = [
            {"gene": "BRCA1", "painel": "Câncer", "risco": "Alto"},
            {"gene": "TP53", "painel": "Tumor", "risco": "Médio"},
        ]

        repo.insert("pac_001", "Q", "A", fontes)
        result = repo.get_by_patient("pac_001")

        assert result[0]["fontes"] == fontes
        assert isinstance(result[0]["fontes"], list)
        assert all(isinstance(f, dict) for f in result[0]["fontes"])


class TestPostgresRepository:
    """Tests for Postgres implementation (mocked)."""

    @pytest.mark.requires_api_key
    def test_postgres_repo_requires_psycopg2(self):
        """Test that Postgres repo raises ImportError if psycopg2 is missing."""
        with patch("services.persistence.postgres_repo.psycopg2", side_effect=ImportError):
            with pytest.raises(ImportError, match="psycopg2-binary"):
                PostgresHistoryRepository("postgresql://localhost/test")

    @pytest.mark.requires_api_key
    def test_postgres_repo_initialization_with_url(self):
        """Test Postgres repo accepts connection string."""
        # Just test that it doesn't raise during init with valid URL format
        try:
            # This will fail at connection time but should pass init
            repo = PostgresHistoryRepository("postgresql://user:pass@localhost/test")
            assert repo.database_url == "postgresql://user:pass@localhost/test"
        except ImportError:
            # psycopg2 might not be installed in test env
            pytest.skip("psycopg2-binary not installed")

    @pytest.mark.requires_api_key
    def test_postgres_insert_mock(self):
        """Test Postgres insert with mocked connection."""
        try:
            repo = PostgresHistoryRepository("postgresql://localhost/test")
        except ImportError:
            pytest.skip("psycopg2-binary not installed")

        # Mock the connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        repo._conn = mock_conn

        repo.insert("pac_001", "Q", "A", [])

        # Verify cursor.execute was called
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()


class TestFactory:
    """Tests for repository factory."""

    def setup_method(self):
        """Reset factory before each test."""
        reset_repo()

    def teardown_method(self):
        """Reset factory after each test."""
        reset_repo()

    def test_factory_returns_sqlite_by_default(self):
        """Test that factory returns SQLite repo by default."""
        with patch("services.persistence.factory.settings") as mock_settings:
            mock_settings.DB_TYPE = "sqlite"
            mock_settings.GENERA_DB_PATH = "/tmp/test.db"

            repo = get_history_repo()
            assert isinstance(repo, SQLiteHistoryRepository)

    def test_factory_returns_postgres_when_configured(self):
        """Test that factory returns Postgres repo when DB_TYPE=postgres."""
        with patch("services.persistence.factory.settings") as mock_settings:
            mock_settings.DB_TYPE = "postgres"
            mock_settings.DATABASE_URL = "postgresql://localhost/test"

            try:
                repo = get_history_repo()
                assert isinstance(repo, PostgresHistoryRepository)
            except ImportError:
                pytest.skip("psycopg2-binary not installed")

    def test_factory_raises_on_invalid_db_type(self):
        """Test that factory raises error for invalid DB_TYPE."""
        with patch("services.persistence.factory.settings") as mock_settings:
            mock_settings.DB_TYPE = "invalid"

            with pytest.raises(ValueError, match="Invalid DB_TYPE"):
                reset_repo()
                get_history_repo()

    def test_factory_raises_on_postgres_without_url(self):
        """Test that factory raises error if Postgres chosen but no DATABASE_URL."""
        with patch("services.persistence.factory.settings") as mock_settings:
            mock_settings.DB_TYPE = "postgres"
            mock_settings.DATABASE_URL = ""

            with pytest.raises(ValueError, match="DATABASE_URL must be set"):
                reset_repo()
                get_history_repo()

    def test_factory_singleton(self):
        """Test that factory returns same instance on multiple calls."""
        with patch("services.persistence.factory.settings") as mock_settings:
            mock_settings.DB_TYPE = "sqlite"
            mock_settings.GENERA_DB_PATH = "/tmp/test.db"

            repo1 = get_history_repo()
            repo2 = get_history_repo()

            assert repo1 is repo2


class TestBackwardCompatibility:
    """Tests for backward compatibility of history_store module."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary SQLite database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield db_path

    def test_history_store_functions_still_work(self, temp_db):
        """Test that history_store module functions work via factory."""
        from services import history_store

        with patch("services.history_store.get_history_repo") as mock_factory:
            mock_repo = MagicMock(spec=HistoryRepository)
            mock_factory.return_value = mock_repo

            # Test all exported functions
            history_store.inicializar_banco()
            mock_repo.inicializar.assert_called_once()

            mock_repo.reset_mock()
            history_store.salvar_interacao("pac_001", "Q", "A", [])
            mock_repo.insert.assert_called_once_with("pac_001", "Q", "A", [])

            mock_repo.reset_mock()
            mock_repo.get_by_patient.return_value = []
            history_store.listar_historico("pac_001", limite=50)
            mock_repo.get_by_patient.assert_called_once_with("pac_001", 50)

            mock_repo.reset_mock()
            mock_repo.count_by_patient.return_value = 5
            history_store.contar_interacoes("pac_001")
            mock_repo.count_by_patient.assert_called_once_with("pac_001")

            mock_repo.reset_mock()
            history_store.excluir_historico_paciente("pac_001")
            mock_repo.delete_by_patient.assert_called_once_with("pac_001")

            mock_repo.reset_mock()
            history_store.aplicar_regra_retencao(dias_retencao=30)
            mock_repo.apply_retention_policy.assert_called_once_with(30)
