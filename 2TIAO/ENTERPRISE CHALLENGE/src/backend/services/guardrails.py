"""
Módulo de Guardrails — Validação Pós-Geração
=============================================
Verifica se a resposta do LLM respeita as políticas de segurança do sistema Genera Intelligence.
Atua como última linha de defesa caso o modelo "escape" das instruções do system prompt.
"""

import re
from dataclasses import dataclass, field

# ═══════════════════════════════════════════
# CONFIGURAÇÃO DE TERMOS E PADRÕES PROIBIDOS
# ═══════════════════════════════════════════

TERMOS_DIAGNOSTICO: list[str] = [
    "seu diagnóstico é",
    "você foi diagnosticado",
    "você tem a doença",
    "confirmo que você possui",
    "isso confirma que você tem",
    "você sofre de",
    "você está doente",
]

TERMOS_PRESCRICAO: list[str] = [
    "tome o medicamento",
    "prescrevo",
    "recomendo que tome",
    "a dosagem ideal é",
    "inicie o tratamento com",
    "pare de tomar",
    "suspenda o uso de",
    "troque o medicamento por",
    "aumente a dose",
    "reduza a dose para",
]

TERMOS_ALARMISTAS: list[str] = [
    "você vai morrer",
    "risco de morte",
    "doença fatal",
    "situação gravíssima",
    "perigo iminente",
    "você certamente desenvolverá",
    "é inevitável que",
]

DISCLAIMER_KEYWORDS: list[str] = [
    "não substitui",
    "consulte um médico",
    "consultar um médico",
    "especialista clínico",
    "médico geneticista",
    "acompanhamento médico",
    "profissional de saúde",
]

DISCLAIMER_FALLBACK: str = (
    "\n\n⚠️ **Importante:** Este assistente é puramente informativo e não substitui uma consulta médica. "
    "Os dados genéticos indicam predisposições, não certezas. Recomendamos fortemente que você consulte "
    "um médico geneticista ou especialista clínico para correlacionar esses achados com seu histórico "
    "pessoal e familiar."
)

RESPOSTA_BLOQUEADA: str = (
    "Desculpe, não consigo fornecer uma resposta adequada para essa pergunta no momento. "
    "Para informações sobre diagnósticos ou tratamentos, por favor consulte diretamente "
    "um profissional de saúde qualificado." + DISCLAIMER_FALLBACK
)


# ═══════════════════════════════════════════
# RESULTADO DA VALIDAÇÃO
# ═══════════════════════════════════════════


@dataclass
class GuardrailResult:
    """Resultado da verificação de guardrails."""

    aprovado: bool = True
    resposta_final: str = ""
    violacoes: list[str] = field(default_factory=list)
    disclaimer_adicionado: bool = False


# ═══════════════════════════════════════════
# FUNÇÕES DE VERIFICAÇÃO
# ═══════════════════════════════════════════


def _normalizar(texto: str) -> str:
    """Normaliza texto para comparação case-insensitive e sem acentos extras."""
    return texto.lower().strip()


def verificar_diagnostico(resposta: str) -> list[str]:
    """Verifica se a resposta contém termos que indicam diagnóstico médico."""
    resposta_lower = _normalizar(resposta)
    violacoes = []
    for termo in TERMOS_DIAGNOSTICO:
        if termo.lower() in resposta_lower:
            violacoes.append(f"[DIAGNÓSTICO] Termo proibido detectado: '{termo}'")
    return violacoes


def verificar_prescricao(resposta: str) -> list[str]:
    """Verifica se a resposta contém termos que indicam prescrição médica."""
    resposta_lower = _normalizar(resposta)
    violacoes = []
    for termo in TERMOS_PRESCRICAO:
        if termo.lower() in resposta_lower:
            violacoes.append(f"[PRESCRIÇÃO] Termo proibido detectado: '{termo}'")
    return violacoes


def verificar_tom_alarmista(resposta: str) -> list[str]:
    """Verifica se a resposta contém linguagem alarmista ou catastrofista."""
    resposta_lower = _normalizar(resposta)
    violacoes = []
    for termo in TERMOS_ALARMISTAS:
        if termo.lower() in resposta_lower:
            violacoes.append(f"[ALARMISMO] Linguagem inadequada detectada: '{termo}'")
    return violacoes


def verificar_disclaimer(resposta: str) -> bool:
    """Verifica se a resposta contém alguma forma de disclaimer médico."""
    resposta_lower = _normalizar(resposta)
    return any(kw.lower() in resposta_lower for kw in DISCLAIMER_KEYWORDS)


def verificar_pii_na_resposta(resposta: str) -> list[str]:
    """Verifica se a resposta contém padrões de PII (CPF, e-mail, telefone)."""
    violacoes = []

    # CPF: 000.000.000-00 ou 00000000000
    if re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", resposta):
        violacoes.append("[PII] Possível CPF detectado na resposta")

    # E-mail
    if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resposta):
        violacoes.append("[PII] Possível e-mail detectado na resposta")

    # Telefone brasileiro
    if re.search(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", resposta):
        violacoes.append("[PII] Possível telefone detectado na resposta")

    return violacoes


# ═══════════════════════════════════════════
# FUNÇÃO PRINCIPAL DE VALIDAÇÃO
# ═══════════════════════════════════════════


def validar_resposta(resposta: str) -> GuardrailResult:
    """
    Executa todas as verificações de guardrail na resposta gerada pelo LLM.

    Retorna um GuardrailResult com:
    - aprovado: True se a resposta pode ser entregue ao usuário
    - resposta_final: a resposta (possivelmente com disclaimer adicionado) ou a mensagem de bloqueio
    - violacoes: lista de problemas encontrados
    """
    result = GuardrailResult(resposta_final=resposta)

    # Coleta todas as violações
    violacoes = []
    violacoes.extend(verificar_diagnostico(resposta))
    violacoes.extend(verificar_prescricao(resposta))
    violacoes.extend(verificar_tom_alarmista(resposta))
    violacoes.extend(verificar_pii_na_resposta(resposta))

    result.violacoes = violacoes

    # Se há violações críticas (diagnóstico, prescrição, PII), bloqueia a resposta
    violacoes_criticas = [
        v
        for v in violacoes
        if "[DIAGNÓSTICO]" in v or "[PRESCRIÇÃO]" in v or "[PII]" in v
    ]

    if violacoes_criticas:
        result.aprovado = False
        result.resposta_final = RESPOSTA_BLOQUEADA
        return result

    # Se há violações de tom mas não críticas, deixa passar com aviso no log
    # (o tom alarmista é preocupante mas não justifica bloquear a resposta inteira)

    # Verifica e adiciona disclaimer se ausente
    if not verificar_disclaimer(resposta):
        result.resposta_final = resposta + DISCLAIMER_FALLBACK
        result.disclaimer_adicionado = True

    return result
