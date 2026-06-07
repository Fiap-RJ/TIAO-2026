# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Orbital RAG: Assistente Inteligente para Monitoramento de Anomalias Espaciais

## Grupo: Squad AI Engineering

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/arthur-alentejo">Arthur Guimarães Alentejo</a>
- <a href="https://www.linkedin.com/in/michaelrodriguess">Michael Rodrigues</a>
- <a href="https://www.linkedin.com/in/nathalia-vasconcelos-18a390292/">Nathalia Vasconcelos</a> 

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="#">Caique (CaiqueFiap-2026)</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godói</a>

---

## 📜 Descrição

O projeto resolve o problema da **dispersão e complexidade dos dados de monitoramento espacial**. Atualmente, informações sobre asteroides próximos à Terra, tempestades solares, tempestades geomagnéticas e detritos orbitais estão espalhadas em múltiplas APIs da NASA (NeoWs, DONKI) e portais como Space-Track, tornando a análise de risco lenta e fragmentada.

A nossa solução é um **assistente conversacional baseado em RAG (Retrieval-Augmented Generation)** que consolida eventos espaciais em tempo real e permite ao usuário interagir em linguagem natural — perguntando sobre riscos de colisão, tempestades solares e impactos em infraestrutura orbital, com respostas fundamentadas em dados reais da NASA.

## 📺 Apresentação do Projeto

