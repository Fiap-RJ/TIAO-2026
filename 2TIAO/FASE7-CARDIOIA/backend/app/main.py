"""Ponto de entrada do backend integrador CardioIA."""

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from . import db
from services.chat_service import chat_service
from .config import CORS_ORIGINS, DEVICE_KEY
from .dependencies import authorize_patient, current_user, require_doctor
from .evaluator import evaluate, needs_automatic_evaluation
from .schemas import ChatRequest, LeituraEntrada, LoginRequest
from .security import create_token, hash_password


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.initialize()
    yield


app = FastAPI(title="CardioIA — API integradora", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def patient_or_404(paciente_id: str):
    paciente = db.patient_by_id(paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return paciente


def patient_view(paciente):
    return {"id": paciente["id"], "nome": paciente["nome"], "idade": paciente["idade"], "leito": paciente["leito"]}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/login")
def login(payload: LoginRequest):
    usuario = db.user_by_email(payload.email)
    if not usuario or hash_password(payload.senha, usuario["salt"]) != usuario["senha_hash"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    dados = {"id": usuario["id"], "nome": usuario["nome"], "perfil": usuario["perfil"], "paciente_id": usuario["paciente_id"]}
    return {"access_token": create_token(dados), "token_type": "bearer", "usuario": dados}


@app.get("/api/pacientes")
def list_patients(usuario: dict = Depends(current_user)):
    resultado = []
    for paciente in db.patients_for(usuario):
        leituras = db.readings(paciente["id"], limit=1)
        avaliacao = db.latest_assessment(paciente["id"])
        resultado.append({
            **patient_view(paciente),
            "ultima_leitura": dict(leituras[-1]) if leituras else None,
            "probabilidade": avaliacao["avaliacao_risco"]["probabilidade"] if avaliacao else None,
            "classificacao": avaliacao["avaliacao_risco"]["classificacao"] if avaliacao else None,
            "avaliado_em": avaliacao["gerado_em"] if avaliacao else None,
        })
    return resultado


@app.get("/api/pacientes/{paciente_id}/status")
def patient_status(paciente_id: str, usuario: dict = Depends(current_user)):
    authorize_patient(paciente_id, usuario)
    paciente = patient_or_404(paciente_id)
    return {"paciente": patient_view(paciente), "leituras": [dict(l) for l in db.readings(paciente_id)], "avaliacao": db.latest_assessment(paciente_id)}


@app.post("/api/pacientes/{paciente_id}/avaliar")
def evaluate_patient(paciente_id: str, usuario: dict = Depends(current_user)):
    require_doctor(usuario)
    patient_or_404(paciente_id)
    return evaluate(paciente_id)


@app.post("/api/leituras", status_code=status.HTTP_201_CREATED)
def receive_reading(payload: LeituraEntrada, x_device_key: Annotated[str | None, Header()] = None):
    if not DEVICE_KEY:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DEVICE_KEY não configurada no servidor.")
    if x_device_key != DEVICE_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Dispositivo não autorizado.")
    patient_or_404(payload.paciente_id)
    leitura = payload.normalized()
    db.add_reading(leitura)
    avaliacao = evaluate(leitura["paciente_id"]) if needs_automatic_evaluation(leitura) else None
    return {"recebida": True, "reavaliado": avaliacao is not None}


@app.post("/api/chat")
def chat(payload: ChatRequest, usuario: dict = Depends(current_user)):
    if payload.paciente_id:
        authorize_patient(payload.paciente_id, usuario)
        patient_or_404(payload.paciente_id)
    resultado = chat_service.processar_mensagem(payload.mensagem, payload.sessao_id)
    return {
        "resposta": resultado["resposta"],
        "sessao_id": resultado.get("session_id") or "local",
        "origem": resultado["origem"],
    }
