"""
Camada de Persistência — Genera Intelligence
==============================================
Abstração para múltiplos backends de armazenamento (SQLite, Postgres).
"""

from services.persistence.factory import get_history_repo

__all__ = ["get_history_repo"]