* **Global Solution 1:** [Link para o YouTube](#)

---

## 🏗 Arquitetura da Solução

```
[NASA NeoWs] [NASA DONKI] [Space-Track] [News+PDFs]
      │            │            │              │
      └────────────┴────────────┴──────────────┘
                           │
                    collectors/ (Python)
                           │
                    normalizer.py
                           │
               ┌───────────┴────────────┐
               │                        │
        context_data.json         vectorstore/
               │                  (futuro)
               └───────────┬────────────┘
                            │
                   LangGraph Agent (NestJS)
                            │
                    LLM (Google Gemini)
                            │
                   POST /api/chat
                            │
              ┌─────────────┴─────────────┐
              │                           │
          Dashboard                    Chat UI
```

### Pipeline RAG (LangGraph)

```
[retrieveData] → [generateResponse] → [validator] → Resposta
       │                  │                  │
  Carrega JSON       LLM (Gemini       Guardrail
  + sanitiza        3.1 Flash Lite)    anti-alucinação
```

### Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Orquestração de Agentes | LangGraph (StateGraph) — `@langchain/langgraph` |
| LLM | Google Gemini 3.1 Flash Lite Preview |
| Backend / API | NestJS + TypeScript (Clean Architecture) |
| Engenharia de Dados | Python (requests, python-dotenv) |
| Containerização | Docker Compose |
| Gerenciamento de Deps (Data) | Poetry |
| Fontes de Dados | NASA NeoWs, NASA DONKI (CME, GST, SEP) |

---

## 🧠 Justificativa Técnica

### Escolha do LLM

- **Google Gemini 3.1 Flash Lite Preview**: Escolhido pelo custo-benefício para tarefas de síntese e interpretação de dados estruturados. Latência baixa, suporte nativo a português e custo zero na tier gratuita — ideal para um projeto acadêmico com múltiplas iterações.

### Arquitetura RAG com LangGraph

O motor cognitivo é um **StateGraph** com 3 nós:

1. **`retrieveData`** — Carrega `context_data.json`, sanitiza e mapeia campos para entidades de domínio
2. **`generateResponse`** — Constrói prompt determinístico (contexto + pergunta) e invoca o LLM
3. **`validator`** — Guardrail anti-alucinação: verifica se a resposta referencia dados reais do JSON

Se a validação falha (alucinação detectada), o grafo retorna ao processamento via **aresta condicional**, garantindo resiliência.

### Pipeline de Dados (Python)

A coleta de dados é desacoplada do backend. Scripts Python coletam dados de múltiplas APIs da NASA e normalizam para um formato unificado (`context_data.json`), que é consumido pelo backend via volume Docker.

Mapeamento NeoWs → JSON:

| Campo NASA | Campo normalizado |
|---|---|
| `neo_reference_id` | `id_evento` |
| `name` | `nome` |
| `close_approach_data[0].close_approach_date` | `data_aproximacao` |
| `close_approach_data[0].miss_distance.kilometers` | `distancia_terra_km` |
| `is_potentially_hazardous_asteroid` | `risco_colisao` |
| *(gerado pelo normalizer)* | `resumo_alerta` |

---

## 📁 Estrutura de Pastas

```
Global-Solution-1/
├── assets/                        # Logo e diagramas
├── backend/                       # Core do motor RAG (NestJS)
│   ├── src/
│   │   ├── domain/entities/       # SpaceEvent entity
│   │   ├── application/
│   │   │   ├── dtos/              # ChatDto
│   │   │   ├── ports/             # Interfaces (Repository, Agent)
│   │   │   └── use-cases/         # ProcessChatMessageUseCase
│   │   ├── infrastructure/
│   │   │   ├── repositories/      # FileSpaceEventRepository
│   │   │   └── services/          # LangGraphAgentService
│   │   └── presentation/
│   │       └── controllers/       # ChatController (POST /api/chat)
│   ├── context_data.json          # Dados espaciais (injetados pelo pipeline)
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── package.json
└── orbital-rag-data/              # Pipeline de engenharia de dados (Python)
    ├── collectors/
    │   ├── neo_collector.py       # NASA NeoWs — Asteroides
    │   └── donki_collector.py     # NASA DONKI — CME, GST, SEP
    ├── processors/
    │   └── normalizer.py          # Normaliza → context_data.json
    ├── output/
    │   └── context_data.json      # JSON gerado com dados reais
    ├── main.py                    # Pipeline principal
    ├── pyproject.toml             # Dependências (Poetry)
    └── Makefile                   # Shortcuts de execução
```

---

## 🔧 Como Executar

### Opção 1: Docker Compose (recomendado)

```bash
# 1. Configure a API key do Gemini
cp backend/.env.example backend/.env
# Edite o .env com sua GOOGLE_API_KEY

# 2. Suba o backend
cd backend
docker compose up --build

# Resultado:
#   API: http://localhost:3000
```

### Opção 2: Pipeline de Dados (Python)

```bash
# 1. Instale dependências
cd orbital-rag-data
make install

# 2. Configure as credenciais da NASA
# Edite o .env com sua NASA_API_KEY

# 3. Execute a coleta
make run

# 4. Copie os dados para o backend
make copy
```

### Comandos Make (orbital-rag-data/)

| Comando | O que faz |
|---------|-----------|
| `make install` | Instala dependências via Poetry |
| `make run` | Executa o pipeline completo (coleta + normalização) |
| `make clean` | Remove o JSON gerado |
| `make copy` | Copia output para `backend/context_data.json` |

---

## 🔌 Contrato de API

### `POST /api/chat`

**Request:**
```json
{
  "message": "Quais asteroides oferecem risco de colisão esta semana?"
}
```

**Response:**
```json
{
  "reply": "De acordo com os dados atuais, o asteroide (2013 NF19) é classificado como potencialmente perigoso pela NASA, mas sua aproximação ocorre a distância segura de 59.259.950 km.",
  "source_data": [
    "(2013 NF19) - Risco: true",
    "510190 (2011 CX7) - Risco: false"
  ]
}
```

### Contrato de Dados (`context_data.json`)

```json
[
  {
    "id_evento": "NEO-2510190",
    "tipo": "Asteroide",
    "nome": "510190 (2011 CX7)",
    "data_aproximacao": "2026-06-14",
    "distancia_terra_km": 16870305,
    "risco_colisao": false,
    "resumo_alerta": "Asteroide 510190 (2011 CX7) com passagem prevista a 16,870,305 km. Sem risco de impacto identificado."
  }
]
```

---

## 🗃 Histórico de Lançamentos

* **0.1.0 - 07/06/2026** — Global Solution 1: Pipeline de coleta de dados NASA (NeoWs + DONKI), normalização automatizada, backend RAG com LangGraph + Gemini, Docker Compose end-to-end.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
