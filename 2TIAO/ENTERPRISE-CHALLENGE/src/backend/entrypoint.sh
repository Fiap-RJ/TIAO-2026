#!/bin/sh
# Genera Intelligence — Entrypoint do backend
# Gera o índice FAISS na primeira execução, depois sobe o uvicorn.
set -e

FAISS_PATH="${GENERA_FAISS_PATH:-/app/faiss_index}"

# Verifica se já existe algum índice FAISS nos subdiretórios do provider/modelo
if [ -z "$(find "$FAISS_PATH" -name 'index.faiss' 2>/dev/null)" ]; then
    echo "=== Índice FAISS não encontrado em $FAISS_PATH — gerando agora... ==="
    python -m services.vector_store
    echo "=== Índice FAISS gerado com sucesso ==="
else
    echo "=== Índice FAISS encontrado em $FAISS_PATH — pulando seed ==="
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
