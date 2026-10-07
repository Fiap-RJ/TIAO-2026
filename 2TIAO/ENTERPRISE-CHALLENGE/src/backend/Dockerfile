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

COPY src/backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Healthcheck: Test /health endpoint
# Uses RENDER_EXTERNAL_URL if set (Render deployment), else localhost (local dev)
HEALTHCHECK --interval=15s --timeout=10s --retries=5 --start-period=90s \
  CMD sh -c 'if [ -n "$RENDER_EXTERNAL_URL" ]; then \
    python -c "import urllib.request; urllib.request.urlopen(\"https://$RENDER_EXTERNAL_URL/health\", timeout=5)"; \
  else \
    python -c "import urllib.request; urllib.request.urlopen(\"http://localhost:8000/health\", timeout=5)"; \
  fi'

CMD ["/app/entrypoint.sh"]
