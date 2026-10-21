"""
CLI do CardioIA — Fase 6
========================

Uso (a partir de ``src/``)::

    python main.py [--paciente CAMINHO_JSON] [--json] [--interativo] [--sem-llm] [--log-level NIVEL]

Códigos de saída:

- 0 sucesso (inclusive com fallback determinístico, sinalizado em ``ORIGEM``);
- 1 entrada ou argumento inválido;
- 2 configuração/ambiente (chave ausente ou inválida, modelo indisponível,
  variável de ambiente inválida). Erros de sintaxe do próprio ``argparse``
  (opção desconhecida) também saem com 2;
- 3 mensagem bloqueada pelo guardrail de entrada;
- 4 erro inesperado.

Nada é lido no import: configuração, logging, modelo e paciente são carregados
dentro do ``try`` de ``main()``, que concentra o mapeamento exceção → código.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from uuid import uuid4

import openai
from agents import SQLiteSession
from pydantic import ValidationError

from agentes.contexto import ContextoAtendimento
from core.config import obter_settings
from core.erros import (
    ConfiguracaoError,
    EntradaBloqueadaError,
    EntradaInvalidaError,
    ModeloIndisponivelError,
)
from core.logging_config import configurar_logging
from domain.schemas import DadosPaciente, RespostaAtendimento
from ml.preditor import obter_preditor
from pipeline import MENSAGEM_SEM_CHAVE, executar_atendimento_sync

logger = logging.getLogger("cardioia.main")

COMANDOS_SAIDA = {"sair", "exit"}


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="CardioIA Fase 6 — predição de pico de risco e recomendação multiagente.",
    )
    parser.add_argument(
        "--paciente",
        type=Path,
        default=None,
        help="JSON do paciente (padrão: data/novo_caso.json da fase)",
    )
    parser.add_argument(
        "--json", action="store_true", help="imprime a resposta em JSON"
    )
    parser.add_argument(
        "--interativo",
        action="store_true",
        help="após a primeira resposta, aceita perguntas de acompanhamento (exige LLM)",
    )
    parser.add_argument(
        "--sem-llm",
        action="store_true",
        help="executa só as regras determinísticas e o modelo, sem OpenAI",
    )
    parser.add_argument(
        "--log-level",
        type=str.upper,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="nível de log (padrão: LOG_LEVEL do .env ou INFO)",
    )
    return parser


def _erro(mensagem: str) -> None:
    """Mensagem de erro para o operador (stderr)."""
    print(f"ERRO: {mensagem}", file=sys.stderr)


def carregar_paciente(caminho: Path) -> DadosPaciente:
    """Lê e valida o JSON do paciente (``FileNotFoundError``, ``JSONDecodeError``,
    ``EntradaInvalidaError`` ou ``ValidationError``)."""
    with caminho.open(encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise EntradaInvalidaError(f"{caminho}: o JSON do paciente deve ser um objeto")
    return DadosPaciente.model_validate(dados)


def _mensagem_validacao(erro: dict) -> str:
    """Traduz os erros mais comuns do Pydantic; os demais mantêm a mensagem original."""
    ctx = erro.get("ctx") or {}
    traducoes = {
        "missing": "campo obrigatório ausente",
        "extra_forbidden": "campo não reconhecido",
        "greater_than_equal": f"deve ser ≥ {ctx.get('ge')}",
        "less_than_equal": f"deve ser ≤ {ctx.get('le')}",
        "float_parsing": "deve ser um número",
        "int_parsing": "deve ser um número inteiro",
        "int_from_float": "deve ser um número inteiro",
        "finite_number": "deve ser um número finito",
    }
    if erro["type"] == "value_error":
        return str(ctx.get("error", erro["msg"]))
    return traducoes.get(erro["type"], erro["msg"])


def _formatar_erros_validacao(exc: ValidationError) -> str:
    linhas = []
    for erro in exc.errors():
        campo = ".".join(str(p) for p in erro["loc"]) or "(objeto)"
        linhas.append(f"  - {campo}: {_mensagem_validacao(erro)}")
    return "\n".join(linhas)


def formatar_resposta(resposta: RespostaAtendimento) -> str:
    """Saída legível no formato do enunciado."""
    av = resposta.avaliacao_risco
    linhas = [
        f"=== CardioIA — Recomendação | atendimento {resposta.atendimento_id[:8]}… ===",
        f"RISCO PREVISTO: {av.probabilidade:.4f} | CLASSIFICAÇÃO: {av.classificacao} | "
        f"PICO PREVISTO: {'sim' if av.pico_risco_previsto else 'não'}",
        "PROTOCOLOS SUGERIDOS:",
    ]
    if resposta.protocolos:
        linhas += [
            f"  - [{p.id}] {p.texto}   ({p.justificativa})" for p in resposta.protocolos
        ]
    else:
        linhas.append("  - nenhum protocolo acionado")
    if resposta.sinais_de_atencao:
        linhas.append(
            "SINAIS DE ATENÇÃO (acima do limiar de risco, abaixo do limiar do protocolo):"
        )
        linhas += [f"  - {s.mensagem}" for s in resposta.sinais_de_atencao]
    if av.avisos:
        linhas.append("AVISOS DO MODELO:")
        linhas += [f"  - {a}" for a in av.avisos]
    linhas.append("AÇÕES OPERACIONAIS:")
    linhas += [
        f"  {i}. {a}" for i, a in enumerate(resposta.acoes_operacionais, start=1)
    ]
    linhas.append(f"EXPLICAÇÃO: {resposta.explicacao}")
    # No modo sem LLM nenhum agente atua; a cadeia só é exibida quando há agentes.
    if resposta.origem != "sem_llm":
        linhas.append(f"AGENTES: {' → '.join(resposta.cadeia_agentes)}")
    origem = resposta.origem
    if resposta.motivo_fallback:
        origem += f" ({resposta.motivo_fallback})"
    linhas.append(f"ORIGEM: {origem}")
    if resposta.violacoes_guardrail:
        linhas.append("VIOLAÇÕES DO GUARDRAIL DE SAÍDA:")
        linhas += [f"  - {v}" for v in resposta.violacoes_guardrail]
    linhas.append(resposta.aviso_legal)
    return "\n".join(linhas)


def _imprimir(resposta: RespostaAtendimento, como_json: bool) -> None:
    print(
        resposta.model_dump_json(indent=2) if como_json else formatar_resposta(resposta)
    )


def _loop_interativo(
    paciente: DadosPaciente,
    contexto: ContextoAtendimento,
    sessao: SQLiteSession,
    como_json: bool,
) -> None:
    """Perguntas de acompanhamento com a mesma sessão e o mesmo contexto."""
    print(
        "\nModo interativo: faça perguntas sobre o atendimento ('sair' para encerrar)."
    )
    while True:
        try:
            pergunta = input("\nVocê> ").strip()
        except EOFError:
            print()
            return
        if not pergunta:
            continue
        if pergunta.lower() in COMANDOS_SAIDA:
            return
        try:
            resposta = executar_atendimento_sync(
                paciente, pergunta=pergunta, contexto=contexto, sessao=sessao
            )
        except EntradaBloqueadaError as exc:
            # Recuperável: mostra o motivo e segue o loop.
            print(f"Pergunta bloqueada: {exc.motivo}")
            continue
        _imprimir(resposta, como_json)


def main(argv: list[str] | None = None) -> int:
    parser = criar_parser()
    args = parser.parse_args(argv)

    # Validação cruzada após o parse: exit 1 (parser.error sairia com 2).
    if args.interativo and args.sem_llm:
        print("--interativo exige o modo com LLM (remova --sem-llm)", file=sys.stderr)
        return 1

    # Logging provisório: garante formato padrão mesmo se a configuração falhar.
    configurar_logging(args.log_level or "INFO")
    try:
        settings = obter_settings()
        if args.log_level is None:
            configurar_logging(settings.LOG_LEVEL)
        caminho = args.paciente or settings.RAIZ_FASE / "data" / "novo_caso.json"
        obter_preditor()  # falha cedo (exit 2) se o artefato estiver ausente
        paciente = carregar_paciente(caminho)

        # Sem chave no modo LLM: falha antes de criar sessão (o pipeline também checa).
        if not args.sem_llm and not settings.openai_configurado:
            raise ConfiguracaoError(MENSAGEM_SEM_CHAVE)

        contexto = sessao = None
        if args.interativo:
            # Contexto e sessão compartilhados entre os turnos do atendimento.
            contexto = ContextoAtendimento(
                atendimento_id=uuid4().hex,
                paciente=paciente,
                preditor=obter_preditor(),
            )
            settings.SESSIONS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            sessao = SQLiteSession(contexto.atendimento_id, settings.SESSIONS_DB_PATH)

        resposta = executar_atendimento_sync(
            paciente, contexto=contexto, sessao=sessao, usar_llm=not args.sem_llm
        )
        _imprimir(resposta, args.json)

        if args.interativo:
            _loop_interativo(paciente, contexto, sessao, args.json)
        return 0

    except (FileNotFoundError, json.JSONDecodeError, EntradaInvalidaError) as exc:
        logger.error("entrada inválida: %s", exc)
        _erro(f"entrada inválida: {exc}")
        return 1
    except ValidationError as exc:
        detalhes = _formatar_erros_validacao(exc)
        logger.warning("paciente inválido:\n%s", detalhes)
        _erro(f"dados do paciente inválidos:\n{detalhes}")
        return 1
    except (ConfiguracaoError, ModeloIndisponivelError) as exc:
        logger.error("%s", exc)
        _erro(str(exc))
        return 2
    except (openai.AuthenticationError, openai.PermissionDeniedError) as exc:
        logger.error("credencial OpenAI recusada (%s)", type(exc).__name__)
        _erro(
            f"a OpenAI recusou a credencial ({type(exc).__name__}); confira OPENAI_API_KEY "
            "em src/.env ou use --sem-llm"
        )
        return 2
    except EntradaBloqueadaError as exc:
        logger.warning("entrada bloqueada: %s", exc.motivo)
        _erro(f"mensagem bloqueada: {exc.motivo}")
        return 3
    except Exception as exc:
        # Última barreira: UserError de configuração do SDK e qualquer falha não prevista.
        logger.exception("erro inesperado")
        _erro(f"erro inesperado ({type(exc).__name__}): {exc}")
        return 4


if __name__ == "__main__":
    sys.exit(main())
