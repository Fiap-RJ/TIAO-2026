# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Genera Intelligence: RAG Multimodelo para Laudos Genéticos (Sprint 2)

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

## ⚠️ Nota Técnica Arquitetural (Sprint 2)
Para a avaliação desta etapa focada em Inteligência Artificial, a equipe adotou uma estratégia de mitigação de risco no pipeline de ingestão. Em vez de executar o OCR (Textract) em tempo real nos arquivos PDF de origem, **os laudos foram previamente convertidos e padronizados no arquivo `proposta_estrutura_de_dados.json`**. 

Esta decisão permite que a equipe concentre todos os esforços no que realmente importa nesta Sprint: a **implementação do motor RAG, a orquestração de múltiplos agentes via LangGraph e a engenharia de prompts**, garantindo respostas semânticas altamente precisas e ancoradas em dados estruturados.

---

## 📜 Descrição
O projeto visa resolver o gargalo de interpretação de dados genéticos do produto Genera (Grupo Dasa). Atualmente, os laudos são entregues em arquivos PDF extensos e repletos de terminologias técnicas, o que dificulta a compreensão do paciente e a tomada de decisão ágil pelo médico. 

A nossa solução é uma camada de inteligência baseada em **RAG (Retrieval-Augmented Generation)**. Através de um assistente conversacional inteligente, o usuário pode "conversar" com o seu DNA, recebendo explicações em linguagem simples, recomendações personalizadas e visualizações intuitivas de riscos e predisposições.

