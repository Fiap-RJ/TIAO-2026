# Genera Intelligence — Backend (Sprint 3)

Core do motor RAG, orquestração de agentes via LangGraph e API do dashboard (riscos, ancestralidade,
resumos e histórico).

## Arquitetura

```
backend/
├── main.py              # Bootstrap FastAPI
├── agents/              # LangGraph pipeline
│   ├── state.py         # Estado tipado (Pydantic BaseModel)
│   ├── graph.py         # Builder do grafo
│   └── nodes/           # Nós do pipeline
│       ├── sanitize.py  # PII Redaction (LGPD)
│       ├── retrieve.py  # Busca semântica FAISS
│       ├── generate.py  # Invocação do LLM (Gemini/OpenAI)
│       └── guardrail.py # Validação pós-geração
├── api/routes/          # Endpoints HTTP
│   ├── chat.py              # POST /api/chat/ (persiste no histórico)
│   ├── riscos.py            # GET /api/riscos/ (Sprint 3)
│   ├── ancestralidade.py    # GET /api/ancestralidade/ (Sprint 3)
│   ├── resumos.py           # GET /api/resumos/{relatorio,interacoes}/{paciente_id} (Sprint 3)
│   └── historico.py         # GET /api/historico/{paciente_id} (Sprint 3)
├── core/                # Configuração centralizada
│   ├── config.py        # Pydantic BaseSettings (.env)
│   └── llm.py           # Factory: build_llm() + build_embeddings()
├── data/                 # Banco SQLite do histórico (não versionado — ver .gitignore)
├── domain/              # DTOs
│   └── schemas.py       # ChatRequest/Response, riscos, ancestralidade, resumos, histórico
├── eval/                # Avaliação automatizada
│   ├── cases.py         # Dataset de eval (7 casos)
│   ├── criteria.py      # Funções de critério
│   ├── runner.py        # Orquestrador
│   └── __main__.py      # python -m eval
├── prompts/             # Engenharia de prompts
│   ├── base.py          # SYSTEM_BASE (8 regras invioláveis)
│   └── specialists.py   # AGENT_NUTRI, AGENT_FARMA, AGENT_FIT, AGENT_SKIN, AGENT_RISCO
├── services/            # Infraestrutura
│   ├── vector_store.py  # FAISS: ingestão + carregamento (usado pelo grafo)
│   ├── report_data.py   # Leitura cacheada do JSON estruturado (Sprint 3 — endpoints do dashboard)
│   ├── history_store.py # Persistência SQLite do histórico de interações (Sprint 3)
│   ├── resumo.py        # Geração e cache dos resumos automáticos (Sprint 3)
│   ├── guardrails.py    # Validação de termos proibidos + disclaimers (ampliado na Sprint 3)
│   └── pii_redaction.py # Anonimização (CPF, RG, e-mail, telefone, CEP)
├── Dockerfile           # Build (contexto na raiz do projeto)
├── requirements.txt     # Dependências pip
└── .env.example         # Template de variáveis de ambiente
```

> `report_data.py` é deliberadamente independente de `vector_store.py`: os endpoints do dashboard só
> precisam ler o JSON do relatório, então evitam a dependência pesada de LangChain/FAISS que o
> `vector_store.py` carrega para a ingestão do RAG.

## Configuração Multi-Provider

O sistema suporta Gemini e OpenAI via variável `LLM_PROVIDER`:

```env
# Gemini (default)
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your_key
```

A factory em `core/llm.py` instancia o provider correto. Lazy imports garantem que `langchain-openai` só é carregado quando necessário.

## Comandos

```bash
# Seed do vector store (obrigatório antes de rodar)
make seed

# API com hot-reload
make serve

# Eval do agente
make eval

# Lint
make lint
```

## Grafo LangGraph

```
sanitize → retrieve → generate → guardrail → END
```

| Nó | Responsabilidade |
|----|-----------------|
| `sanitize` | Remove PII do input (LGPD) |
| `retrieve` | Busca semântica no FAISS (k=3) |
| `generate` | Invoca LLM com prompt especializado |
| `guardrail` | Valida resposta + adiciona disclaimer |

## Eval

```bash
cd src/backend && python -m eval
```

Executa 7 casos cobrindo:
- Grounding por painel (Nutri, Farma, Fit, Skin, Risco)
- Guardrails (recusa de diagnóstico)
- Escopo (recusa de perguntas fora do domínio)

## Endpoints do Dashboard (Sprint 3)

| Rota | Responsabilidade |
|------|-------------------|
| `GET /api/riscos/` | Painéis genéticos + escala de risco, com nível normalizado (`baixo`/`moderado`/`atencao`) |
| `GET /api/ancestralidade/` | Composição de ancestralidade (dado simulado — ver `proposta_estrutura_de_dados.json`) |
| `GET /api/resumos/relatorio/{paciente_id}` | Resumo executivo do relatório, cacheado por versão do arquivo de dados |
| `GET /api/resumos/interacoes/{paciente_id}` | Resumo do histórico de interações, cacheado por volume de interações |
| `GET /api/historico/{paciente_id}` | Interações persistidas do paciente, da mais antiga para a mais recente |

