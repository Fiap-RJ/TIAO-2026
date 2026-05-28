# Genera Intelligence - Backend Core (Sprint 2)

Este diretório contém o coração do ecossistema de Inteligência Artificial da nossa solução, sendo responsável pela ingestão de dados na base vetorial (FAISS), orquestração de agentes dinâmicos via **LangGraph** e integração com os modelos de linguagem do **Google Gemini**.

## 🏗️ Estrutura de Pastas

A arquitetura foi desenhada seguindo os princípios de modularidade e Clean Architecture para separação de responsabilidades:

```text
backend/
├── agents/          # Definição dos grafos e nós do LangGraph (Agente Médico Dasa)
├── api/             # Camada de exposição da aplicação (Rotas e Endpoints FastAPI)
│   └── routes/      # Controladores de rotas (ex: chat.py)
├── core/            # Configurações globais, segurança e variáveis de ambiente (Pydantic V2)
├── domain/          # Entidades de negócio e contratos de dados (Schemas Pydantic)
├── services/        # Serviços de suporte (Conexão com a Base Vetorial FAISS e Embeddings)
├── utils/           # Ferramentas de diagnóstico, testes de busca e validação de LLMs
└── main.py          # Ponto de entrada (Bootstrap) da aplicação FastAPI

```

## 🚀 Como Executar Localmente

Siga os passos abaixo para configurar o ambiente virtual, preparar os dados e rodar o servidor de desenvolvimento:

### 1. Pré-requisitos

Certifique-se de ter o Python 3.10 ou superior instalado na sua máquina.

### 2. Configuração do Ambiente Virtual

Navegue até a pasta `src/backend` no seu terminal e execute:

```bash
# Criação do ambiente virtual
python3 -m venv .venv

# Ativação do ambiente (Linux/macOS)
source .venv/bin/activate

# Ativação do ambiente (Windows)
.venv\Scripts\activate

```

### 3. Instalação de Dependências

Com o ambiente virtual ativo, instale as bibliotecas necessárias:

```bash
pip install --no-cache-dir -r requirements.txt

```

### 4. Configuração das Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz da pasta `backend/` e adicione sua chave de API do Google Studio:

```env
GOOGLE_API_KEY=sua_chave_api_aqui

```

### 5. Ingestão de Dados (Criação do Banco Vetorial)

Antes de rodar a API, é necessário processar o laudo genético (`proposta_estrutura_de_dados.json`) e criar o índice de busca semântica. Execute:

```bash
python3 services/vector_store.py

```

*Nota: Isso criará a pasta `faiss_index/` na raiz do backend.*

### 6. Executar a API

Para levantar o servidor local com suporte a *hot-reload* (atualização automática ao salvar os arquivos):

```bash
uvicorn main:app --reload

```

* A API ficará disponível em: `http://localhost:8000`
* A documentação interativa (Swagger) poderá ser acessada em: `http://localhost:8000/docs`

## 🛠️ Ferramentas de Diagnóstico (`utils/`)

Para facilitar o desenvolvimento e debugar o comportamento do RAG, criamos scripts independentes na pasta `utils/`:

* **`check_models.py`:** Verifica a conectividade com a API do Google e lista os modelos de Embedding liberados para a sua chave de API. Útil para validar problemas de `404 NOT_FOUND` de modelos de IA.
```bash
python3 utils/check_models.py

```


* **`test_search.py`:** Testa exclusivamente o motor de busca vetorial (FAISS). Simula uma pergunta de paciente e retorna os chunks (trechos do laudo) recuperados no terminal, garantindo que o RAG está extraindo a informação correta antes de enviar ao LLM.
```bash
python3 utils/test_search.py

```


* **`test_agent.py`:** Dispara uma execução direta do LangGraph (Agente Médico), testando o fluxo completo (Recuperação + Geração) via terminal, sem precisar levantar a API FastAPI.
```bash
python3 utils/test_agent.py

```



## 🔌 Contrato de API Estabelecido

### Endpoint: `POST /api/chat/`

Interface de comunicação utilizada pelo Front-end para enviar as dúvidas dos usuários e receber as respostas fundamentadas via RAG.

**Request Body (Envio):**

```json
{
  "paciente_id": "string (uuid)",
  "mensagem": "string"
}

```

**Response Body (Retorno):**

```json
{
  "resposta": "string",
  "fontes": [
    {
      "painel": "string",
      "marcador": "string",
      "gene": "string",
      "conclusao_curta": "string"
    }
  ]
}

```