# **Sprint 4 — Produção e Governança (Challenge Dasa/Genera)** 

## **Contexto** 

Nas Sprints 1 a 3, o grupo estruturou os dados do relatório Genera, construiu o agente especialista com RAG e transformou essa inteligência em uma experiência acessível (dashboard, personalização, linguagem simplificada, resumos e salvaguardas). Nesta Sprint 4, a última, o foco passa a ser **operação** : a solução precisa estar pronta para uso real — monitorável, rastreável, explicável e responsável no tratamento dos dados (LGPD). 

Não basta o sistema responder corretamente: é preciso **evidenciar** como ele se comporta em produção — logs, monitoramento, avaliação do modelo, validação das respostas e aplicação em deploy. 

## **Objetivos da Sprint** 

1. **Governança de IA** — LGPD, explicabilidade e logging, documentados numa política de governança. 

2. **Operação e Automação** — monitorar os pipelines e organizar as automações de execução. 

3. **Avaliação do Modelo** — qualidade e consistência das respostas, com ajustes finais. 

4. **Validação das Respostas** — coerência e aderência ao contexto do laudo. 

5. **Deploy da Aplicação** — Front End/Mobile disponível para execução e demonstração. 

6. **Refinamento Final** — consolidar o incremento final dos módulos (Visão Computacional: não utilizada no projeto — declarar como não aplicável). 

## **Entregáveis da Sprint** 

Política de Governança de IA (LGPD, explicabilidade, logging) 

- Evidências de monitoramento dos pipelines e das automações de execução Modelo avaliado e refinado, com evidências de qualidade e consistência Evidências da validação das respostas (NLP) 

Aplicação em deploy, fluxo demonstrável de ponta a ponta 

- Vídeo de até 5 min, narração humana, "não listado" no YouTube 

- README final (evolução das 4 sprints, execução, deploy, incrementos, link do vídeo) 

- Repositório privado, compartilhado **apenas** com `fiap-tutoria` 

## **Estado atual do projeto (ponto de partida)** 

**Nota da Sprint 3: 8.55 / 9.00.** Descontos apontados pelo professor: 

- **Respostas do chatbot longas demais** para o usuário leigo — `detail_level="resumido"` é só uma 

dica no prompt, sem limite real ( `LLM_MAX_TOKENS=2048` ) nem métrica de 

- tamanho/legibilidade. 

- **Resumos determinísticos** — a geração via LLM existe em `services/resumo.py` , mas cai no fallback sem API key, e o front-end **não tem tela de resumos** . 

Riscos encontrados no código: 

- **Dashboard no** main **usa mocks** ( `USE_MOCKS = true` em 

- `src/frontend/src/services/api.js` ) e as 

rotas de riscos/ancestralidade estão sem `{paciente_id}` — o fluxo ponta a ponta não usa o backend 

real. 

- **Repositório está público** , mas a Sprint 4 exige privado + convite só para `fiap-tutoria` . 

- **Logging limitado** — só 4 módulos usam `logging` , sem estrutura, `request_id` ou métricas. 

- **Avaliação com 7 casos** — o `eval/judge.py` (LLM-as-judge) já existe, mas a cobertura é 

- pequena 

- e não gera relatório versionado. 

- **Sem CI** — não há `.github/workflows` . 

- **LGPD** — o risco R9 (sem endpoint de exclusão do histórico) segue em aberto. 

## **Distribuição de Tarefas** 

### 👤 **Michael — IA Generativa & NLP (avaliação e validação)** 

Foco: resolver os dois descontos da Sprint 3 e comprovar qualidade e consistência do modelo. 

|**#**|**Tarefa**|**Detalhamento**|
|---|---|---|
|M1|Respostas|Limite real no modo resumido (~120 palavras), estrutura fixa (resposta direta|
||curtas|→o que fazer→disclaimer curto), opção "quero mais detalhes".|
|M2|Resumos<br>sempre via LLM|Garantir a geração por LLM no ambiente de deploy; fallback determinístico<br>documentado apenas como contingência.|



|**#**|**Tarefa**|**Detalhamento**|
|---|---|---|
|M3|Avaliação do<br>modelo|Expandir o eval de 7 para ~30 casos usando o<br>`judge.py`, com métricas de<br>fidelidade ao laudo, tamanho, legibilidade e tom não alarmista. Relatório<br>**antes × depois**salvo em<br>`document/evidencias/`.|
|M4|Consistência|Rodar cada pergunta N vezes, medir a variação das respostas e ajustar<br>temperatura/prompt, registrando os ajustes feitos.|
|M5|Validação das<br>respostas|Conjunto de perguntas com resposta esperada, revisão humana +<br>automática, tabela de evidência.|