Contrato completo (request/response) documentado no [README raiz](../../README.md#-contrato-de-api).

## Persistência de Histórico (Sprint 3)

Cada chamada bem-sucedida a `POST /api/chat/` grava a interação em SQLite via
`services/history_store.py` (tabela `interacoes`: `paciente_id`, `pergunta` já sanitizada,
`resposta`, `fontes` e `criado_em`). A escrita é *best-effort*: uma falha de persistência é logada,
mas não derruba a resposta ao usuário.

- Banco criado automaticamente no primeiro uso — sem migração manual.
- Caminho configurável via `GENERA_DB_PATH` (padrão: `data/history.db`, não versionado — ver `.gitignore` na raiz do repositório).
- Ver `document/governanca_e_riscos.md` (§3.3, R9) para a justificativa LGPD e as limitações conhecidas dessa persistência.

## Variáveis de Ambiente

Todas as configurações são controladas via variáveis de ambiente carregadas do arquivo `.env` (template: `.env.example`).
O sistema suporta múltiplos providers de LLM, embeddings, OCR e persistência — selecionáveis via env vars.

### Providers e Modelos

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `LLM_PROVIDER` | `gemini` | Provider do LLM: `gemini` ou `openai` |
| `LLM_MODEL` | vazio | Modelo específico (vazio = usa default do provider) |
| `EMBEDDINGS_PROVIDER` | `gemini` | Provider de embeddings: `gemini` ou `openai` |
| `EMBEDDINGS_MODEL` | vazio | Modelo de embeddings (vazio = usa default) |
| `JUDGE_PROVIDER` | vazio | Provider do juiz (LLM-as-a-Judge); vazio = usa `LLM_PROVIDER` |
| `JUDGE_MODEL` | vazio | Modelo do juiz (vazio = usa default do `JUDGE_PROVIDER`) |

### Google Gemini

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `GOOGLE_API_KEY` | (secret) | Chave API do Google Gemini (obrigatória se `LLM_PROVIDER=gemini`) |
| `GEMINI_MODEL` | `gemini-3.1-flash-lite` | Modelo Gemini de geração |
| `GEMINI_EMBEDDING_MODEL` | `models/gemini-embedding-001` | Modelo Gemini de embeddings |

### OpenAI

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `OPENAI_API_KEY` | (secret) | Chave API da OpenAI (obrigatória se `LLM_PROVIDER=openai`) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo OpenAI de geração |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Modelo OpenAI de embeddings |

### Parâmetros do LLM

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `LLM_TEMPERATURE` | `0.3` | Temperatura (0.0–1.0): menor = mais determinístico |
| `LLM_MAX_TOKENS` | `2048` | Máximo de tokens na resposta |

### Chat: Limites por Nível de Detalhe

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CHAT_MAX_TOKENS_RESUMIDO` | `400` | Máximo de tokens para modo resumido |
| `CHAT_MAX_TOKENS_DETALHADO` | `1200` | Máximo de tokens para modo detalhado |
| `CHAT_MAX_PALAVRAS_RESUMIDO` | `120` | Máximo de palavras para modo resumido |

### RAG

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `RETRIEVER_K` | `3` | Número de documentos recuperados do FAISS por query |

### OCR (ETL)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `OCR_PROVIDER` | `paddle_local` | Provider de OCR: `paddle_local` (HTTP local) ou `textract` (AWS) |
| `OCR_TOKEN` | (vazio) | Bearer token para autenticação do endpoint `/api/ocr/` |
| `TEXTRACT_REGION` | `us-east-1` | Região AWS Textract (ignorada se `OCR_PROVIDER != textract`) |
| `AWS_ACCESS_KEY_ID` | (vazio) | Credencial AWS (ignorada se `OCR_PROVIDER != textract`) |
| `AWS_SECRET_ACCESS_KEY` | (vazio) | Credencial AWS (ignorada se `OCR_PROVIDER != textract`) |

### Persistência: Camada de Dados

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DB_TYPE` | `sqlite` | Tipo de banco: `sqlite` ou `postgres` |
| `DATABASE_URL` | (vazio) | Connection string Postgres (ex: `postgresql://user:pass@host/db`); obrigatório se `DB_TYPE=postgres` |
| `GENERA_DB_PATH` | `data/history.db` | Caminho do arquivo SQLite (usado se `DB_TYPE=sqlite`) |

### Caminhos de Dados

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `GENERA_DATA_PATH` | `proposta_estrutura_de_dados.json` | Caminho do JSON estruturado de dados genéticos |
| `GENERA_FAISS_PATH` | `faiss_index/` | Diretório do índice FAISS |

Consulte `.env.example` para o template completo com comentários de cada variável.
