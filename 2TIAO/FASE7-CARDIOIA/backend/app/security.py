"""JWT HMAC mínimo para os dois usuários de demonstração."""

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from fastapi import HTTPException, status

from .config import JWT_SECRET


def _b64(valor: bytes) -> str:
    return base64.urlsafe_b64encode(valor).rstrip(b"=").decode()


def _unb64(valor: str) -> bytes:
    return base64.urlsafe_b64decode(valor + "=" * (-len(valor) % 4))


def hash_password(senha: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 100_000).hex()


def create_token(usuario: dict[str, Any]) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64(
        json.dumps(
            {"sub": usuario["id"], "perfil": usuario["perfil"], "paciente_id": usuario["paciente_id"], "exp": int(time.time()) + 60 * 60 * 8},
            separators=(",", ":"),
        ).encode()
    )
    assinatura = _b64(hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{assinatura}"


def decode_token(token: str) -> dict[str, Any]:
    try:
        header, payload, assinatura = token.split(".")
        esperado = _b64(hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(assinatura, esperado):
            raise ValueError("assinatura inválida")
        dados = json.loads(_unb64(payload))
        if int(dados["exp"]) < time.time():
            raise ValueError("token expirado")
        return dados
    except (ValueError, KeyError, json.JSONDecodeError) as erro:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.") from erro
