"""
Configurações centralizadas — CardioIA Fase 6
=============================================

Único módulo que lê variáveis de ambiente (nenhum outro chama ``os.getenv``).
O ``.env`` é carregado de ``src/.env``, independentemente do diretório atual.

Diferença deliberada em relação à Fase 5: lá os valores eram atributos de
classe e ``settings = Settings()`` era criado no import. Aqui o parse acontece
em ``Settings.__init__`` e o acesso é preguiçoso, por ``obter_settings()``.
Assim, um ``MAX_TURNS=abc`` não estoura no ``import`` (antes do ``try`` da
CLI, que o converte em exit 2), e os testes conseguem trocar a configuração
com ``monkeypatch`` + ``obter_settings.cache_clear()``.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from core.erros import ConfiguracaoError

# Raiz da fase: .../FASE6-CARDIOIA (este arquivo está em src/core/).
RAIZ_FASE = Path(__file__).resolve().parents[2]
CAMINHO_ENV = Path(__file__).resolve().parents[1] / ".env"

_VERDADEIROS = {"true", "1", "sim"}
_FALSOS = {"false", "0", "nao", "não"}
_NIVEIS_LOG = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _ler_texto(nome: str, padrao: str) -> str:
    """Lê uma variável como texto, sem espaços nas pontas."""
    return os.getenv(nome, padrao).strip()


def _ler_int(nome: str, padrao: int, *, minimo: int | None = None) -> int:
    """Lê um inteiro; vazio/ausente usa o padrão; inválido → ``ConfiguracaoError``."""
    bruto = _ler_texto(nome, "")
    if not bruto:
        return padrao
    esperado = f"inteiro ≥ {minimo}" if minimo is not None else "inteiro"
    try:
        valor = int(bruto)
    except ValueError:
        raise ConfiguracaoError(
            f"{nome} deve ser {esperado}; recebido {bruto!r}"
        ) from None
    if minimo is not None and valor < minimo:
        raise ConfiguracaoError(f"{nome} deve ser {esperado}; recebido {bruto!r}")
    return valor


def _ler_float_opcional(
    nome: str, padrao: float | None, *, minimo: float, maximo: float
) -> float | None:
    """Lê um float opcional.

    Ausente → padrão; definido como string vazia → ``None`` (o parâmetro não é
    enviado ao modelo, útil para modelos que rejeitam ``temperature``).
    """
    bruto = os.getenv(nome)
    if bruto is None:
        return padrao
    bruto = bruto.strip()
    if not bruto:
        return None
    try:
        valor = float(bruto)
    except ValueError:
        raise ConfiguracaoError(
            f"{nome} deve ser número entre {minimo} e {maximo} ou vazio; recebido {bruto!r}"
        ) from None
    if not minimo <= valor <= maximo:
        raise ConfiguracaoError(
            f"{nome} deve ser número entre {minimo} e {maximo} ou vazio; recebido {bruto!r}"
        )
    return valor


def _ler_bool(nome: str, padrao: bool) -> bool:
    """Aceita true/false/1/0/sim/nao (sem diferenciar maiúsculas)."""
    bruto = _ler_texto(nome, "").lower()
    if not bruto:
        return padrao
    if bruto in _VERDADEIROS:
        return True
    if bruto in _FALSOS:
        return False
    raise ConfiguracaoError(
        f"{nome} deve ser true/false/1/0/sim/nao; recebido {bruto!r}"
    )


def _ler_caminho(nome: str, padrao: str) -> Path:
    """Lê um caminho; relativos são resolvidos contra a raiz da fase."""
    caminho = Path(_ler_texto(nome, "") or padrao)
    return caminho if caminho.is_absolute() else (RAIZ_FASE / caminho).resolve()


def _ler_nivel_log(nome: str, padrao: str) -> str:
    """Lê um nível de log padrão do módulo ``logging``."""
    nivel = (_ler_texto(nome, "") or padrao).upper()
    if nivel not in _NIVEIS_LOG:
        raise ConfiguracaoError(
            f"{nome} deve ser um de {sorted(_NIVEIS_LOG)}; recebido {nivel!r}"
        )
    return nivel


class Settings:
    """Configuração da aplicação, lida de ``src/.env`` (padrão Fase 5, com parse validado)."""

    def __init__(self) -> None:
        # override=False (padrão): variáveis já definidas no ambiente prevalecem
        # sobre o .env, o que permite aos testes controlar a configuração.
        load_dotenv(CAMINHO_ENV)
        self.RAIZ_FASE = RAIZ_FASE
        self.OPENAI_API_KEY = _ler_texto("OPENAI_API_KEY", "")
        self.OPENAI_MODEL = _ler_texto("OPENAI_MODEL", "") or "gpt-4.1-mini"
        self.OPENAI_TEMPERATURE = _ler_float_opcional(
            "OPENAI_TEMPERATURE", 0.0, minimo=0.0, maximo=2.0
        )
        self.MAX_TURNS = _ler_int("MAX_TURNS", 12, minimo=1)
        self.MODELO_PATH = _ler_caminho(
            "MODELO_PATH", "models/modelo_pico_risco.joblib"
        )
        self.SESSIONS_DB_PATH = _ler_caminho("SESSIONS_DB_PATH", "data/sessoes.db")
        self.TRACING_HABILITADO = _ler_bool("TRACING_HABILITADO", False)
        self.LOG_LEVEL = _ler_nivel_log("LOG_LEVEL", "INFO")

    @property
    def openai_configurado(self) -> bool:
        """True se ``OPENAI_API_KEY`` estiver preenchida (o valor nunca é exibido)."""
        return bool(self.OPENAI_API_KEY)

    @property
    def metadados_path(self) -> Path:
        """Metadados do modelo: mesmo nome do ``.joblib`` com ``.metadata.json``."""
        return self.MODELO_PATH.with_suffix(".metadata.json")

    def __repr__(self) -> str:
        # Evita que a chave apareça em logs ou tracebacks por acidente.
        return (
            f"Settings(OPENAI_MODEL={self.OPENAI_MODEL!r}, "
            f"openai_configurado={self.openai_configurado}, MAX_TURNS={self.MAX_TURNS}, "
            f"MODELO_PATH={str(self.MODELO_PATH)!r})"
        )


@lru_cache(maxsize=1)
def obter_settings() -> Settings:
    """Devolve a configuração do processo (criada na primeira chamada)."""
    return Settings()
