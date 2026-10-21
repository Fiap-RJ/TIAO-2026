"""
Pipeline de atendimento — CardioIA Fase 6
=========================================

``executar_atendimento`` é o ponto único de execução, usado pela CLI e pelos
testes (o parâmetro ``hooks`` permite observar a execução sem alterá-la).

Fluxo:

1. cria ou reaproveita o ``ContextoAtendimento`` e reinicia a cadeia do turno
   (``["Orquestrador"]``; R10.4). Risco, protocolos e notas persistem;
2. ``usar_llm=False``: calcula tudo por ``services`` e devolve ``origem="sem_llm"``;
3. com LLM: exige ``OPENAI_API_KEY`` (``ConfiguracaoError``), inicializa o SDK
   uma vez e executa ``Runner.run`` a partir do Orquestrador;
4. monta a ``RespostaAtendimento`` com os valores do **contexto** (calculados
   por código) e as ações/explicação do LLM. O aviso legal é fixo.

Falhas recuperáveis do LLM (guardrail de saída, limite de turnos, saída
inválida, rede, fluxo fora de ordem) viram fallback determinístico, sempre
sinalizado em ``origem`` e ``motivo_fallback``.
"""

import asyncio
import atexit
import json
import logging
from datetime import datetime, timezone
from uuid import uuid4

import openai
from agents import (
    InputGuardrailTripwireTriggered,
    MaxTurnsExceeded,
    ModelBehaviorError,
    ModelRefusalError,
    OutputGuardrailTripwireTriggered,
    RunConfig,
    RunHooks,
    Runner,
    Session,
    UserError,
    set_default_openai_key,
)

from agentes.contexto import ContextoAtendimento
from agentes.orquestrador import criar_orquestrador
from core.config import Settings, obter_settings
from core.erros import (
    ConfiguracaoError,
    EntradaBloqueadaError,
    ErroFluxoAgentes,
    ModeloIndisponivelError,
)
from domain.schemas import DadosPaciente, RecomendacaoFinal, RespostaAtendimento
from ml.preditor import obter_preditor
from services.protocolos import selecionar_protocolos
from services.recomendacao import montar_recomendacao_deterministica
from services.risco import avaliar_risco

logger = logging.getLogger("cardioia.pipeline")

NOME_WORKFLOW = "CardioIA-Fase6"
MENSAGEM_SEM_CHAVE = (
    "OPENAI_API_KEY não configurada: configure src/.env (veja src/.env.example) "
    "ou use --sem-llm"
)

_sdk_inicializado = False


def inicializar_sdk(settings: Settings) -> None:
    """Registra a chave no SDK uma única vez por processo (idempotente)."""
    global _sdk_inicializado
    if _sdk_inicializado:
        return
    set_default_openai_key(
        settings.OPENAI_API_KEY, use_for_tracing=settings.TRACING_HABILITADO
    )
    _sdk_inicializado = True


def _reiniciar_sdk_para_testes() -> None:
    """Permite que os testes verifiquem a idempotência de ``inicializar_sdk``."""
    global _sdk_inicializado
    _sdk_inicializado = False


def _causa_raiz(exc: BaseException) -> BaseException:
    """Desembrulha o UserError com que o SDK envolve exceções levantadas dentro de tools."""
    return (
        exc.__cause__
        if isinstance(exc, UserError) and exc.__cause__ is not None
        else exc
    )


def _motivo(exc: InputGuardrailTripwireTriggered) -> str:
    info = exc.guardrail_result.output.output_info or {}
    return str(info.get("motivo") or "entrada bloqueada pelo guardrail")


def _violacoes(exc: OutputGuardrailTripwireTriggered) -> list[str]:
    info = exc.guardrail_result.output.output_info or {}
    return list(info.get("violacoes") or [])


def _mensagem_inicial(contexto: ContextoAtendimento) -> str:
    """Turno 1. Os números entram só para registro no histórico: as tools leem o contexto."""
    dados = json.dumps(contexto.paciente.model_dump(), ensure_ascii=False)
    return (
        f"Novo atendimento {contexto.atendimento_id}. Dados do paciente (já validados e "
        f"disponíveis no contexto): {dados}. Execute a avaliação completa e produza a "
        "recomendação final."
    )


def _completar_contexto(contexto: ContextoAtendimento) -> None:
    """Calcula por ``services`` o que ainda faltar no contexto (sem LLM)."""
    if contexto.avaliacao_risco is None:
        contexto.avaliacao_risco = avaliar_risco(contexto.paciente, contexto.preditor)
    if contexto.resultado_protocolos is None:
        contexto.resultado_protocolos = selecionar_protocolos(
            contexto.paciente, contexto.avaliacao_risco.classificacao
        )


def _montar_resposta(
    contexto: ContextoAtendimento,
    recomendacao: RecomendacaoFinal,
    *,
    origem: str,
    violacoes: list[str] | None = None,
    motivo: str | None = None,
) -> RespostaAtendimento:
    """Resposta final: valores do contexto + ações/explicação da recomendação."""
    _completar_contexto(contexto)
    resposta = RespostaAtendimento(
        atendimento_id=contexto.atendimento_id,
        gerado_em=datetime.now(timezone.utc),
        paciente=contexto.paciente,
        avaliacao_risco=contexto.avaliacao_risco,
        protocolos=contexto.resultado_protocolos.protocolos,
        sinais_de_atencao=contexto.resultado_protocolos.sinais_de_atencao,
        acoes_operacionais=list(recomendacao.acoes_operacionais),
        explicacao=recomendacao.explicacao,
        cadeia_agentes=list(contexto.cadeia_agentes),
        origem=origem,
        violacoes_guardrail=list(violacoes or []),
        motivo_fallback=motivo,
    )
    logger.info(
        "fim do atendimento | id=%s | origem=%s | p=%.4f %s | protocolos=%s",
        resposta.atendimento_id,
        resposta.origem,
        resposta.avaliacao_risco.probabilidade,
        resposta.avaliacao_risco.classificacao,
        [p.id for p in resposta.protocolos],
    )
    return resposta


