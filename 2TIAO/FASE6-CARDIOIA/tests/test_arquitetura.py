"""
Teste de arquitetura
====================

Direção de dependências (R17.1, R17.2): ``core``, ``domain``, ``ml`` e
``services`` não importam o OpenAI Agents SDK (``agents``). Roda em
subprocesso para não herdar módulos já importados por outros testes.
"""

import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"

CODIGO = """
import sys
import core.config, core.erros, core.logging_config
import domain.constantes, domain.schemas
import ml.dataset, ml.preditor
import services.protocolos, services.recomendacao, services.risco
carregados = sorted(m for m in sys.modules if m == "agents" or m.startswith("agents."))
assert not carregados, carregados
print("ok")
"""


def test_camadas_de_dominio_nao_importam_o_sdk():
    resultado = subprocess.run(
        [sys.executable, "-c", CODIGO],
        cwd=SRC,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == "ok"


def test_pacote_da_aplicacao_nao_se_chama_agents():
    # "agents" sombrearia o SDK; o pacote local é "agentes".
    assert not (SRC / "agents").exists()
    assert (SRC / "agentes" / "__init__.py").is_file()
