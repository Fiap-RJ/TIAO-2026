"""
Preditor de pico de risco — CardioIA Fase 6
===========================================

Carrega o artefato treinado no notebook (``models/modelo_pico_risco.joblib``
+ ``.metadata.json``) e expõe a probabilidade ``P(pico_risco = 1)``.

Na construção, o preditor:

1. lê os metadados e confere que ``features`` é exatamente ``FEATURES``;
2. faz ``joblib.load`` apenas do caminho configurado (o artefato é pickle:
   nunca carregue arquivo de terceiros — RNF3);
3. confere que o objeto tem ``predict_proba``;
4. compara a versão do scikit-learn instalada com a do treino (aviso, não erro).

Qualquer falha de carregamento vira ``ModeloIndisponivelError`` (fatal; a CLI
sai com código 2 e orienta a executar o notebook).
"""

import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import sklearn

from core.config import obter_settings
from core.erros import ModeloIndisponivelError
from domain.constantes import FEATURES
from domain.schemas import DadosPaciente

logger = logging.getLogger("cardioia.ml.preditor")

ORIENTACAO = (
    "Execute o notebook src/CardioIA_Fase6_Modelo_Preditivo.ipynb e copie os artefatos "
    "(modelo_pico_risco.joblib e modelo_pico_risco.metadata.json) para models/."
)


class PreditorPicoRisco:
    """Modelo de pico de risco carregado e validado contra os metadados."""

    def __init__(self, caminho_modelo: Path, caminho_metadados: Path) -> None:
        self.caminho_modelo = Path(caminho_modelo)
        self.caminho_metadados = Path(caminho_metadados)
        self._sha256: str | None = None

        for caminho in (self.caminho_modelo, self.caminho_metadados):
            if not caminho.is_file():
                raise ModeloIndisponivelError(
                    f"Artefato não encontrado: {caminho}. {ORIENTACAO}"
                )

        try:
            self._metadados: dict[str, Any] = json.loads(
                self.caminho_metadados.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ModeloIndisponivelError(
                f"Metadados inválidos em {self.caminho_metadados}: {exc}. {ORIENTACAO}"
            ) from exc

        # A ordem e os nomes das colunas precisam ser os do treino.
        features = self._metadados.get("features")
        if features != list(FEATURES):
            raise ModeloIndisponivelError(
                f"As features dos metadados ({features}) diferem de FEATURES ({list(FEATURES)}). "
                f"{ORIENTACAO}"
            )

        try:
            self._modelo = joblib.load(self.caminho_modelo)
        except Exception as exc:  # pickle incompatível, arquivo truncado etc.
            logger.exception("Falha ao carregar %s", self.caminho_modelo)
            raise ModeloIndisponivelError(
                f"Não foi possível carregar {self.caminho_modelo} ({type(exc).__name__}). "
                "Alinhe as versões de scikit-learn/numpy/joblib com o requirements.txt "
                f"ou gere o artefato de novo. {ORIENTACAO}"
            ) from exc

        if not hasattr(self._modelo, "predict_proba"):
            raise ModeloIndisponivelError(
                f"O objeto em {self.caminho_modelo} não tem predict_proba. {ORIENTACAO}"
            )

        # Pickle do scikit-learn só é garantido na mesma versão: avisa, mas segue.
        self.avisos: list[str] = []
        versao_treino = self._metadados.get("versoes", {}).get("scikit-learn")
        if versao_treino and versao_treino != sklearn.__version__:
            aviso = (
                f"Modelo treinado com scikit-learn {versao_treino}; "
                f"instalado {sklearn.__version__}."
            )
            self.avisos.append(aviso)
            logger.warning(aviso)

        logger.info(
            "Modelo carregado: %s (versão %s)", self.caminho_modelo.name, self.versao
        )

    @property
    def metadados(self) -> dict[str, Any]:
        """Metadados do artefato (features, métricas, faixas de treino, versões)."""
        return self._metadados

    @property
    def versao(self) -> str:
        """Versão do artefato (``metadados["versao"]``)."""
        return str(self._metadados.get("versao", "desconhecida"))

    @property
    def faixas_treino(self) -> dict[str, list[float]]:
        """Mínimo e máximo de cada feature no treino (avisos de extrapolação)."""
        return self._metadados.get("faixas_treino", {})

    @property
    def sha256(self) -> str:
        """Hash do ``.joblib``, calculado sob demanda (rastreabilidade do artefato)."""
        if self._sha256 is None:
            self._sha256 = hashlib.sha256(self.caminho_modelo.read_bytes()).hexdigest()
        return self._sha256

    def _matriz(self, pacientes: list[DadosPaciente]) -> pd.DataFrame:
        # DataFrame com os nomes do treino, na ordem canônica: o modelo foi
        # ajustado com DataFrame e rejeitaria nomes/ordem diferentes.
        return pd.DataFrame([p.model_dump() for p in pacientes])[list(FEATURES)]

    def prever_probabilidade(self, paciente: DadosPaciente) -> float:
        """``P(pico_risco = 1)`` para um paciente."""
        return self.prever_lote([paciente])[0]

    def prever_lote(self, pacientes: list[DadosPaciente]) -> list[float]:
        """Probabilidades de vários pacientes numa única chamada vetorizada."""
        if not pacientes:
            return []
        return [
            float(p) for p in self._modelo.predict_proba(self._matriz(pacientes))[:, 1]
        ]


@lru_cache(maxsize=1)
def obter_preditor() -> PreditorPicoRisco:
    """Singleton do processo; lê ``MODELO_PATH`` da configuração em tempo de execução."""
    settings = obter_settings()
    return PreditorPicoRisco(settings.MODELO_PATH, settings.metadados_path)
