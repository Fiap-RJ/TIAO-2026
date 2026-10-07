FROM paddlepaddle/paddle:3.2.0

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências Python
COPY docker/paddle-ocr/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia a aplicação
COPY docker/paddle-ocr/app.py .

ENV DISABLE_MODEL_SOURCE_CHECK=true
ENV PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=true

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
