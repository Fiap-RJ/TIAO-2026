import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat

app = FastAPI(
    title="Genera Intelligence API",
    description="Motor RAG e Multi-Agent para Interpretação de Laudos Genéticos (Dasa)",
    version="0.2.0"
)

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["Chat Conversacional"])

@app.get("/health", tags=["Monitoramento"])
def health_check():
    return {"status": "ok", "message": "A API Genera Intelligence está no ar!"}