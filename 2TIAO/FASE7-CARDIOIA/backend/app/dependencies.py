from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação obrigatória.")
    return decode_token(credentials.credentials)


def authorize_patient(paciente_id: str, usuario: dict) -> None:
    if usuario["perfil"] == "paciente" and usuario["paciente_id"] != paciente_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem acesso a este paciente.")


def require_doctor(usuario: dict) -> None:
    if usuario["perfil"] != "medico":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Esta ação requer perfil médico.")
