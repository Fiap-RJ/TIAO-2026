# Documentação Técnica: Orbital RAG

## 1. Visão Geral e Arquitetura do Sistema

O backend do Orbital RAG foi projetado sob os princípios da **Clean Architecture**, garantindo uma separação estrita de responsabilidades, alta testabilidade e isolamento entre as regras de negócio da aplicação e seus detalhes de infraestrutura (frameworks, APIs externas e sistema de arquivos). 

Desenvolvido em **TypeScript** sobre o ecossistema **NestJS**, o sistema implementa a inversão de dependência através de portas e adaptadores, permitindo que a camada de domínio permaneça agnóstica.

### Estrutura de Diretórios
- `domain/`: Contém as entidades puras (ex: `SpaceEvent`), blindadas de dependências externas.
- `application/`: Contém os casos de uso (ex: `ProcessChatMessageUseCase`), DTOs e as definições de portas (interfaces que ditam o contrato de comunicação).
- `infrastructure/`: Implementação técnica dos adaptadores, incluindo repositórios (`FileSpaceEventRepository`) e integrações externas (LangGraph, Google Gemini).
- `presentation/`: Controllers do NestJS que expõem a API REST para consumo do Frontend.

## 2. API e Endpoints

O ponto de entrada da aplicação é o endpoint unificado de conversação.

### `POST /api/chat`
Recebe a pergunta em linguagem natural, aciona o motor de IA e retorna a inferência acompanhada das fontes rastreadas.

**Request Payload:**
```json
{
  "message": "Quais asteroides oferecem risco de colisão esta semana?"
}

```

**Response Payload (Sucesso):**
O retorno garante transparência ao cliente, separando a resposta gerada (`reply`) das informações factuais extraídas (`source_data`).

```json
{
  "reply": "De acordo com os dados atuais, o asteroide 2026 Xray-1 apresenta risco de colisão avaliado em 4%. O asteroide 2026 Yankee-2 passa a uma distância segura.",
  "source_data": [
    "2026 Xray-1 - Risco: true",
    "2026 Yankee-2 - Risco: false"
  ]
}

```

## 3. Motor RAG com LangGraph (Inteligência Artificial)

A orquestração da Inteligência Artificial transcende uma chamada linear simples. Foi implementado um sistema RAG (Retrieval-Augmented Generation) baseado em um **Grafo de Estado (StateGraph)** utilizando a biblioteca `@langchain/langgraph` e esquematizado de forma estrita via `Annotation.Root`. O motor cognitivo subjacente é o modelo `gemini-3.1-flash-lite-preview`.

O fluxo arquitetural do agente é composto por três nós fundamentais:

1. **`retrieveData`:**
Acessa a camada de repositório para carregar o contexto atualizado (`context_data.json`). Realiza a sanitização e o mapeamento dos dados (convertendo as chaves em `snake_case` provenientes da engenharia de dados para o modelo `camelCase` exigido pelas entidades de domínio).
2. **`generateResponse`:**
Constrói um prompt determinístico unindo a intencionalidade do usuário com os dados espaciais brutos extraídos, invocando o modelo LLM para síntese textual.
3. **`validator` (Guardrail Anti-Alucinação):**
Nó de segurança que aplica regras heurísticas sobre a saída do modelo. Valida se a resposta possui conteúdo semântico válido e se faz referência direta às chaves primárias dos dados injetados.

### Resiliência de Fluxo (Conditional Edges)

Para garantir a confiabilidade da resposta, foi estabelecida uma aresta condicional (`addConditionalEdges`) atrelada à saída do `validator`. Se for detectado que a IA sofreu uma "alucinação" (inventou informações que não constam no banco de dados), a validação falha e o grafo entra em recursão, roteando o estado de volta para o processamento ou assumindo uma degradação graciosa.

## 4. Observabilidade e Tratamento de Erros

A aplicação foi desenvolvida com foco em monitoramento contínuo:

* **Latência e Tracking de Nós:** Foi implementado um sistema de métricas no serviço do agente. Cada transição de estado no LangGraph possui marcações de tempo (`Date.now() - start`), registrando via `Logger` do NestJS a latência exata (em milissegundos) das chamadas de rede e processamentos locais.
* **Fail-Safe de Dados:** O `FileSpaceEventRepository` opera com blocos `try/catch` de contenção. Caso o script de extração falhe ou gere um JSON malformado, o sistema intercepta o erro em tempo de execução, impede o crash do serviço e retorna um contexto vazio, sinalizando adequadamente ao usuário a falta de dados atualizados.

## 5. Infraestrutura e Deploy

O serviço é totalmente conteinerizado via **Docker**, utilizando uma imagem otimizada baseada no `node:20-alpine`. O `docker-compose.yml` mapeia a porta 3000 e utiliza volumes dinâmicos para ler o `context_data.json` em tempo real, permitindo que a IA possua dados quentes sem necessidade de rebuild do container.

```
