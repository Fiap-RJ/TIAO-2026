"""
Testes de ``ml.preditor``
=========================

Usa o artefato versionado em ``models/`` (``skip`` com motivo claro se ele
faltar). Confere que o artefato corresponde ao pipeline do notebook: regera a
base e o mesmo split e exige acurácia ≥ 0,98 no teste.
"""

import json
import shutil

import pytest
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from core.config import RAIZ_FASE
from core.erros import ModeloIndisponivelError
from domain.constantes import FEATURES
from domain.schemas import DadosPaciente
from ml.dataset import gerar_base_sintetica
from ml.preditor import PreditorPicoRisco, obter_preditor

MODELO = RAIZ_FASE / "models" / "modelo_pico_risco.joblib"
METADADOS = RAIZ_FASE / "models" / "modelo_pico_risco.metadata.json"

pytestmark = pytest.mark.skipif(
    not (MODELO.is_file() and METADADOS.is_file()),
    reason="artefato ausente em models/: execute o notebook src/CardioIA_Fase6_Modelo_Preditivo.ipynb",
)


@pytest.fixture(scope="module")
def preditor() -> PreditorPicoRisco:
    return PreditorPicoRisco(MODELO, METADADOS)


def test_features_dos_metadados_sao_as_canonicas(preditor):
    assert preditor.metadados["features"] == list(FEATURES)


def test_novo_caso_tem_risco_alto(preditor, novo_caso):
    assert preditor.prever_probabilidade(novo_caso) >= 0.70


def test_acuracia_no_split_regerado(preditor):
    df = gerar_base_sintetica()
    X, y = df[list(FEATURES)], df["pico_risco"]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    pacientes = [
        DadosPaciente.model_validate(linha) for linha in X_test.to_dict("records")
    ]
    previsto = [int(p >= 0.5) for p in preditor.prever_lote(pacientes)]
    assert accuracy_score(y_test, previsto) >= 0.98


def test_prever_lote_igual_a_unitario(preditor, novo_caso):
    assert (
        preditor.prever_lote([novo_caso, novo_caso])
        == [preditor.prever_probabilidade(novo_caso)] * 2
    )
    assert preditor.prever_lote([]) == []


def test_sem_aviso_de_versao_no_ambiente_do_treino(preditor):
    assert preditor.avisos == []


def test_sha256_tem_64_hex(preditor):
    assert len(preditor.sha256) == 64
    int(preditor.sha256, 16)


def test_features_trocadas_geram_erro(tmp_path):
    metadados = json.loads(METADADOS.read_text(encoding="utf-8"))
    metadados["features"] = list(reversed(metadados["features"]))
    falso = tmp_path / "modelo.metadata.json"
    falso.write_text(json.dumps(metadados), encoding="utf-8")
    with pytest.raises(ModeloIndisponivelError, match="features"):
        PreditorPicoRisco(MODELO, falso)


def test_arquivo_ausente_gera_erro(tmp_path):
    with pytest.raises(ModeloIndisponivelError, match="notebook"):
        PreditorPicoRisco(tmp_path / "nao_existe.joblib", METADADOS)


def test_pickle_corrompido_gera_erro(tmp_path):
    corrompido = tmp_path / "modelo.joblib"
    corrompido.write_bytes(b"isto nao e um pickle")
    with pytest.raises(ModeloIndisponivelError, match="carregar"):
        PreditorPicoRisco(corrompido, METADADOS)


def test_versao_diferente_gera_aviso(tmp_path):
    metadados = json.loads(METADADOS.read_text(encoding="utf-8"))
    metadados["versoes"]["scikit-learn"] = "0.0.1"
    falso = tmp_path / "modelo.metadata.json"
    falso.write_text(json.dumps(metadados), encoding="utf-8")
    shutil.copy(MODELO, tmp_path / "modelo.joblib")
    preditor = PreditorPicoRisco(tmp_path / "modelo.joblib", falso)
    assert any("0.0.1" in aviso for aviso in preditor.avisos)


def test_obter_preditor_usa_configuracao(settings_limpas, tmp_path):
    settings_limpas.setenv("MODELO_PATH", str(tmp_path / "inexistente.joblib"))
    with pytest.raises(ModeloIndisponivelError):
        obter_preditor()
