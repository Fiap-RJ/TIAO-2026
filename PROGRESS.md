# 🚀 Status do Projeto: Orbital RAG (Global Solution 2026.1)

**Data de Entrega:** 09/06/2026
**Fase Atual:** Desenvolvimento MVP (Trabalho em Paralelo)

---

## 📊 Engenharia de Dados e Audiovisual (Arthur)
- [ ] **APIs:** Mapear as APIs públicas da NASA (sugiro a Asteroids NeoWs ou Space Weather).
- [ ] **Extração:** Criar scripts Python para extrair e limpar esses dados brutos.
- [ ] **Mock de Dados (CRÍTICO):** Gerar o arquivo `context_data.json` de amostra e enviar para o backend.
- [ ] **Diagramas:** Desenhar os fluxogramas da arquitetura para inclusão no PDF.
- [ ] **Audiovisual:** Gravar a demonstração final (até 5 min), falar "QUERO CONCORRER" no início.
- [ ] **Deploy de Vídeo:** Subir no YouTube como "Não Listado" e gerar o link.

## 👨‍💻 Backend, IA e Arquitetura (Michael)
- [x] **Repositório:** Clonar o template oficial da FIAP (`TEMPLATE-TIAO-2026`).
- [x] **Infraestrutura:** Configurar o Docker (`Dockerfile` e `docker-compose.yml`) para a API.
- [x] **Core da API:** Subir a API principal em Node.js (NestJS) com Clean Architecture.
- [ ] **Motor de IA:** Construir a orquestração via LangGraph consumindo os dados da NASA.
- [ ] **Contrato da API:** Expor o endpoint `POST /api/chat` para o Front-end.
- [ ] **Documentação Técnica:** Extrair trechos vitais do código em formato de texto para o PDF.

## 🎨 Frontend e Documentação Narrativa (Nathalia)
- [ ] **Setup:** Iniciar o projeto da interface (React Native ou Web).
- [ ] **Telas:** Desenvolver o Dashboard numérico e a Tela de Chat (com estados de loading).
- [ ] **Integração Front:** Integrar o Front com a rota `/api/chat` (usando mocks iniciais).
- [ ] **PDF:** Montar a estrutura do documento (Introdução, Resultados e Conclusão) com diagramação visual.
- [ ] **Regra de Ouro:** Garantir a inserção da frase "QUERO CONCORRER" na primeira página.

---

## 🗓️ Cronograma de Integração (Code Freeze)
- [ ] **Até 06/06:** Trabalhos paralelos. Entrega dos mocks de dados e construção das telas/API.
- [ ] **07/06 (Virada de Chave):** Apagar mocks, plugar o Front na API e rodar fluxo real ponta a ponta.
- [ ] **08/06 (Code Freeze):** Congelamento de código. Foco 100% na formatação do PDF e edição do vídeo.
