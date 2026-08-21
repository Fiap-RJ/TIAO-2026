"""
Serviço de leitura do relatório estruturado (proposta_estrutura_de_dados.json).
Fonte única para os endpoints de riscos, ancestralidade e resumos.
"""

import json
import os
from functools import lru_cache
from pathlib import Path

CURRENT_DIR = Path(__file__).parent
BACKEND_DIR = CURRENT_DIR.parent

# Path do JSON: usa env var (Docker) ou infere do layout local
_default_json = BACKEND_DIR.parent.parent / "proposta_estrutura_de_dados.json"
JSON_PATH = Path(os.getenv("GENERA_DATA_PATH", str(_default_json)))


@lru_cache(maxsize=1)
def carregar_relatorio() -> dict:
    """Carrega o relatório estruturado do disco (cacheado em memória)."""
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
