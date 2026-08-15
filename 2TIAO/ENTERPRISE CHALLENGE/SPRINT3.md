# Sprint 3 — Experiência do Usuário (Challenge Dasa/Genera)

## Contexto

Nas Sprints 1 e 2, o grupo estruturou os dados do relatório Genera e construiu o agente
especialista em RAG capaz de interpretar o conteúdo genético. Nesta Sprint 3, o foco
sai da **inteligência** e vai para a **experiência**: transformar essa capacidade
técnica em um produto que o cliente final compreenda e use com segurança.

O desafio central é a **tradução** entre o conhecimento técnico-científico do relatório
e a compreensão cotidiana de quem não tem formação em saúde — com clareza, contexto e
comunicação responsável (nunca alarmista, nunca diagnóstica).

## Objetivos da Sprint

1. **Dashboard de visualização** — cards de risco e resumo de ancestralidade, com
   interface refinada e navegação clara.
2. **Personalização das respostas** — o agente adapta a resposta ao perfil/dúvida do
   usuário, mantendo fundamentação no relatório (RAG).
3. **Simplificação da linguagem (NLP)** — traduzir termos técnicos em explicações
   acessíveis ao público leigo.
4. **Resumos automáticos** — do relatório e do histórico de interações.
5. **Comunicação responsável** — evitar linguagem alarmista, incluir disclaimers,
   nunca emitir diagnóstico definitivo.
6. **Entrada multimodal (opcional)** — leitura de imagens/gráficos do relatório.

## Entregáveis da Sprint

- [ ] Dashboard refinado (cards de risco + resumo de ancestralidade + navegação)
- [ ] Agente respondendo de forma personalizada e em linguagem simplificada
- [ ] Módulo de resumos automáticos (relatório + interações)
- [ ] Salvaguardas de comunicação implementadas e documentadas
- [ ] (Opcional) Pipeline de entrada multimodal
- [ ] Vídeo de demonstração (até 5 min, narração humana, "não listado" no YouTube)
- [ ] README atualizado com a evolução da experiência do usuário + link do vídeo
- [ ] Repositório privado com tutores como colaboradores

## Estado atual do projeto (ponto de partida)

- **Backend**: FastAPI + LangGraph já funcional. Grafo com nós `retrieve` → `generate`
  → `guardrail` / `sanitize`. Guardrails e redação de PII já existem em
  `services/guardrails.py` e `services/pii_redaction.py`. Vector store FAISS já
  populado (`faiss_index/`).
- **Frontend**: esqueleto React + Vite + Tailwind, praticamente só com `App.jsx`
  inicial. É onde está a maior lacuna a preencher nesta sprint.
- **Governança**: já há uma base em `document/governanca_e_riscos.md`.

---

## Distribuição de Tarefas

### 👤 Arthur — Frontend & Dashboard

Foco: transformar o esqueleto do frontend em um dashboard visual, acessível e
navegável, consumindo os dados expostos pelo backend.

| # | Tarefa | Detalhamento |
|---|--------|--------------|
| A1 | Layout base do dashboard | Definir estrutura de navegação (ex.: Home / Riscos / Ancestralidade / Chat / Histórico) usando React Router. Hierarquia visual clara, sem poluição de informação. |
| A2 | Cards de risco | Componente reutilizável de card por categoria (Nutri, Fit, Skin, Farma, Aging etc.), exibindo nível de predisposição com linguagem e cores **não alarmistas** (evitar vermelho puro / termos como "perigo", preferir escalas neutras: baixo/moderado/atenção). |
| A3 | Resumo de ancestralidade | Componente visual (gráfico de pizza/barra ou mapa simplificado) mostrando a composição de ancestralidade a partir dos dados estruturados do relatório. |
| A4 | Tela de histórico de interações | Lista das conversas/perguntas anteriores do usuário com o agente, com persistência (consome endpoint do Michael). |
| A5 | Integração do chat existente | Conectar a interface de chat ao dashboard (mesma experiência, navegação unificada), ajustando UX para exibir disclaimers e resumos gerados pela Nathalia. |
| A6 | Estados de carregamento e erro | Feedback visual (loading, empty state, erro de API) para todas as telas, garantindo usabilidade mesmo em falhas de rede/API. |
| A7 | Responsividade e acessibilidade básica | Testar em mobile/desktop, contraste de cores adequado, navegação por teclado e leitura por screen reader nos componentes principais. |

**Depende de**: endpoints do Michael (A4, A5) e formato de resumo definido pela Nathalia (A5).

---

### 👤 Nathalia — IA Generativa & NLP

Foco: fazer o agente falar a língua do usuário — personalização, simplificação e
resumos, sempre fundamentado no relatório.