**Depende de** : nada bloqueia o início — trabalha sobre o agente já existente. 

### 👤 **Arthur — Front-end, Deploy & Automações** 

Foco: colocar o produto no ar, consumindo dados reais, com execução automatizada e monitorada. 

|**#**|**Tarefa**|**Detalhamento**|
|---|---|---|
|A1|Integração real<br>front↔back|Remover os mocks (<br>`USE_MOCKS`) e alinhar os contratos de riscos,<br>ancestralidade e histórico com o backend.**Prioridade máxima**—<br>bloqueia o deploy.|
|A2|Tela de resumos|Exibir no dashboard o resumo do relatório e o resumo das interações<br>(<br>`/api/resumos/...`).|
|A3|Deploy público|Backend e front-end acessíveis por URL (ex.: Render/Railway + Vercel, ou<br>VM com Docker Compose); ajustes de responsividade/PWA para o<br>requisito Mobile.|
|A4|Automações<br>(CI/RPA)|GitHub Actions rodando lint + testes + eval a cada push; job agendado de<br>avaliação/reindexação do FAISS. Remover ou tornar real o "upload de PDF<br>(mock)" do chat.|
|A5|Página de<br>monitoramento|Tela no dashboard consumindo<br>`/metrics`: saúde do pipeline, latência,<br>taxa de bloqueio de guardrails, últimas execuções.|



**Depende de** : endpoint `/metrics` da Nathalia (A5). 

### 👤 **Nathalia — Governança, Observabilidade & Entrega** 

Foco: tornar o sistema rastreável e explicável, documentar a governança e consolidar a entrega. 

|**#**|**Tarefa**|**Detalhamento**|
|---|---|---|
|N1|Política de<br>Governança de IA|Evoluir<br>`document/governanca_e_riscos.md`para uma política<br>formal: LGPD (base legal, finalidade, minimização, retenção, direitos do<br>titular), explicabilidade, logging e critérios de acompanhamento.|
|N2|Direito de exclusão<br>(LGPD)|`DELETE /api/historico/{paciente_id}`+ regra de retenção<br>do histórico. Fecha o risco R9.|
||Logging|Logs em JSON com<br>`request_id`, latência por nó do grafo (sanitize→|
|N3|estruturado e<br>rastreável|retrieve→generate→guardrail), violações de guardrail registradas,<br>sem PII nos logs.|
|N4|Explicabilidade +<br>métricas|Resposta do chat passa a informar painel especialista usado, fontes e<br>guardrails acionados; endpoint<br>`/metrics`com latência, volume e taxa<br>de bloqueio.|
|N5|README final,<br>repositório e vídeo|README com evolução das 4 sprints, deploy e evidências; repositório<br>privado + convite<br>`fiap-tutoria`; coordenação e edição final do<br>vídeo.|



**Depende de** : deploy do Arthur (A3) para documentar a URL; relatórios do Michael (M3–M5) para as evidências do README. 

## **Tarefas compartilhadas** 

- **Evidências** : tudo que comprova funcionamento vai para `document/evidencias/` (relatórios de 

- eval, prints do monitoramento, execuções do CI, amostras de log). 

- **Vídeo de demonstração** : cada integrante narra a parte que desenvolveu (deploy e fluxo, avaliação/validação, monitoramento e governança); Nathalia consolida a edição final. 

- **Revisão cruzada** : testar o fluxo completo na URL de deploy antes da entrega 

- (dashboard → chat → resumo → histórico → monitoramento). 

## **Ordem sugerida de execução** 

1. Arthur faz a integração real front ↔ back (A1) — desbloqueia deploy e demo. 

2. Nathalia define logs e métricas (N3/N4); Michael ajusta o tamanho das respostas (M1) em paralelo. 

3. Deploy (A3), CI (A4), avaliação e consistência (M3/M4), política de governança (N1/N2). 

4. Tela de resumos e de monitoramento (A2/A5), validação das respostas (M5). 

5. Evidências, README final, vídeo, repositório privado + convite `fiap-tutoria` . 

## **Checklist de entrega (revisão final)** 

Repositório privado, apenas `fiap-tutoria` como colaborador 

Aplicação em deploy, consumindo dados reais (sem mocks) 

- Respostas curtas e em linguagem leiga 

- Resumos gerados por LLM e visíveis no dashboard 

- Política de Governança de IA (LGPD, explicabilidade, logging) 

- Logs estruturados e monitoramento dos pipelines com evidências 

- Automações de execução (CI) funcionando 

- Relatório de avaliação do modelo (qualidade + consistência, antes × depois) 

- Evidências de validação das respostas 

- README final com evolução das 4 sprints e link do vídeo 

- Vídeo gravado, até 5 min, "não listado" 