def _resposta_fallback(
    contexto: ContextoAtendimento, motivo: str, violacoes: list[str] | None = None
) -> RespostaAtendimento:
    """Recomendação determinística quando o fluxo com LLM falha (sempre segura)."""
    logger.warning(
        "fallback determinístico | atendimento=%s | motivo=%s | violacoes=%s",
        contexto.atendimento_id,
        motivo,
        violacoes or [],
    )
    _completar_contexto(contexto)
    recomendacao = montar_recomendacao_deterministica(
        contexto.avaliacao_risco, contexto.resultado_protocolos
    )
    return _montar_resposta(
        contexto,
        recomendacao,
        origem="fallback_deterministico",
        violacoes=violacoes,
        motivo=motivo,
    )


async def executar_atendimento(
    paciente: DadosPaciente,
    *,
    pergunta: str | None = None,
    contexto: ContextoAtendimento | None = None,
    sessao: Session | None = None,
    usar_llm: bool = True,
    hooks: RunHooks | None = None,
    settings: Settings | None = None,
) -> RespostaAtendimento:
    """Executa um turno do atendimento (novo atendimento ou pergunta de acompanhamento)."""
    if contexto is None:
        contexto = ContextoAtendimento(
            atendimento_id=uuid4().hex, paciente=paciente, preditor=obter_preditor()
        )
    # A cadeia é do turno: cada chamada recomeça no Orquestrador (R10.4).
    contexto.cadeia_agentes = ["Orquestrador"]
    logger.info(
        "início do atendimento | id=%s | usar_llm=%s | acompanhamento=%s",
        contexto.atendimento_id,
        usar_llm,
        pergunta is not None,
    )

    if not usar_llm:
        _completar_contexto(contexto)
        recomendacao = montar_recomendacao_deterministica(
            contexto.avaliacao_risco, contexto.resultado_protocolos
        )
        return _montar_resposta(contexto, recomendacao, origem="sem_llm")

    settings = settings or obter_settings()
    # Checado antes de qualquer chamada ao SDK; a mensagem nunca inclui a chave.
    if not settings.openai_configurado:
        raise ConfiguracaoError(MENSAGEM_SEM_CHAVE)
    inicializar_sdk(settings)

    entrada = pergunta if pergunta is not None else _mensagem_inicial(contexto)
    # A ordem dos except importa: os tipos específicos são subclasses de
    # AgentsException, assim como UserError, que vem por último.
    try:
        resultado = await Runner.run(
            criar_orquestrador(settings),
            input=entrada,
            context=contexto,
            session=sessao,
            max_turns=settings.MAX_TURNS,
            hooks=hooks,
            run_config=RunConfig(
                workflow_name=NOME_WORKFLOW,
                group_id=contexto.atendimento_id,
                tracing_disabled=not settings.TRACING_HABILITADO,
            ),
        )
        # Execução que terminou fora do Planejador → TypeError → fallback.
        recomendacao = resultado.final_output_as(
            RecomendacaoFinal, raise_if_incorrect_type=True
        )
    except InputGuardrailTripwireTriggered as exc:
        raise EntradaBloqueadaError(_motivo(exc)) from exc
    except OutputGuardrailTripwireTriggered as exc:
        return _resposta_fallback(
            contexto, motivo="guardrail_saida", violacoes=_violacoes(exc)
        )
    except (MaxTurnsExceeded, ModelBehaviorError, ModelRefusalError, TypeError) as exc:
        return _resposta_fallback(contexto, motivo=type(exc).__name__)
    except (
        openai.APIConnectionError,
        openai.RateLimitError,
        openai.APITimeoutError,  # subclasse de APIConnectionError; listada por legibilidade
        openai.InternalServerError,
    ) as exc:
        return _resposta_fallback(contexto, motivo=type(exc).__name__)
    except UserError as exc:
        causa = _causa_raiz(exc)
        if isinstance(causa, ErroFluxoAgentes):
            return _resposta_fallback(contexto, motivo="fluxo_fora_de_ordem")
        if isinstance(causa, ModeloIndisponivelError):
            raise causa from exc  # CLI → exit 2
        raise  # UserError de configuração do SDK → CLI exit 4

    return _montar_resposta(contexto, recomendacao, origem="agentes")


_runner_sync: asyncio.Runner | None = None


def _obter_runner_sync() -> asyncio.Runner:
    """Event loop único por processo para a versão síncrona.

    O SDK reaproveita um cliente ``AsyncOpenAI`` global, cujas conexões HTTP
    ficam presas ao loop em que foram abertas. Com um ``asyncio.run`` (loop novo)
    por turno, o 2º turno do modo interativo falhava com
    ``RuntimeError: Event loop is closed``.
    """
    global _runner_sync
    if _runner_sync is None:
        _runner_sync = asyncio.Runner()
        atexit.register(_runner_sync.close)
    return _runner_sync


def executar_atendimento_sync(paciente: DadosPaciente, **kwargs) -> RespostaAtendimento:
    """Versão síncrona para a CLI e scripts (todos os turnos no mesmo event loop)."""
    return _obter_runner_sync().run(executar_atendimento(paciente, **kwargs))
