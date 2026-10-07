"""Parâmetros de rota compartilhados entre os routers da API."""

from typing import Annotated

from fastapi import Path

from domain.schemas import PACIENTE_ID_PATTERN

PacienteIdPath = Annotated[
    str,
    Path(
        pattern=PACIENTE_ID_PATTERN,
        description="ID do paciente (letras, números, _ e -; até 64 caracteres)",
    ),
]
