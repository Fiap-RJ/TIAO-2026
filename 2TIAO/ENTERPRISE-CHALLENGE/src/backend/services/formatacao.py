"""
Formatação de respostas — Genera Intelligence
==============================================
Pós-processamento determinístico das respostas do LLM (ex.: limite real de
tamanho no modo resumido). Roda ANTES do guardrail: se o corte remover o
disclaimer, o guardrail o reinsere (ver `services/guardrails.py`).
"""

import re

_FIM_DE_FRASE = re.compile(r"[.!?]")

# Início do fechamento da resposta: o disclaimer ("⚠️ Importante: ...") ou, na
# falta dele, a pergunta final do modo resumido ("... mais detalhes?").
_INICIO_DISCLAIMER = re.compile(r"⚠️|\**\bImportante\b\**\s*:", re.IGNORECASE)
_PERGUNTA_FINAL = re.compile(r"[^\n.!?]*mais detalhes\?", re.IGNORECASE)


def limitar_palavras(texto: str, limite: int, tolerancia: float = 1.25) -> str:
    """Limita `texto` a ~`limite` palavras, cortando no último fim de frase.

    Textos com até `limite * tolerancia` palavras são devolvidos intactos. Acima
    disso, mantém as primeiras `limite` palavras (preservando quebras de linha)
    e corta no último `.`, `!` ou `?` desse trecho; sem fim de frase, corta na
    `limite`-ésima palavra e acrescenta reticências.
    """
    if limite <= 0:
        raise ValueError("limite deve ser maior que zero")

    palavras = list(re.finditer(r"\S+", texto))
    if len(palavras) <= int(limite * tolerancia):
        return texto

    prefixo = texto[: palavras[limite - 1].end()]
    fins = list(_FIM_DE_FRASE.finditer(prefixo))
    if fins:
        return prefixo[: fins[-1].end()].rstrip()
    return prefixo.rstrip() + "…"


def _inicio_fechamento(texto: str) -> int | None:
    """Posição onde começa o fechamento (disclaimer ou pergunta final), se houver."""
    disclaimer = _INICIO_DISCLAIMER.search(texto)
    if disclaimer:
        return disclaimer.start()
    pergunta = _PERGUNTA_FINAL.search(texto)
    return pergunta.start() if pergunta else None


def limitar_corpo(texto: str, limite: int, tolerancia: float = 1.25) -> str:
    """Aplica `limitar_palavras` só ao corpo, preservando o fechamento intacto.

    O fechamento (disclaimer e pergunta final) nunca é cortado nem contado no
    limite: se o corpo antes dele passar de `limite * tolerancia` palavras, o
    corpo é cortado e o fechamento original é recolocado ao final.
    """
    inicio = _inicio_fechamento(texto)
    if inicio is None:
        return limitar_palavras(texto, limite, tolerancia)

    corpo, fechamento = texto[:inicio], texto[inicio:]
    corpo_limitado = limitar_palavras(corpo, limite, tolerancia)
    if corpo_limitado == corpo:
        return texto
    return f"{corpo_limitado.rstrip()}\n\n{fechamento.strip()}"
