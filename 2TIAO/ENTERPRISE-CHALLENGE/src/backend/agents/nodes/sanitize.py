"""Nó de sanitização — remove PII do input do usuário antes do processamento."""

import json
import logging
import time

from agents.state import AgentState
from services.pii_redaction import sanitizar_input_usuario

logger = logging.getLogger(__name__)


def sanitize(state: AgentState) -> dict:
    """Remove dados pessoais identificáveis da pergunta do paciente."""
    start_time = time.perf_counter()

    pergunta_limpa = sanitizar_input_usuario(state.question)

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "request_id": getattr(state, "request_id", "unknown"),
                "node": "sanitize",
                "latency_ms": latency_ms,
                "status": "success",
            }
        )
    )

    return {"question": pergunta_limpa}
