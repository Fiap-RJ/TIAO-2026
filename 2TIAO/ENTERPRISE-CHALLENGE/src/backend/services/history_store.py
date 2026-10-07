"""
Serviço de Persistência de Histórico — Genera Intelligence
============================================================
Persiste as interações entre paciente e agente via camada de persistência abstrata.
Suporta múltiplos backends (SQLite, Postgres) selecionáveis via env var DB_TYPE.

Nota de governança (ver document/governanca_e_riscos.md): a pergunta
armazenada já passou pelo nó de sanitização (remoção de PII) antes de
chegar aqui — ver agents/nodes/sanitize.py — mas o texto da resposta e o
conteúdo genético referenciado ainda são dados sensíveis (LGPD, Art. 5º,
II). O banco é local (SQLite) ou privado (Postgres), não é versionado
(ver .gitignore) e deve ser tratado como dado sensível em qualquer
ambiente real de produção.

Este módulo mantém interface compatível com código legado, delegando
a implementação para o repositório apropriado via factory pattern.
"""

import logging

from services.persistence.factory import get_history_repo

logger = logging.getLogger(__name__)


def inicializar_banco() -> None:
    """Cria a tabela de histórico caso ainda não exista. Idempotente."""
    repo = get_history_repo()
    repo.inicializar()


def salvar_interacao(paciente_id: str, pergunta: str, resposta: str, fontes: list[dict]) -> None:
    """Persiste uma interação pergunta/resposta do paciente com o agente."""
    repo = get_history_repo()
    repo.insert(paciente_id, pergunta, resposta, fontes)


def listar_historico(paciente_id: str, limite: int = 100) -> list[dict]:
    """Retorna as interações do paciente, da mais antiga para a mais recente."""
    repo = get_history_repo()
    return repo.get_by_patient(paciente_id, limite)


def contar_interacoes(paciente_id: str) -> int:
    """Conta quantas interações o paciente já teve com o agente."""
    repo = get_history_repo()
    return repo.count_by_patient(paciente_id)


def excluir_historico_paciente(paciente_id: str) -> bool:
    """Exclui todo o histórico de um paciente específico (Direito de Exclusão - LGPD)."""
    repo = get_history_repo()
    return repo.delete_by_patient(paciente_id)


def aplicar_regra_retencao(dias_retencao: int = 30) -> int:
    """
    Remove interações mais antigas que o período de retenção estabelecido,
    purgando automaticamente os dados expirados.
    """
    repo = get_history_repo()
    return repo.apply_retention_policy(dias_retencao)
