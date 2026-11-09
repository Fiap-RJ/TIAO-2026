"""Configuração exclusiva da API integradora."""

import os
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BACKEND_ROOT / "data" / "cardioia.db"))
JWT_SECRET = os.getenv("JWT_SECRET", "troque-esta-chave-em-producao")
DEVICE_KEY = os.getenv("DEVICE_KEY", "")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:8081"
    ).split(",")
    if origin.strip()
]
