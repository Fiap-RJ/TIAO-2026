# Genera Intelligence — Backend (Sprint 2)

Core do motor RAG e orquestração de agentes via LangGraph.

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
│   └── chat.py          # POST /api/chat/
├── core/                # Configuração centralizada
│   ├── config.py        # Pydantic BaseSettings (.env)
│   └── llm.py           # Factory: build_llm() + build_embeddings()
├── domain/              # DTOs
│   └── schemas.py       # ChatRequest, ChatResponse, FonteDado
├── eval/                # Avaliação automatizada
│   ├── cases.py         # Dataset de eval (7 casos)
│   ├── criteria.py      # Funções de critério
│   ├── runner.py        # Orquestrador
│   └── __main__.py      # python -m eval
├── prompts/             # Engenharia de prompts
│   ├── base.py          # SYSTEM_BASE (8 regras invioláveis)
│   └── specialists.py   # AGENT_NUTRI, AGENT_FARMA, AGENT_FIT, AGENT_SKIN, AGENT_RISCO
├── services/            # Infraestrutura
│   ├── vector_store.py  # FAISS: ingestão + carregamento
│   ├── guardrails.py    # Validação de termos proibidos
│   └── pii_redaction.py # Anonimização (CPF, RG, e-mail, telefone, CEP)
├── Dockerfile           # Build (contexto na raiz do projeto)
├── requirements.txt     # Dependências pip
└── .env.example         # Template de variáveis de ambiente
```

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
