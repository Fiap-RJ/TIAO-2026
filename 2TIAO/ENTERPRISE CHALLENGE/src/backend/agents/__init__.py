"""
Módulo de Agentes — Genera Intelligence
========================================
Exporta o grafo compilado pronto para uso pela API.
"""

from agents.graph import build_graph

# Grafo compilado (singleton) — usado pela rota de chat
app = build_graph()

__all__ = ["app"]
