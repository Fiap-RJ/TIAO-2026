from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    senha: str


class LeituraEntrada(BaseModel):
    paciente_id: str
    temperatura: float = Field(ge=0, le=45)
    fc: float = Field(ge=20, le=250)
    spo2: float = Field(ge=50, le=100)
    estado: Literal["normal", "atencao", "critico"] | None = None
    ts: datetime | int | None = None

    def normalized(self) -> dict:
        estado = self.estado or ("critico" if self.fc > 120 or self.fc < 50 or self.temperatura > 38 else "atencao" if self.fc > 100 or self.temperatura >= 37.5 else "normal")
        instante = datetime.fromtimestamp(self.ts, timezone.utc) if isinstance(self.ts, int) else self.ts or datetime.now(timezone.utc)
        return {"paciente_id": self.paciente_id, "temperatura": self.temperatura, "fc": self.fc, "spo2": self.spo2, "estado": estado, "ts": instante.isoformat().replace("+00:00", "Z")}


class ChatRequest(BaseModel):
    mensagem: str = Field(min_length=1, max_length=2000)
    paciente_id: str | None = None
    sessao_id: str | None = None
