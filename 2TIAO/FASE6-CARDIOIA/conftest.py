"""
Fixtures compartilhadas
=======================

Este ``conftest.py`` fica na raiz da fase e atende ``tests/`` (não há
``tests/conftest.py``). O ``pythonpath = src`` do
``pytest.ini`` é aplicado antes da carga deste arquivo, então os pacotes da
aplicação podem ser importados. Os imports ficam dentro das fixtures para que
a coleta não dependa do artefato do modelo nem do SDK.

Fixtures:

- ``novo_caso_dict`` / ``novo_caso``: o paciente do enunciado (dict original e
  ``DadosPaciente``);
- ``settings_limpas``: ambiente de configuração controlado, sem chave;
- ``contexto``: ``ContextoAtendimento`` com o preditor real (``skip`` se o
  artefato estiver ausente);
- ``contexto_falso`` / ``criar_contexto_falso``: contexto com preditor stub de
  probabilidade fixa, para testes que não dependem do artefato.
"""

import json
from pathlib import Path

import pytest

RAIZ_FASE = Path(__file__).resolve().parent
CAMINHO_NOVO_CASO = RAIZ_FASE / "data" / "novo_caso.json"
CAMINHO_MODELO = RAIZ_FASE / "models" / "modelo_pico_risco.joblib"

# Variáveis lidas por core.config.Settings (zeradas pela fixture settings_limpas).
VARIAVEIS_CONFIG = (
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_TEMPERATURE",
    "MAX_TURNS",
    "MODELO_PATH",
    "SESSIONS_DB_PATH",
    "TRACING_HABILITADO",
    "LOG_LEVEL",
)


class PreditorFalso:
    """Stub do ``PreditorPicoRisco`` com probabilidade fixa (sem artefato)."""

    def __init__(self, probabilidade: float = 0.99) -> None:
        self.probabilidade = probabilidade
        self.avisos: list[str] = []
        self.versao = "stub-teste"
        self.faixas_treino: dict = {}
        self.metadados = {"versao": self.versao}
        self.sha256 = "0" * 64
        self.chamadas = 0

    def prever_probabilidade(self, paciente) -> float:
        self.chamadas += 1
        return self.probabilidade

    def prever_lote(self, pacientes) -> list[float]:
        self.chamadas += 1
        return [self.probabilidade] * len(pacientes)


def _limpar_caches() -> None:
    """Esquece configuração, preditor e inicialização do SDK já feitos no processo."""
    import pipeline
    from core.config import obter_settings
    from ml.preditor import obter_preditor

    obter_settings.cache_clear()
    obter_preditor.cache_clear()
    pipeline._reiniciar_sdk_para_testes()


@pytest.fixture
def settings_limpas(monkeypatch, tmp_path):
    """Ambiente de configuração controlado, sem chave da OpenAI.

    - remove as variáveis de configuração herdadas do shell;
    - aponta o ``.env`` para um arquivo inexistente, para que um ``src/.env``
      local não interfira;
    - define ``OPENAI_API_KEY=""`` (simula "sem chave");
    - limpa os caches de ``obter_settings()`` e ``obter_preditor()`` e a flag
      de ``inicializar_sdk`` antes e depois do teste.

    Devolve o ``monkeypatch``: o teste ajusta o ambiente com ``setenv`` antes
    de chamar ``obter_settings()``.
    """
    import core.config

    for nome in VARIAVEIS_CONFIG:
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.setattr(core.config, "CAMINHO_ENV", tmp_path / "inexistente.env")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    _limpar_caches()
    yield monkeypatch
    _limpar_caches()


@pytest.fixture
def novo_caso_dict() -> dict:
    """``novo_caso`` do enunciado, com a chave original ``"disponibilidade recursos"``."""
    with CAMINHO_NOVO_CASO.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


@pytest.fixture
def novo_caso(novo_caso_dict):
    """``novo_caso`` validado como ``DadosPaciente``."""
    from domain.schemas import DadosPaciente

    return DadosPaciente.model_validate(novo_caso_dict)


@pytest.fixture
def contexto(novo_caso):
    """``ContextoAtendimento`` do ``novo_caso`` com o preditor real."""
    if not CAMINHO_MODELO.is_file():
        pytest.skip("artefato ausente em models/: execute o notebook")
    from agentes.contexto import ContextoAtendimento
    from ml.preditor import PreditorPicoRisco

    preditor = PreditorPicoRisco(
        CAMINHO_MODELO, CAMINHO_MODELO.with_suffix(".metadata.json")
    )
    return ContextoAtendimento(
        atendimento_id="teste-real", paciente=novo_caso, preditor=preditor
    )


@pytest.fixture
def criar_contexto_falso(novo_caso):
    """Fábrica de contextos com ``PreditorFalso(probabilidade)``."""
    from agentes.contexto import ContextoAtendimento

    def criar(probabilidade: float = 0.99, paciente=None) -> ContextoAtendimento:
        return ContextoAtendimento(
            atendimento_id="teste-falso",
            paciente=paciente or novo_caso,
            preditor=PreditorFalso(probabilidade),
        )

    return criar


@pytest.fixture
def contexto_falso(criar_contexto_falso):
    """Contexto do ``novo_caso`` com probabilidade fixa 0,99 (ALTO)."""
    return criar_contexto_falso()
