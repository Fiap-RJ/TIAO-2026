"""
Módulo de Anonimização (PII Redaction)
======================================
Remove ou mascara dados pessoais identificáveis antes que o texto
seja enviado ao modelo de linguagem, garantindo conformidade com LGPD
e políticas de privacidade de dados genéticos.
"""

import re
from dataclasses import dataclass, field


@dataclass
class RedactionResult:
    """Resultado do processo de anonimização."""

    texto_limpo: str
    pii_encontrado: bool = False
    itens_removidos: int = 0
    detalhes: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════
# PADRÕES REGEX PARA DETECÇÃO DE PII
# ═══════════════════════════════════════════

PATTERNS: dict[str, re.Pattern] = {
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "rg": re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b"),
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "telefone": re.compile(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"),
    "cep": re.compile(r"\b\d{5}-?\d{3}\b"),
    "data_nascimento": re.compile(
        r"\b(?:nascimento|nascido|nasc\.?|data de nascimento)"
        r"\s*:?\s*\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b",
        re.IGNORECASE,
    ),
}

# Placeholder usado para substituir PII
REDACTED = "[DADO PESSOAL REMOVIDO]"


# ═══════════════════════════════════════════
# FUNÇÕES DE REDAÇÃO
# ═══════════════════════════════════════════


def redact_cpf(texto: str) -> tuple[str, int]:
    """Remove CPFs do texto."""
    matches = PATTERNS["cpf"].findall(texto)
    texto_limpo = PATTERNS["cpf"].sub(REDACTED, texto)
    return texto_limpo, len(matches)


def redact_rg(texto: str) -> tuple[str, int]:
    """Remove RGs do texto."""
    matches = PATTERNS["rg"].findall(texto)
    texto_limpo = PATTERNS["rg"].sub(REDACTED, texto)
    return texto_limpo, len(matches)


def redact_email(texto: str) -> tuple[str, int]:
    """Remove endereços de e-mail do texto."""
    matches = PATTERNS["email"].findall(texto)
    texto_limpo = PATTERNS["email"].sub(REDACTED, texto)
    return texto_limpo, len(matches)


def redact_telefone(texto: str) -> tuple[str, int]:
    """Remove números de telefone do texto."""
    matches = PATTERNS["telefone"].findall(texto)
    texto_limpo = PATTERNS["telefone"].sub(REDACTED, texto)
    return texto_limpo, len(matches)


def redact_cep(texto: str) -> tuple[str, int]:
    """Remove CEPs do texto."""
    matches = PATTERNS["cep"].findall(texto)
    texto_limpo = PATTERNS["cep"].sub(REDACTED, texto)
    return texto_limpo, len(matches)


def redact_data_nascimento(texto: str) -> tuple[str, int]:
    """Remove datas de nascimento do texto."""
    matches = PATTERNS["data_nascimento"].findall(texto)
    texto_limpo = PATTERNS["data_nascimento"].sub(REDACTED, texto)
    return texto_limpo, len(matches)


# ═══════════════════════════════════════════
# FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════


def sanitizar_texto(texto: str) -> RedactionResult:
    """
    Aplica todas as regras de redação de PII ao texto fornecido.

    Uso:
        resultado = sanitizar_texto("Paciente João, CPF 123.456.789-00")
        print(resultado.texto_limpo)
        # "Paciente João, [DADO PESSOAL REMOVIDO]"
    """
    if not texto:
        return RedactionResult(texto_limpo=texto)

    total_removidos = 0
    detalhes = []

    redactors = [
        ("CPF", redact_cpf),
        ("RG", redact_rg),
        ("E-mail", redact_email),
        ("Telefone", redact_telefone),
        ("CEP", redact_cep),
        ("Data de Nascimento", redact_data_nascimento),
    ]

    for nome, func in redactors:
        texto, count = func(texto)
        if count > 0:
            total_removidos += count
            detalhes.append(f"{nome}: {count} ocorrência(s) removida(s)")

    return RedactionResult(
        texto_limpo=texto,
        pii_encontrado=total_removidos > 0,
        itens_removidos=total_removidos,
        detalhes=detalhes,
    )


def sanitizar_input_usuario(mensagem: str) -> str:
    """
    Wrapper simplificado para sanitizar a mensagem do usuário antes de enviar ao agente.
    Retorna apenas o texto limpo.
    """
    resultado = sanitizar_texto(mensagem)
    if resultado.pii_encontrado:
        print(f"⚠️ PII detectado e removido do input: {resultado.detalhes}")
    return resultado.texto_limpo