## 📺 Apresentação do Projeto
* **Sprint 2 (Atual - Motor RAG & Agentes):** [Link do YouTube será inserido aqui]
* **Sprint 1 (Fundação e Arquitetura):** [Link para o YouTube](https://youtu.be/mASJnbO3dqo)

---

## 🏗 Arquitetura da Solução

<img src="assets/hld.png" alt="High Level Design">

### Pipeline RAG (LangGraph)

```
[sanitize] → [retrieve] → [generate] → [guardrail] → Resposta
     │             │             │              │
 PII Redaction   FAISS      LLM (Gemini    Valida termos
 (LGPD)         k=3 docs    ou OpenAI)     + disclaimer
```

### Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Orquestração de Agentes | LangGraph (StateGraph) |
| LLM | Google Gemini 2.0 Flash Lite **ou** OpenAI GPT-4o-mini (configurável) |
| Embeddings | Gemini Embedding 001 **ou** OpenAI text-embedding-3-small |
| Vector Store | FAISS (faiss-cpu) |
| API | FastAPI + Uvicorn |
| Frontend | React 19 + Tailwind CSS + Vite |
| Containerização | Docker Compose (backend + frontend + seed) |
| Qualidade | Ruff (lint), Pytest, Eval automatizado |

---

## 🧠 Justificativa Técnica

### Escolha do LLM

O sistema suporta dois providers via variável de ambiente `LLM_PROVIDER`:

- **Google Gemini 2.0 Flash Lite** (default): Escolhido pelo custo-benefício excepcional para tarefas de interpretação textual. O modelo Flash Lite oferece latência baixa (~1s), suporte nativo a português e custo zero na tier gratuita da API — ideal para um projeto acadêmico com múltiplas iterações de teste.

- **OpenAI GPT-4o-mini** (alternativa): Disponível como fallback para cenários onde a API do Google esteja instável ou para comparação de qualidade no eval. O GPT-4o-mini oferece excelente capacidade de seguir instruções complexas (system prompts longos com guardrails).

### Estratégia de Embeddings

- **Gemini Embedding 001** (`models/gemini-embedding-001`): Modelo de embedding multilíngue com 768 dimensões, otimizado para retrieval. Escolhido por ser gratuito, ter excelente performance em português e integrar nativamente com o ecossistema LangChain.

- **OpenAI text-embedding-3-small** (alternativa): 1536 dimensões, disponível quando `LLM_PROVIDER=openai`.

### Escolha do FAISS como Vector Store

O FAISS (Facebook AI Similarity Search) foi escolhido por:
1. **Zero infraestrutura**: Roda localmente como arquivo, sem necessidade de banco de dados externo
2. **Performance**: Busca por similaridade em milhões de vetores em milissegundos
3. **Simplicidade**: Ideal para o volume de dados do projeto (5-50 documentos por laudo)
4. **Portabilidade**: O índice é um arquivo que pode ser versionado ou montado via Docker volume

### Engenharia de Prompts

A estratégia de prompts segue uma arquitetura em camadas:
1. **Prompt Base** (`prompts/base.py`): 8 regras invioláveis aplicadas a toda resposta (disclaimer, grounding, tom)
2. **Prompts Especialistas** (`prompts/specialists.py`): Diretrizes específicas por painel (Nutri, Farma, Fit, Skin, Risco)
3. **Detecção automática**: O sistema identifica o painel relevante pelos metadados dos documentos recuperados e compõe o prompt final dinamicamente

---

## 🛡️ Governança e Segurança

O sistema implementa 5 camadas de segurança:

1. **PII Redaction** — Remove CPF, RG, e-mail, telefone e CEP antes de enviar ao LLM
2. **System Prompt restritivo** — Instrui o modelo a nunca diagnosticar ou prescrever
3. **Prompt especializado** — Reforça tom adequado por tipo de dado genético
4. **Guardrail pós-geração** — Verifica termos proibidos e bloqueia respostas inadequadas
5. **Disclaimer automático** — Garante que toda resposta contenha aviso médico

Documentação completa: [`document/governanca_e_riscos.md`](document/governanca_e_riscos.md)

---

## 📁 Estrutura de Pastas

```
2TIAO/ENTERPRISE CHALLENGE/
├── assets/                     # Diagramas de arquitetura
├── config/                     # Configurações de deploy
├── document/                   # PDFs originais + Relatório de Governança
├── scripts/                    # ETL de limpeza (Textract)
├── proposta_estrutura_de_dados.json  # Dados genéticos estruturados
├── docker-compose.yml          # Orquestração completa (backend + frontend)
├── Makefile                    # Comandos de desenvolvimento
├── pyproject.toml              # Dependências e tooling (Poetry)
└── src/
    ├── backend/                # Core do motor RAG
    │   ├── agents/             # LangGraph: state, nodes, graph builder
    │   │   ├── nodes/          # sanitize, retrieve, generate, guardrail
    │   │   ├── state.py        # Estado tipado (Pydantic BaseModel)
    │   │   └── graph.py        # Builder do grafo
    │   ├── api/routes/         # Endpoints FastAPI
    │   ├── core/               # Config centralizada + factory LLM
    │   ├── domain/             # Schemas Pydantic (DTOs)
    │   ├── eval/               # Avaliação automatizada do agente
    │   ├── prompts/            # System prompts (constantes Python)
    │   └── services/           # Vector store, guardrails, PII redaction
    └── frontend/               # React + Tailwind + Nginx
```

---

## 🔧 Como Executar

### Opção 1: Docker Compose (recomendado)

```bash
# 1. Configure a API key
cp src/backend/.env.example src/backend/.env
# Edite o .env com sua GOOGLE_API_KEY ou OPENAI_API_KEY

# 2. Suba tudo
make up

# Resultado:
#   Frontend: http://localhost:3000
#   API:      http://localhost:8000
#   Swagger:  http://localhost:8000/docs
```

### Opção 2: Desenvolvimento Local

```bash
# 1. Instale dependências
make install

# 2. Configure o .env
cp src/backend/.env.example src/backend/.env

# 3. Popule o banco vetorial
make seed

# 4. Suba o backend
make serve

# 5. (outro terminal) Suba o frontend
make serve-front
```

### Opção 3: Eval do Agente

```bash
make eval
```

---

## 🔌 Contrato de API

### `POST /api/chat/`

**Request:**
```json
{
  "paciente_id": "uuid-123",
  "mensagem": "Como meu corpo reage à cafeína?"
}
```

**Response:**
```json
{
  "resposta": "Com base no seu laudo genético...",
  "fontes": [
    {
      "painel": "Genera Nutri",
      "marcador": "Sensibilidade à Cafeína",
      "gene": "CYP1A2",
      "conclusao_curta": "Metabolismo lento de cafeína"
    }
  ]
}
```

---

## 🗃 Histórico de Lançamentos

* **0.2.0 - 29/05/2026** - Sprint 2: Motor RAG completo, multi-agentes LangGraph, multi-provider (Gemini/OpenAI), interface de Chat, guardrails, PII redaction, eval automatizado, Docker Compose end-to-end.
* **0.1.0 - 24/04/2026** - Sprint 1: Estruturação arquitetural do projeto, definição em AWS e pipeline conceitual de anonimização.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
