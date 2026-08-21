FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o backend (inclui services/pii_redaction.py)
COPY src/backend/ /app/

# Copia o JSON de dados genéticos para ingestão
COPY proposta_estrutura_de_dados.json /data/proposta_estrutura_de_dados.json

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
