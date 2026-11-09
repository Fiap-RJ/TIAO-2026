"""
Base sintética — CardioIA Fase 6
================================

``gerar_base_sintetica()`` reproduz literalmente o código de geração do
enunciado (seed 42, n = 5000). É o mesmo código da célula 3 do notebook e é
usado pelos testes (``test_preditor.py`` regera o split de teste).

A base não é versionada (CSV ignorado na raiz do repositório): ela é regerada
de forma determinística. ``np.random.seed`` usa o gerador legado, cujo stream
é estável entre versões do NumPy.
"""

import numpy as np
import pandas as pd


def gerar_base_sintetica() -> pd.DataFrame:
    """Gera a base do enunciado: 10 features + ``pico_risco`` (5000 linhas).

    ``risk_score`` é auxiliar (soma das 6 regras) e não entra no DataFrame,
    para não vazar o alvo nas features. Atenção: reinicia a semente global
    do NumPy (``np.random.seed(42)``), exatamente como o código original.
    """
    # --- início do código literal do enunciado ---
    np.random.seed(42)
    n = 5000

    df = pd.DataFrame(
        {
            "idade_media": np.random.normal(55, 12, n).clip(18, 90),
            "carga_sistema": np.random.uniform(30, 100, n),
            "tempo_espera": np.random.normal(45, 20, n).clip(5, 180),
            "fc_media": np.random.normal(85, 15, n).clip(50, 150),
            "spo2_media": np.random.normal(95, 3, n).clip(70, 100),
            "pa_sistolica": np.random.normal(125, 20, n).clip(80, 200),
            "temperatura": np.random.normal(24, 5, n).clip(10, 40),
            "densidade_eventos": np.random.poisson(3, n),
            "eventos_24h": np.random.poisson(2, n),
            "disponibilidade_recursos": np.random.uniform(20, 100, n),
        }
    )

    risk_score = (
        (df["carga_sistema"] > 80).astype(int)
        + (df["tempo_espera"] > 60).astype(int)
        + (df["spo2_media"] < 92).astype(int)
        + (df["fc_media"] > 110).astype(int)
        + (df["eventos_24h"] > 4).astype(int)
        + (df["disponibilidade_recursos"] < 40).astype(int)
    )

    df["pico_risco"] = (risk_score >= 2).astype(int)
    # --- fim do código literal do enunciado ---
    return df
