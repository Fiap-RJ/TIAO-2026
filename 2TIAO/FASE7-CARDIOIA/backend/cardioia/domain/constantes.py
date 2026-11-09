"""
Constantes de domínio — CardioIA Fase 6
=======================================

Fonte única das regras fixas do sistema: ordem das features do modelo,
limiar de decisão, faixas de risco, regras de geração do alvo, aviso legal e expressões de
termos prescritivos.

As faixas não são configuráveis por variável de ambiente: mudá-las é mudança
de regra de negócio e deve passar por código e testes.
"""

import re

# Ordem canônica das colunas usada no treino (o modelo foi ajustado com DataFrame,
# então a ordem e os nomes precisam coincidir na predição).
FEATURES: tuple[str, ...] = (
    "idade_media",
    "carga_sistema",
    "tempo_espera",
    "fc_media",
    "spo2_media",
    "pa_sistolica",
    "temperatura",
    "densidade_eventos",
    "eventos_24h",
    "disponibilidade_recursos",
)

# Limiar do classificador: pico_risco_previsto = probabilidade >= 0,50.
LIMIAR_DECISAO = 0.50

# Faixas de risco: BAIXO < 0,40 ≤ MODERADO < 0,70 ≤ ALTO.
# O limiar de decisão (0,50) cai dentro de MODERADO, a zona de incerteza.
FAIXA_MODERADO, FAIXA_ALTO = 0.40, 0.70

# Regras usadas na GERAÇÃO do alvo (enunciado) — usadas para "sinais de atenção" e coerência.
# Formato: variável → (operador, limiar). pico_risco = 1 quando pelo menos 2 são verdadeiras.
REGRAS_ALVO: dict[str, tuple[str, float]] = {
    "carga_sistema": (">", 80),
    "tempo_espera": (">", 60),
    "spo2_media": ("<", 92),
    "fc_media": (">", 110),
    "eventos_24h": (">", 4),
    "disponibilidade_recursos": ("<", 40),
}

AVISO_LEGAL = (
    "Aviso: o CardioIA é um sistema acadêmico, informativo e de apoio à decisão operacional, "
    "baseado em dados sintéticos. Não realiza diagnóstico, não prescreve tratamentos e não "
    "substitui a avaliação de um profissional de saúde."
)

# Fonte única de termos prescritivos, usada pelo input guardrail e pela verificação V5 da saída.
# \bprescr\w* cobre prescrição/prescrições/prescrever/prescreva/prescrito; re.IGNORECASE nos dois.
_PRESCRITIVOS = r"\bprescr\w*|\bdosage[mn]s?\b|\bdoses?\b|\bposologia\b"

# V5 (saída do LLM): termos prescritivos ou quantidades com unidade de medicamento.
# A regra é rígida de propósito: até a negação ("não prescrevemos") conta como violação.
TERMOS_PRESCRITIVOS = re.compile(
    _PRESCRITIVOS + r"|\b\d+(?:[.,]\d+)?\s?(?:mg|mcg|ml|ui)\b",
    re.IGNORECASE,
)

# Entrada do usuário: termos prescritivos e pedidos diretos de medicamento.
PEDIDOS_PRESCRICAO = re.compile(
    _PRESCRITIVOS + r"|qual (?:rem[eé]dio|medicamento)|posso (?:tomar|aplicar)",
    re.IGNORECASE,
)
