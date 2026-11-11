"""Adaptador entre telemetria persistida e o motor preditivo da Fase 6."""

import json
from datetime import datetime, timezone

from cardioia.domain.schemas import DadosPaciente, RespostaAtendimento
from cardioia.ml.preditor import obter_preditor
from cardioia.services.protocolos import selecionar_protocolos
from cardioia.services.recomendacao import montar_recomendacao_deterministica
from cardioia.services.risco import avaliar_risco

from . import db


def evaluate(paciente_id: str) -> dict:
    paciente = db.patient_by_id(paciente_id)
    if not paciente:
        raise KeyError(paciente_id)
    leituras = db.readings(paciente_id, limit=5)
    indicadores = json.loads(paciente["indicadores_json"])
    fc_media = sum(r["fc"] for r in leituras) / len(leituras) if leituras else 78.0
    spo2_media = sum(r["spo2"] for r in leituras) / len(leituras) if leituras else 97.0
    temperatura = sum(r["temperatura"] for r in leituras) / len(leituras) if leituras else 36.6
    dados = DadosPaciente(idade_media=paciente["idade"], fc_media=fc_media, spo2_media=spo2_media, temperatura=temperatura, **indicadores)
    avaliacao = avaliar_risco(dados, obter_preditor())
    protocolos = selecionar_protocolos(dados, avaliacao.classificacao)
    recomendacao = montar_recomendacao_deterministica(avaliacao, protocolos)
    resposta = RespostaAtendimento(
        atendimento_id=f"fase7-{paciente_id}-{int(datetime.now().timestamp())}",
        gerado_em=datetime.now(timezone.utc),
        paciente=dados,
        avaliacao_risco=avaliacao,
        protocolos=protocolos.protocolos,
        sinais_de_atencao=protocolos.sinais_de_atencao,
        acoes_operacionais=recomendacao.acoes_operacionais,
        explicacao=recomendacao.explicacao,
        cadeia_agentes=["Orquestrador", "Avaliação determinística"],
        origem="sem_llm",
        violacoes_guardrail=[],
        motivo_fallback=None,
    )
    resultado = resposta.model_dump(mode="json")
    db.save_assessment(paciente_id, resultado)
    return resultado

