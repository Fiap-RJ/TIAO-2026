# Documentação Técnica: Orbital RAG

## 1. Arquitetura do Sistema
O backend foi desenvolvido utilizando **NestJS** com **Clean Architecture**, garantindo a separação de responsabilidades entre as camadas de Domínio, Aplicação e Infraestrutura.

### Estrutura de Pastas
- `domain/`: Contém as entidades puras e regras de negócio (ex: `SpaceEvent`).
- `application/`: Contém os casos de uso (ex: `ProcessChatMessageUseCase`).
- `infrastructure/`: Implementação de repositórios e serviços externos (LangGraph, FileSystem).
- `presentation/`: Controllers do NestJS que expõem a API REST.

## 2. Endpoint de Chat
O ponto de entrada principal é o endpoint `POST /api/chat`.

**Request:**
```json
{
  "message": "Quais asteroides oferecem risco hoje?"
}
```

**Implementação (Controller):**
O controller delega a execução para o `ProcessChatMessageUseCase`, que orquestra a busca de dados e a resposta da IA.

## 3. Motor de IA (LangGraph)
A orquestração é feita via **LangGraph**, permitindo um fluxo de agentes resiliente:
1. **Input:** Recebe a mensagem do usuário.
2. **Retrieval:** O `FileSpaceEventRepository` lê o `context_data.json` para fornecer contexto.
3. **Processing:** O `LangGraphAgentService` processa a consulta, cruza com os dados espaciais e gera uma resposta em linguagem natural.
4. **Output:** Retorna o JSON estruturado com a resposta e as fontes utilizadas.

## 4. Infraestrutura
O projeto é conteinerizado via **Docker**, garantindo que o ambiente de desenvolvimento seja idêntico ao de produção. O `docker-compose.yml` expõe a API na porta 3000, facilitando a integração imediata com o Frontend.