| # | Tarefa | Detalhamento |
|---|--------|--------------|
| N1 | Perfil de personalização | Definir dimensões de personalização (ex.: nível de detalhe desejado, tom, foco em determinada categoria de risco) e como isso entra no state do LangGraph (`agents/state.py`). |
| N2 | Ajuste do nó `generate` | Modificar `agents/nodes/generate.py` e `prompts/specialists.py` para injetar o perfil/contexto do usuário no prompt, mantendo a resposta ancorada nos documentos recuperados via RAG. |
| N3 | Simplificação de linguagem técnica | Criar uma etapa (novo nó ou pós-processamento) que traduz termos técnicos do relatório (ex.: nomenclatura de genes, variantes, unidades) em linguagem acessível, com glossário de apoio se necessário. |
| N4 | Módulo de resumo do relatório | Novo serviço/nó que gera um resumo executivo do relatório completo do usuário (principais riscos + ancestralidade), sem extrapolar dados não verificáveis. |
| N5 | Módulo de resumo de interações | Gerar resumo periódico do histórico de conversas do usuário (ex.: "principais dúvidas discutidas até agora"), reaproveitando a mesma lógica de resumo do N4. |
| N6 | Testes de qualidade das respostas | Estender `eval/cases.py` e `eval/criteria.py` com casos de teste para tom, clareza e fidelidade ao relatório após as mudanças de personalização/simplificação. |

**Depende de**: contrato de dados do relatório (já existe em
`proposta_estrutura_de_dados.json`); alinhar formato do resumo com Arthur (para exibição) e Michael (para persistência/endpoint).

---

### 👤 Michael — Backend, Integração & Governança

Foco: expor os dados necessários para o dashboard, persistir histórico, reforçar
guardrails e cuidar da organização/documentação da entrega.

| # | Tarefa | Detalhamento |
|---|--------|--------------|
| M1 | Endpoint de riscos | Novo endpoint (`api/routes/`) que retorna os dados estruturados de risco por categoria para o dashboard, com schema em `domain/schemas.py`. |
| M2 | Endpoint de ancestralidade | Endpoint que retorna os dados de composição de ancestralidade do relatório. |
| M3 | Endpoint de resumos | Endpoint que expõe os resumos gerados pela Nathalia (relatório e interações), incluindo cache/estratégia de atualização quando novos dados chegam. |
| M4 | Persistência de histórico | Adicionar camada de persistência (ex.: SQLite/Postgres leve ou arquivo estruturado, a decidir conforme escopo) para salvar histórico de interações por usuário, com endpoint de leitura para o frontend. |
| M5 | Reforço de guardrails | Revisar `services/guardrails.py` e `agents/nodes/guardrail.py` para cobrir explicitamente linguagem alarmista e reforçar disclaimers obrigatórios em toda resposta final. |
| M6 | Testes de integração da API | Testes cobrindo os novos endpoints (riscos, ancestralidade, resumos, histórico) e o fluxo ponta a ponta com o agente. |
| M7 | Documentação e organização do repositório | Atualizar `README.md` (raiz do projeto e do backend/frontend) descrevendo a evolução da UX, decisões de interface e salvaguardas. Garantir repo privado com tutores como colaboradores (Caique `CaiqueFiap-2026`, Leonardo `Leoruiz197`). |
| M8 | Coordenação do vídeo de entrega | Organizar roteiro e gravação do vídeo (até 5 min, narração humana, publicado como "não listado"), integrando as partes de dashboard, personalização e linguagem simplificada demonstradas por Arthur e Nathalia. |

**Depende de**: schemas alinhados com Arthur (M1-M3) e formato de resumo da Nathalia (M3).

---

## Tarefas compartilhadas

- **Vídeo de demonstração**: cada integrante narra a parte que desenvolveu (dashboard,
  personalização/linguagem, backend/governança). Michael consolida a edição final.
- **Revisão cruzada**: revisar o trabalho um do outro antes da entrega, especialmente
  o fluxo ponta a ponta (dashboard → chat → resumo → histórico).
- **(Opcional) Multimodalidade**: se houver tempo, Nathalia (pipeline de leitura de
  imagem) + Michael (endpoint de upload/integração) tocam essa frente, já que é
  extensão do backend/IA.

## Ordem sugerida de execução

1. Michael define e sobe os contratos de API (schemas) para riscos, ancestralidade e
   resumos — desbloqueia Arthur e Nathalia.
2. Nathalia trabalha em paralelo na personalização/simplificação/resumos usando o
   agente já existente, sem esperar a API final (pode mockar).
3. Arthur constrói o dashboard consumindo mocks e depois troca pelos endpoints reais
   do Michael.
4. Integração final: Michael conecta resumos da Nathalia aos endpoints; Arthur troca
   mocks pelos dados reais.
5. Testes ponta a ponta, gravação do vídeo, atualização do README.

## Checklist de entrega (revisão final)

- [ ] Repositório privado, tutores adicionados como collaborators
- [ ] Dashboard funcional com cards de risco e ancestralidade
- [ ] Histórico de interações persistido e visível
- [ ] Respostas do agente personalizadas e em linguagem simplificada
- [ ] Resumos automáticos (relatório + interações) funcionando
- [ ] Disclaimers presentes em toda resposta; nenhuma linguagem alarmista
- [ ] README atualizado com decisões de UX/comunicação e link do vídeo
- [ ] Vídeo gravado, até 5 min, publicado como "não listado"
