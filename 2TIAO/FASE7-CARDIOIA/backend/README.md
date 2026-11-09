# Backend integrador — CardioIA

API FastAPI que recebe telemetria MicroPython, persiste dados em SQLite e usa o
modelo de risco da Fase 6 para devolver recomendações ao Web e Mobile.

## Executar localmente

```bash
cd FASE7-CARDIOIA/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Consulte `http://localhost:8000/docs`. As contas demo são
`medico@cardioia.com` e `paciente@cardioia.com`, ambas com a senha
`cardioia`. Configure `DEVICE_KEY` igual no Render e em `iot/main.py`.

## Deploy

O [`render.yaml`](render.yaml) define o serviço. No painel do Render, defina
`DEVICE_KEY`, `CORS_ORIGINS` com a URL da Vercel e, se disponíveis, as
credenciais Watson/OpenAI. Nunca envie o arquivo `.env` ao repositório.
