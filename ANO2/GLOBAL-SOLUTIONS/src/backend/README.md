# Backend do Orbital RAG

Este é o serviço de backend para o projeto Orbital RAG, construído com NestJS e Clean Architecture. Ele fornece um assistente inteligente para monitoramento de anomalias espaciais utilizando LangGraph e Google Gemini.

## Guia de Início

### Pré-requisitos
- Node.js (v18+)
- Docker e Docker Compose
- Chave de API do Google Gemini (Google Gemini API Key)

### Configuração
Antes de rodar a aplicação, crie um arquivo `.env` na raiz do diretório do backend e adicione sua chave de API:

```env
GOOGLE_API_KEY="sua_chave_da_api_aqui"

```

### Contrato de Dados (`context_data.json`)

A aplicação espera um arquivo `context_data.json` no diretório raiz, populado pelo script de engenharia de dados. Ele deve seguir exatamente este formato (utilizando *snake_case*):

```json
[
  {
    "id_evento": "string",
    "tipo": "string",
    "nome": "string",
    "data_aproximacao": "string (ISO 8601)",
    "distancia_terra_km": "number",
    "risco_colisao": "boolean",
    "resumo_alerta": "string"
  }
]

```

### Instalação

Navegue até o diretório do backend e instale as dependências:

```bash
cd ANO2/GLOBAL-SOLUTIONS/src/backend
npm install

```

### Executando a Aplicação

Para subir a aplicação utilizando o Docker (que já está mapeando os volumes para ler seus arquivos locais em tempo real), execute:

```bash
docker compose up --build

```

A API ficará disponível em `http://localhost:3000`.

**Uso do Endpoint:**
Envie uma requisição `POST` para a rota `/api/chat` com o seguinte payload:

```json
{
  "message": "Tem algum asteroide com risco de colisão vindo?"
}

```

## Documentação

Para informações arquiteturais detalhadas, padrões de projeto, fluxo da máquina de estados do LangGraph e especificações da API, consulte o arquivo [DOCUMENTACAO_TECNICA.md](https://www.google.com/search?q=./DOCUMENTACAO_TECNICA.md).

```
