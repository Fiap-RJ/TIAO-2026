FROM paddlepaddle/paddle:3.2.0

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências Python
COPY scripts/docker/paddle-ocr/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia a aplicação
COPY scripts/docker/paddle-ocr/app.py .

ENV DISABLE_MODEL_SOURCE_CHECK=true
ENV PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=true
ENV DEBUG=false

EXPOSE 8100

# Healthcheck: Test /health endpoint
HEALTHCHECK --interval=15s --timeout=10s --retries=5 --start-period=90s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/health')"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8100"]

