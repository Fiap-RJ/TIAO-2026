"""
Verificação e fallback da recomendação — CardioIA Fase 6
========================================================

- ``verificar_recomendacao``: confere a saída estruturada do LLM
  (``RecomendacaoFinal``) contra o que o código calculou. É a função usada
  pelo ``output_guardrail`` do Planejador. Lista vazia = sem violações.
- ``montar_recomendacao_deterministica``: recomendação por template, usada no
  modo ``--sem-llm`` e como fallback seguro quando o LLM falha.

Verificações:

- V1 probabilidade divergente (tolerância 0,0005);
- V2 classificação diferente;
- V3 conjunto de protocolos diferente (faltantes/extras);
- V4 IDs duplicados;
- V5 termo prescritivo em ``acoes_operacionais`` ou ``explicacao`` (nunca no
  aviso legal, que o código acrescenta depois e contém "prescreve").
"""

from collections import Counter

from domain.constantes import TERMOS_PRESCRITIVOS
from domain.schemas import AvaliacaoRisco, RecomendacaoFinal, ResultadoProtocolos
from services.protocolos import formatar_numero, obter_protocolo

TOLERANCIA_PROBABILIDADE = 0.0005
MAX_ACOES = 8
ACAO_SEM_PROTOCOLOS = "Manter monitoramento de rotina e reavaliar periodicamente."


def verificar_recomendacao(
    rec: RecomendacaoFinal,
    avaliacao: AvaliacaoRisco | None,
    resultado: ResultadoProtocolos | None,
) -> list[str]:
    """Devolve as violações de ``rec`` em relação ao que foi calculado (função pura)."""
    if avaliacao is None or resultado is None:
        return [
            "contexto incompleto: risco ou protocolos não foram calculados pelas tools"
        ]

    violacoes: list[str] = []
    if (
        abs(rec.probabilidade_prevista - avaliacao.probabilidade)
        > TOLERANCIA_PROBABILIDADE
    ):
        violacoes.append(
            f"V1 probabilidade divergente: informada {rec.probabilidade_prevista}, "
            f"calculada {avaliacao.probabilidade}"
        )
    if rec.classificacao_risco != avaliacao.classificacao:
        violacoes.append(
            f"V2 classificação divergente: informada {rec.classificacao_risco}, "
            f"calculada {avaliacao.classificacao}"
        )

    esperados = {p.id for p in resultado.protocolos}
    informados = set(rec.protocolos_sugeridos)
    if informados != esperados:
        faltantes = sorted(esperados - informados)
        extras = sorted(informados - esperados)
        violacoes.append(
            f"V3 protocolos divergentes: faltantes {faltantes}, extras {extras}"
        )

    duplicados = sorted(
        i for i, n in Counter(rec.protocolos_sugeridos).items() if n > 1
    )
    if duplicados:
        violacoes.append(f"V4 protocolos duplicados: {duplicados}")

    campos = [
        (f"acoes_operacionais[{i}]", a) for i, a in enumerate(rec.acoes_operacionais)
    ]
    campos.append(("explicacao", rec.explicacao))
    for campo, texto in campos:
        achado = TERMOS_PRESCRITIVOS.search(texto)
        if achado:
            violacoes.append(f"V5 termo prescritivo em {campo}: {achado.group(0)!r}")

    return violacoes


def _acao_do_protocolo(texto: str) -> str:
    """Trecho após "→", com a primeira letra maiúscula."""
    acao = texto.split("→", 1)[-1].strip()
    return acao[:1].upper() + acao[1:]


def montar_recomendacao_deterministica(
    avaliacao: AvaliacaoRisco, resultado: ResultadoProtocolos
) -> RecomendacaoFinal:
    """Recomendação por regras e template, sem LLM (sempre passa em ``verificar_recomendacao``)."""
    acoes = [_acao_do_protocolo(p.texto) for p in resultado.protocolos] or [
        ACAO_SEM_PROTOCOLOS
    ]
    for sinal in resultado.sinais_de_atencao:
        protocolo = obter_protocolo(sinal.protocolo_id)
        acoes.append(
            f"Acompanhar {sinal.variavel} (valor {formatar_numero(sinal.valor)}; "
            f"protocolo {sinal.protocolo_id} aciona em {protocolo.operador} "
            f"{formatar_numero(sinal.limiar_protocolo)})"
        )
    acoes = acoes[:MAX_ACOES]

    ids = [p.id for p in resultado.protocolos]
    sinais = [s.variavel for s in resultado.sinais_de_atencao]
    probabilidade_txt = f"{avaliacao.probabilidade:.4f}".replace(".", ",")
    explicacao = (
        f"O modelo preditivo estimou probabilidade de pico de risco de {probabilidade_txt} "
        f"(faixa {avaliacao.classificacao}). "
        f"Protocolos acionados pelas regras da base simulada: {', '.join(ids) or 'nenhum'}. "
        "Sinais de atenção (acima do limiar de risco, abaixo do gatilho do protocolo): "
        f"{', '.join(sinais) or 'nenhum'}. "
        "Recomendação montada por regras determinísticas, para apoio à decisão operacional."
    )

    return RecomendacaoFinal(
        probabilidade_prevista=avaliacao.probabilidade,
        classificacao_risco=avaliacao.classificacao,
        protocolos_sugeridos=ids,
        acoes_operacionais=acoes,
        explicacao=explicacao,
    )
