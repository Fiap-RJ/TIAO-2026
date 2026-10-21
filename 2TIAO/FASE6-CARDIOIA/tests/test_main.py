"""
Testes da CLI (``main.main(argv)``)
===================================

Códigos de saída e saídas da CLI sem LLM (R6.3, R14.2, R15.1, R16.1, CA4,
CA5). O loop interativo é exercitado com o pipeline substituído por um stub,
sem rede.
"""

import io
import json

import pytest

import main as cli
from core.erros import EntradaBloqueadaError
from domain.schemas import RespostaAtendimento


@pytest.fixture(autouse=True)
def ambiente(settings_limpas, monkeypatch, tmp_path):
    # configurar_logging(force=True) trocaria os handlers do pytest; não é o alvo aqui.
    monkeypatch.setattr(cli, "configurar_logging", lambda nivel: None)
    settings_limpas.setenv("SESSIONS_DB_PATH", str(tmp_path / "sessoes.db"))
    return settings_limpas


def _gravar(tmp_path, dados) -> str:
    caminho = tmp_path / "paciente.json"
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    return str(caminho)


def test_sem_llm_com_novo_caso(capsys):
    assert cli.main(["--sem-llm"]) == 0
    saida = capsys.readouterr().out
    assert "CLASSIFICAÇÃO: ALTO" in saida
    posicoes = [saida.index(f"[{i}]") for i in ("P02", "P05", "P08", "P10")]
    assert posicoes == sorted(posicoes)
    assert "[P01]" not in saida
    for variavel in (
        "tempo_espera=75",
        "fc_media=118",
        "spo2_media=89",
        "eventos_24h=5",
    ):
        assert variavel in saida
    assert "ORIGEM: sem_llm" in saida
    assert "AGENTES:" not in saida
    assert "Aviso: o CardioIA" in saida


def test_json_e_resposta_valida(capsys):
    assert cli.main(["--sem-llm", "--json"]) == 0
    resposta = RespostaAtendimento.model_validate_json(capsys.readouterr().out)
    assert resposta.origem == "sem_llm"
    assert resposta.avaliacao_risco.probabilidade >= 0.70
    assert [p.id for p in resposta.protocolos] == ["P02", "P05", "P08", "P10"]


@pytest.mark.parametrize(
    ("alteracao", "campo"),
    [
        ({"remover": "fc_media"}, "fc_media"),
        ({"peso": 80}, "peso"),
        ({"spo2_media": 150}, "spo2_media"),
        ({"fc_media": True}, "fc_media"),
    ],
)
def test_paciente_invalido_sai_com_1(
    tmp_path, capsys, novo_caso_dict, alteracao, campo
):
    dados = dict(novo_caso_dict)
    if "remover" in alteracao:
        del dados[alteracao["remover"]]
    else:
        dados.update(alteracao)
    assert cli.main(["--sem-llm", "--paciente", _gravar(tmp_path, dados)]) == 1
    assert campo in capsys.readouterr().err


@pytest.mark.parametrize("conteudo", ["[1, 2]", "{nao e json"])
def test_arquivo_invalido_sai_com_1(tmp_path, conteudo):
    caminho = tmp_path / "paciente.json"
    caminho.write_text(conteudo, encoding="utf-8")
    assert cli.main(["--sem-llm", "--paciente", str(caminho)]) == 1


def test_arquivo_inexistente_sai_com_1(tmp_path):
    assert cli.main(["--sem-llm", "--paciente", str(tmp_path / "nada.json")]) == 1


def test_max_turns_invalido_sai_com_2(ambiente, capsys):
    ambiente.setenv("MAX_TURNS", "abc")
    assert cli.main(["--sem-llm"]) == 2
    assert "MAX_TURNS" in capsys.readouterr().err


def test_modelo_ausente_sai_com_2(ambiente, tmp_path, capsys):
    ambiente.setenv("MODELO_PATH", str(tmp_path / "inexistente.joblib"))
    assert cli.main(["--sem-llm"]) == 2
    assert "notebook" in capsys.readouterr().err


def test_sem_chave_no_modo_llm_sai_com_2(capsys):
    assert cli.main([]) == 2
    erro = capsys.readouterr().err
    assert "src/.env" in erro
    assert "--sem-llm" in erro


def test_interativo_com_sem_llm_sai_com_1(capsys):
    assert cli.main(["--interativo", "--sem-llm"]) == 1
    assert "--interativo exige o modo com LLM" in capsys.readouterr().err


def test_opcao_desconhecida_sai_com_2_do_argparse():
    with pytest.raises(SystemExit) as exc:
        cli.main(["--opcao-inexistente"])
    assert exc.value.code == 2


def test_entrada_bloqueada_sai_com_3(ambiente, monkeypatch, capsys):
    ambiente.setenv("OPENAI_API_KEY", "chave-falsa-de-teste")

    def bloquear(*args, **kwargs):
        raise EntradaBloqueadaError("pedido de dose")

    monkeypatch.setattr(cli, "executar_atendimento_sync", bloquear)
    assert cli.main([]) == 3
    assert "pedido de dose" in capsys.readouterr().err


def test_erro_inesperado_sai_com_4(ambiente, monkeypatch):
    ambiente.setenv("OPENAI_API_KEY", "chave-falsa-de-teste")

    def quebrar(*args, **kwargs):
        raise RuntimeError("falha não prevista")

    monkeypatch.setattr(cli, "executar_atendimento_sync", quebrar)
    assert cli.main([]) == 4


def test_loop_interativo(ambiente, monkeypatch, capsys):
    """Reaproveita contexto e sessão, ignora linhas vazias, segue após bloqueio e encerra com 'sair'."""
    import pipeline

    ambiente.setenv("OPENAI_API_KEY", "chave-falsa-de-teste")
    chamadas = []

    def falso(paciente, **kwargs):
        chamadas.append(kwargs)
        if kwargs.get("pergunta") == "qual dose aplicar?":
            raise EntradaBloqueadaError("pedido de dose")
        return pipeline.executar_atendimento_sync(
            paciente, contexto=kwargs["contexto"], usar_llm=False
        )

    monkeypatch.setattr(cli, "executar_atendimento_sync", falso)
    monkeypatch.setattr(
        "sys.stdin", io.StringIO("\n  \nqual dose aplicar?\npor que?\nsair\n")
    )
    assert cli.main(["--interativo"]) == 0

    saida = capsys.readouterr().out
    assert "Pergunta bloqueada: pedido de dose" in saida
    assert [c.get("pergunta") for c in chamadas] == [
        None,
        "qual dose aplicar?",
        "por que?",
    ]
    contextos = {id(c["contexto"]) for c in chamadas}
    sessoes = {id(c["sessao"]) for c in chamadas}
    assert len(contextos) == 1 and len(sessoes) == 1
    assert chamadas[0]["sessao"].session_id == chamadas[0]["contexto"].atendimento_id


def test_loop_interativo_encerra_com_eof(ambiente, monkeypatch):
    import pipeline

    ambiente.setenv("OPENAI_API_KEY", "chave-falsa-de-teste")
    monkeypatch.setattr(
        cli,
        "executar_atendimento_sync",
        lambda paciente, **kw: pipeline.executar_atendimento_sync(
            paciente, contexto=kw["contexto"], usar_llm=False
        ),
    )
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert cli.main(["--interativo"]) == 0
