"""
Protocolos operacionais — CardioIA Fase 6
=========================================

Base simulada P01–P10 (texto literal do enunciado) e seleção determinística.

Duas camadas de limiar:

- os **protocolos** são gatilhos de ação (ex.: ``carga_sistema > 85`` → abrir
  unidades temporárias);
- as **regras do alvo** (``REGRAS_ALVO``) definem o que é sinal de risco e são
  mais brandas (ex.: ``carga_sistema > 80``).

Uma feature que atende à regra do alvo, mas não ao gatilho do protocolo, vira
"sinal de atenção" (ex.: SpO2 89 é < 92, mas não < 88: P01 não aciona).

A seleção é feita por código: o LLM não escolhe protocolos, e o guardrail
de saída rejeita qualquer conjunto diferente deste.
"""

from domain.constantes import FEATURES, REGRAS_ALVO
from domain.schemas import (
    Classificacao,
    DadosPaciente,
    Protocolo,
    ProtocoloAcionado,
    ResultadoProtocolos,
    SinalAtencao,
)

BASE_PROTOCOLOS: tuple[Protocolo, ...] = (
    Protocolo(
        id="P01",
        texto="Se SPO2 < 88% → iniciar suporte respiratório imediato",
        variavel="spo2_media",
        operador="<",
        limiar=88,
    ),
    Protocolo(
        id="P02",
        texto="Se carga do sistema > 85% → abrir unidades temporárias",
        variavel="carga_sistema",
        operador=">",
        limiar=85,
    ),
    Protocolo(
        id="P03",
        texto="Se FC > 120 → iniciar monitoramento intensivo",
        variavel="fc_media",
        operador=">",
        limiar=120,
    ),
    Protocolo(
        id="P04",
        texto="Se eventos_24h > 5 → ativar equipe de resposta rápida",
        variavel="eventos_24h",
        operador=">",
        limiar=5,
    ),
    Protocolo(
        id="P05",
        texto="Se disponibilidade_recursos < 30% → redistribuir insumos",
        variavel="disponibilidade_recursos",
        operador="<",
        limiar=30,
    ),
    Protocolo(
        id="P06",
        texto="Se tempo_espera > 90 min → priorizar triagem emergencial",
        variavel="tempo_espera",
        operador=">",
        limiar=90,
    ),
    Protocolo(
        id="P07",
        texto="Se temperatura > 38°C média → iniciar protocolo infeccioso",
        variavel="temperatura",
        operador=">",
        limiar=38,
    ),
    Protocolo(
        id="P08",
        texto="Se densidade_eventos > 6 → ativar plano de contingência",
        variavel="densidade_eventos",
        operador=">",
        limiar=6,
    ),
    Protocolo(
        id="P09",
        texto="Se PA sistólica < 90 → iniciar protocolo de choque",
        variavel="pa_sistolica",
        operador="<",
        limiar=90,
    ),
    Protocolo(
        id="P10",
        texto="Se risco sistêmico alto → ativar estado de emergência",
        variavel="classificacao_risco",
        operador="==",
        limiar="ALTO",
    ),
)

_POR_ID = {p.id: p for p in BASE_PROTOCOLOS}
_POR_VARIAVEL = {p.variavel: p for p in BASE_PROTOCOLOS}


def formatar_numero(valor: float | str) -> str:
    """``92.0`` → ``"92"``; ``37.5`` → ``"37.5"`` (sem zeros supérfluos)."""
    return valor if isinstance(valor, str) else f"{valor:g}"


def comparar(valor: float | str, operador: str, limiar: float | str) -> bool:
    """Comparação estrita: o valor igual ao limiar NÃO aciona ``>`` nem ``<``."""
    if operador == ">":
        return valor > limiar
    if operador == "<":
        return valor < limiar
    if operador == "==":
        return valor == limiar
    raise ValueError(f"operador desconhecido: {operador!r}")


def obter_protocolo(protocolo_id: str) -> Protocolo:
    """Protocolo da base pelo ID (``KeyError`` se não existir)."""
    return _POR_ID[protocolo_id]


def listar_base() -> list[Protocolo]:
    """Cópia da base completa P01–P10 (para consulta, sem risco de alteração)."""
    return [p.model_copy() for p in BASE_PROTOCOLOS]


def selecionar_protocolos(
    paciente: DadosPaciente, classificacao: Classificacao
) -> ResultadoProtocolos:
    """Seleciona os protocolos acionados e os sinais de atenção (função pura).

    - Protocolos: ordem por ID; P10 aciona se, e somente se, a classificação é ALTO.
    - Sinais de atenção: na ordem de ``FEATURES``, as variáveis com regra do
      alvo verdadeira e protocolo correspondente falso.
    """
    acionados: list[ProtocoloAcionado] = []
    for protocolo in sorted(BASE_PROTOCOLOS, key=lambda p: p.id):
        if protocolo.variavel == "classificacao_risco":
            valor: float | str = classificacao
        else:
            valor = getattr(paciente, protocolo.variavel)
        if comparar(valor, protocolo.operador, protocolo.limiar):
            acionados.append(
                ProtocoloAcionado(
                    id=protocolo.id,
                    texto=protocolo.texto,
                    variavel=protocolo.variavel,
                    valor_observado=valor,
                    limiar=protocolo.limiar,
                    justificativa=(
                        f"{protocolo.variavel}={formatar_numero(valor)}"
                        if protocolo.operador == "=="
                        else f"{protocolo.variavel}={formatar_numero(valor)} "
                        f"{protocolo.operador} {formatar_numero(protocolo.limiar)}"
                    ),
                )
            )

    ids_acionados = {p.id for p in acionados}
    sinais: list[SinalAtencao] = []
    for nome in FEATURES:
        if nome not in REGRAS_ALVO:
            continue
        operador_risco, limiar_risco = REGRAS_ALVO[nome]
        valor = getattr(paciente, nome)
        protocolo = _POR_VARIAVEL[nome]
        if (
            comparar(valor, operador_risco, limiar_risco)
            and protocolo.id not in ids_acionados
        ):
            sinais.append(
                SinalAtencao(
                    variavel=nome,
                    valor=valor,
                    limiar_risco=limiar_risco,
                    limiar_protocolo=protocolo.limiar,
                    protocolo_id=protocolo.id,
                    mensagem=(
                        f"{nome}={formatar_numero(valor)} (risco {operador_risco} "
                        f"{formatar_numero(limiar_risco)}; {protocolo.id} aciona "
                        f"{protocolo.operador} {formatar_numero(protocolo.limiar)})"
                    ),
                )
            )

    return ResultadoProtocolos(protocolos=acionados, sinais_de_atencao=sinais)
