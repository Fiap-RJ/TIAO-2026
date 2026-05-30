.PHONY: install dev seed serve serve-front test lint format check up down logs clean help

BACKEND := src/backend
FRONTEND := src/frontend

help: ## Mostra este menu de ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ─── Desenvolvimento Local ───────────────────────────────────────────────────

install: ## Instala dependências (backend + frontend)
	poetry install
	cd $(FRONTEND) && npm ci

dev: ## Ativa o shell do Poetry
	poetry shell

seed: ## Popula o vector store FAISS
	poetry run python $(BACKEND)/services/vector_store.py

serve: ## Sobe a API backend com hot-reload
	poetry run uvicorn main:app --reload --app-dir $(BACKEND)

serve-front: ## Sobe o frontend em modo dev
	cd $(FRONTEND) && npm run dev

test: ## Roda os testes com pytest
	poetry run pytest -v

lint: ## Verifica estilo com ruff
	poetry run ruff check $(BACKEND)

format: ## Formata código com ruff
	poetry run ruff format $(BACKEND)

check: lint test ## Lint + testes (CI local)

eval: ## Roda o eval do agente RAG
	cd $(BACKEND) && poetry run python -m eval

# ─── Docker (experiência completa) ───────────────────────────────────────────

up: ## Sobe todos os serviços (backend + frontend + seed)
	docker compose up --build -d
	@echo ""
	@echo "🚀 Genera Intelligence rodando:"
	@echo "   Frontend: http://localhost:3000"
	@echo "   API:      http://localhost:8000"
	@echo "   Docs:     http://localhost:8000/docs"
	@echo ""

down: ## Para todos os containers
	docker compose down

logs: ## Mostra logs dos containers
	docker compose logs -f

logs-back: ## Mostra logs apenas do backend
	docker compose logs -f backend

# ─── Limpeza ─────────────────────────────────────────────────────────────────

clean: ## Remove caches e artefatos
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	docker compose down -v 2>/dev/null || true
