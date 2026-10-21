"""
Testes de ``core.config``
=========================

Parse preguiçoso das variáveis de ambiente e ``ConfiguracaoError`` com o nome
da variável. Usa a fixture ``settings_limpas``.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from core.config import RAIZ_FASE, obter_settings
from core.erros import ConfiguracaoError

CHAVE_FALSA = "chave-de-teste-que-nao-pode-vazar-123"


def test_padroes_sem_variaveis(settings_limpas):
    settings = obter_settings()
    assert settings.OPENAI_MODEL == "gpt-4.1-mini"
    assert settings.OPENAI_TEMPERATURE == 0.0
    assert settings.MAX_TURNS == 12
    assert settings.MODELO_PATH == RAIZ_FASE / "models" / "modelo_pico_risco.joblib"
    assert settings.metadados_path.name == "modelo_pico_risco.metadata.json"
    assert settings.SESSIONS_DB_PATH == RAIZ_FASE / "data" / "sessoes.db"
    assert settings.TRACING_HABILITADO is False
    assert settings.LOG_LEVEL == "INFO"
    assert settings.openai_configurado is False


@pytest.mark.parametrize(
    ("variavel", "valor"),
    [
        ("MAX_TURNS", "abc"),
        ("MAX_TURNS", "0"),
        ("TRACING_HABILITADO", "talvez"),
        ("OPENAI_TEMPERATURE", "quente"),
        ("OPENAI_TEMPERATURE", "3"),
        ("LOG_LEVEL", "verboso"),
    ],
)
def test_valor_invalido_gera_configuracao_error(settings_limpas, variavel, valor):
    settings_limpas.setenv(variavel, valor)
    with pytest.raises(ConfiguracaoError) as exc:
        obter_settings()
    assert variavel in str(exc.value)


def test_import_com_env_invalido_nao_levanta():
    """O parse é preguiçoso: importar o módulo não lê o ambiente."""
    raiz_src = Path(__file__).resolve().parents[1] / "src"
    resultado = subprocess.run(
        [sys.executable, "-c", "import core.config"],
        cwd=raiz_src,
        env={"MAX_TURNS": "abc", "PATH": ""},
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr


def test_temperatura_vazia_vira_none(settings_limpas):
    settings_limpas.setenv("OPENAI_TEMPERATURE", "")
    assert obter_settings().OPENAI_TEMPERATURE is None


@pytest.mark.parametrize(
    ("bruto", "esperado"), [("sim", True), ("TRUE", True), ("0", False)]
)
def test_bool_aceita_variacoes(settings_limpas, bruto, esperado):
    settings_limpas.setenv("TRACING_HABILITADO", bruto)
    assert obter_settings().TRACING_HABILITADO is esperado


def test_caminho_relativo_resolvido_contra_raiz(settings_limpas):
    settings_limpas.setenv("MODELO_PATH", "outro/modelo.joblib")
    assert obter_settings().MODELO_PATH == RAIZ_FASE / "outro" / "modelo.joblib"


def test_chave_configurada_nao_aparece_em_mensagens(settings_limpas):
    settings_limpas.setenv("OPENAI_API_KEY", CHAVE_FALSA)
    settings = obter_settings()
    assert settings.openai_configurado is True
    assert CHAVE_FALSA not in repr(settings)

    obter_settings.cache_clear()
    settings_limpas.setenv("MAX_TURNS", "abc")
    with pytest.raises(ConfiguracaoError) as exc:
        obter_settings()
    assert CHAVE_FALSA not in str(exc.value)


def test_obter_settings_e_cacheado(settings_limpas):
    assert obter_settings() is obter_settings()
