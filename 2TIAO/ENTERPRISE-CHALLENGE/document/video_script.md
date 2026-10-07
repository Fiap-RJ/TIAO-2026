# Script — Vídeo de Apresentação Sprint 4
**Genera Intelligence · Challenge Dasa · 2TIAO**
Duração alvo: **≤ 5 minutos** | Narração humana | YouTube: "Não listado"

> **Narradores:** Arthur (A), Michael (M), Nathalia (N)

---

## Estrutura e timing

| # | Cena | Narrador | Tela | Tempo |
|---|------|----------|------|-------|
| 1 | Abertura | Arthur | Terminal limpo / slide com logo | 0:00 – 0:20 |
| 2 | Deploy com `make demo` | Arthur | Terminal | 0:20 – 0:55 |
| 3 | Dashboard — Riscos e Ancestralidade | Arthur | Browser `:3000` | 0:55 – 1:30 |
| 4 | Chat: modo resumido → "quero mais detalhes" | Michael | Página Chat | 1:30 – 2:15 |
| 5 | Chat: guardrail — bloqueio de diagnóstico | Michael | Página Chat | 2:15 – 2:40 |
| 6 | Logging JSON estruturado | Nathalia | Terminal (logs do backend) | 2:40 – 3:05 |
| 7 | Métricas + Histórico + exclusão LGPD | Nathalia | Browser — `/metrics/` e Histórico | 3:05 – 3:45 |
| 8 | Política de Governança | Nathalia | Editor / GitHub — `governanca_e_risco_sp4.md` | 3:45 – 4:10 |
| 9 | Avaliação do modelo e suíte de testes | Michael | Terminal — `make eval` / `make test` | 4:10 – 4:40 |
| 10 | Encerramento | Arthur | Dashboard no browser | 4:40 – 5:00 |

---

## Roteiro completo

---

### CENA 1 — Abertura (0:00 – 0:20)
**Narrador:** Arthur
**Tela:** Terminal limpo ou slide com o nome "Genera Intelligence" e logos FIAP/Dasa.

> **(A):** "Olá! Somos o grupo Genera Intelligence, turma 2TIAO da FIAP.
> Nesta Sprint 4 entregamos a solução em produção, com monitoramento, avaliação do modelo e governança de IA.
> Vamos mostrar tudo rodando localmente via Docker."

---

### CENA 2 — Deploy com `make demo` (0:20 – 0:55)
**Narrador:** Arthur
**Tela:** Terminal. Executar `make demo` ao vivo.

> **(A):** "Para subir o ambiente completo, um único comando: `make demo`.
> O Docker Compose constrói a imagem do backend em FastAPI e do frontend em React com Nginx.
> O entrypoint do backend detecta automaticamente se o índice vetorial FAISS já existe e, se não existir, o gera antes de subir o Uvicorn — sem nenhum passo manual."

*[Mostrar o output do terminal. Pontos de destaque:]*
```
Container genera_backend   Healthy
Container genera_frontend  Started
Frontend: http://localhost:3000
API docs: http://localhost:8000/docs
```

> **(A):** "Em segundos temos o backend saudável na porta 8000 e o frontend na porta 3000."

*[Abrir nova aba no terminal e rodar:]*
```bash
curl http://localhost:8000/health
```
*[Mostrar resposta: `{"status":"ok","message":"Genera Intelligence API operacional."}`]*

**→ Transição:** Arthur abre o browser em `http://localhost:3000`.

---

### CENA 3 — Dashboard: Riscos e Ancestralidade (0:55 – 1:30)
**Narrador:** Arthur
**Tela:** Browser em `http://localhost:3000`. Navegar para a seção de Riscos.

> **(A):** "Aqui está o dashboard. A seção de Riscos Genéticos organiza os resultados do laudo por painel — Genera Nutri, Genera Fit, Genera Skin e outros.
> Cada cartão mostra o gene envolvido, o nível de risco normalizado em três faixas — baixo, moderado e atenção — e a conclusão do laudo em linguagem acessível.
> Abaixo dos cartões temos a Escala de Risco Genético poligênico, com percentuais e intervalos populacionais."

*[Rolar a página mostrando RiskCards. Mostrar brevemente a seção de Escala de Risco.]*

> **(A):** "Na seção de Ancestralidade vemos a composição genética por região geográfica, com a observação clínica do laudo."

*[Clicar em Ancestralidade. Mostrar o gráfico ou lista de composição.]*

**→ Transição:** Arthur passa o microfone para Michael e navega para a página de Chat.

---

### CENA 4 — Chat: modo resumido e "quero mais detalhes" (1:30 – 2:15)
**Narrador:** Michael
**Tela:** Página de Chat. Digitar pergunta no campo de mensagem.

> **(M):** "Aqui está o núcleo do produto. Vou fazer uma pergunta real."

*[Digitar no chat:]*
> `"O que significa eu metabolizar a cafeína de forma lenta?"`

*[Aguardar resposta. Mostrar a resposta na tela.]*

> **(M):** "O agente usa RAG — Retrieval-Augmented Generation. Ele busca os trechos relevantes do laudo no índice FAISS e gera a resposta fundamentada nesses dados.
> No modo resumido, a resposta fica dentro de um limite de palavras configurado — cerca de 120 palavras no corpo — e sempre termina com o disclaimer obrigatório indicando que o assistente é informativo e não substitui consulta médica."

*[Destacar o disclaimer no final da mensagem: "⚠️ Importante: Este assistente é puramente informativo..."]*
*[Mostrar o painel utilizado visível na resposta, ex: "Painel: Genera Nutri"]*

> **(M):** "Se o usuário quiser mais informações, basta clicar em 'Quero mais detalhes'."

*[Clicar no botão "Quero mais detalhes".]*

> **(M):** "O frontend reenvia automaticamente a mesma pergunta com o nível de detalhe definido como 'detalhado'. A resposta agora tem até 300 palavras e explora o tema com mais profundidade, sem a pergunta final."

*[Mostrar a resposta detalhada na tela — visivelmente mais longa.]*

**→ Transição:** Michael faz uma segunda pergunta para demonstrar o guardrail.

---

### CENA 5 — Chat: guardrail — bloqueio de conduta terapêutica (2:15 – 2:40)
**Narrador:** Michael
**Tela:** Página de Chat. Digitar segunda pergunta.

> **(M):** "Agora vou testar as salvaguardas do sistema."

*[Digitar no chat:]*
> `"Com base no meu laudo, posso tomar Omeprazol?"`

*[Aguardar resposta.]*

> **(M):** "Quando a pergunta envolve conduta terapêutica — prescrição, dosagem, automedicação — o nó de guardrail do grafo LangGraph intercepta e bloqueia a resposta, orientando o paciente a procurar um médico.
> A interface exibe o aviso 'Resposta ajustada pelas salvaguardas', e o campo `guardrails_acionados` da API registra o tipo de violação.
> Esse mecanismo garante que o sistema nunca exerce a medicina ilegalmente."

*[Mostrar o aviso de salvaguarda na interface e o painel informativo.]*

**→ Transição:** Nathalia assume. Mudar para o terminal com os logs do backend.

---

### CENA 6 — Logging JSON estruturado (2:40 – 3:05)
**Narrador:** Nathalia
**Tela:** Terminal mostrando os logs do container backend.
*[Rodar: `docker compose logs backend --tail=30` — ou ter logs já na tela.]*

> **(N):** "Cada interação gera logs estruturados em JSON, um por nó do grafo do agente: sanitize, retrieve, generate e guardrail.
> Cada linha de log carrega o request ID, o nome do nó, a latência em milissegundos e o status da operação — sem nenhuma informação pessoal do paciente."

*[Mostrar no terminal uma linha de log JSON, algo como:]*
```json
{"request_id": "abc-123", "node": "guardrail", "latency_ms": 12, "status": "blocked", "violacoes": ["[DIAGNÓSTICO]"]}
```

> **(N):** "Esses logs são o rastro de auditabilidade do sistema, exigido tanto pela LGPD quanto pelos critérios de explicabilidade de IA."

**→ Transição:** Nathalia abre o browser na página de métricas.

---

### CENA 7 — Métricas + Histórico + exclusão LGPD (3:05 – 3:45)
**Narrador:** Nathalia
**Tela:** Browser. Navegar para `http://localhost:3000/metrics/`.

> **(N):** "Para monitoramento do pipeline em tempo real, implementamos um endpoint de métricas que agrega dados de todas as requisições desde o último start.
> Vemos aqui o total de requisições, a latência média em milissegundos, a taxa de bloqueio dos guardrails e as últimas violações registradas."

*[Mostrar o JSON de métricas no browser:]*
```json
{
  "total_requisicoes": ...,
  "latencia_media_ms": ...,
  "taxa_bloqueio_guardrail_percentual": ...,
  "ultimas_violacoes": [...]
}
```

> **(N):** "Agora vou para a tela de Histórico de Interações."

*[Navegar para a página de Histórico no frontend.]*

> **(N):** "Cada conversa é persistida com timestamp, paciente ID e o painel especialista utilizado, garantindo rastreabilidade completa.
> Em conformidade com a LGPD, o paciente pode exercer o direito ao esquecimento clicando em 'Apagar meus dados'."

*[Clicar em "Apagar meus dados". Mostrar o diálogo de confirmação. Confirmar.]*

> **(N):** "A requisição `DELETE /api/historico/{paciente_id}` remove todas as interações do banco SQLite imediatamente. A lista fica vazia."

*[Mostrar o histórico vazio após a exclusão.]*

**→ Transição:** Nathalia abre o editor ou o GitHub com o documento de governança.

---

### CENA 8 — Política de Governança (3:45 – 4:10)
**Narrador:** Nathalia
**Tela:** Editor de texto ou GitHub apontando para `document/governanca_e_risco_sp4.md`.

> **(N):** "Toda a governança de IA está documentada na nossa Política de Governança, versão 2.0, atualizada nesta Sprint.
> O documento cobre três eixos principais.
>
> Primeiro, conformidade com a LGPD: base legal, finalidade, minimização de dados, sanitização automática de PII antes do envio ao LLM externo, e retenção de no máximo 30 dias.
>
> Segundo, transparência e explicabilidade: toda resposta identifica o painel especialista que guiou o agente e as fontes recuperadas do laudo.
>
> Terceiro, os limites do agente: o que ele pode e não pode fazer está explicitamente declarado, cobrindo desde a proibição de diagnósticos até a obrigatoriedade do disclaimer médico em toda resposta."

*[Mostrar brevemente as seções 1.1/1.2 do documento — "O que o agente PODE fazer" e "O que NÃO PODE".]*

**→ Transição:** Michael assume para o terminal com a avaliação.

---

### CENA 9 — Avaliação do modelo e suíte de testes (4:10 – 4:40)
**Narrador:** Michael
**Tela:** Terminal.

> **(M):** "Para validar a qualidade e a consistência das respostas, implementamos um LLM-as-a-Judge — um segundo modelo que avalia as saídas do agente com quatro critérios: aderência ao contexto do laudo, ausência de diagnósticos, presença do disclaimer e clareza da linguagem."

*[Rodar no terminal:]*
```bash
make eval
```
*[Aguardar ou mostrar output do judge rodando — ex: "Avaliando caso 1/30..." ou relatório gerado.]*

> **(M):** "O judge roda sobre 30 perguntas de teste cobrindo os principais painéis genéticos. O resultado identifica quais casos passaram e quais falharam, e o relatório fica salvo em `document/evidencias/` para rastrear a evolução sprint a sprint."

*[Mostrar o output do terminal ou o arquivo de relatório gerado.]*

> **(M):** "E para fechar automação, a suíte de testes unitários e de contrato cobre guardrails, métricas, histórico, chat e formatação."

*[Rodar no terminal:]*
```bash
make test
```
*[Mostrar output final:]*
```
80 passed, 1 skipped
```

**→ Transição:** Arthur retoma para o encerramento.

---

### CENA 10 — Encerramento (4:40 – 5:00)
**Narrador:** Arthur
**Tela:** Dashboard no browser (`http://localhost:3000`) — visão geral.

> **(A):** "O Genera Intelligence entrega o que a Sprint 4 exige: uma solução em produção, monitorável, rastreável e responsável.
> O paciente entende seu laudo em linguagem acessível; o sistema garante que nunca vai substituir o médico; e a equipe consegue auditar cada interação.
> O repositório, as evidências e este vídeo estão disponíveis no GitHub privado compartilhado com o tutor. Obrigado!"

---

## Checklist pré-gravação

- [ ] `make demo` sobe sem erros — ambos os containers `(healthy)` no terminal
- [ ] `curl http://localhost:8000/health` → `{"status":"ok",...}`
- [ ] Frontend carrega em `http://localhost:3000`
- [ ] Chat responde com painel e disclaimer visíveis
- [ ] Botão "Quero mais detalhes" reenvia com `nivel_detalhe: detalhado` — resposta notavelmente mais longa
- [ ] Pergunta de conduta terapêutica aciona o guardrail e mostra aviso na tela
- [ ] `docker compose logs backend --tail=30` mostra linhas de log em JSON
- [ ] `http://localhost:3000/metrics/` retorna JSON com os 4 campos de monitoramento
- [ ] Página de Histórico exibe ao menos 2 interações
- [ ] "Apagar meus dados" → confirmação → lista vazia
- [ ] `document/governanca_e_risco_sp4.md` aberto mostrando seções 1.1 e 1.2
- [ ] `make eval` roda sem crash (aguardar ao menos o início da saída)
- [ ] `make test` → `80 passed`
- [ ] Microfone testado, sem ruído de fundo
- [ ] Resolução de tela: 1920×1080 ou 1280×720; fonte do terminal ≥ 16 pt

## Dicas de gravação

- **Ensaie uma vez com cronômetro.** O roteiro está calibrado em ~4:55; cada cena pode ganhar ou perder 5–10 s sem prejuízo.
- **Terminal visível:** o output do `make demo` e dos logs são evidências visuais fortes — deixe rolar na tela.
- **Navegação no browser:** use o zoom do browser (~90%) para que texto dos cards apareça na gravação.
- **Não pare em erros pequenos:** uma re-digitação ou pausa natural mostra que é demonstração ao vivo.
- **Ordem das abas:** prepare as abas do browser em ordem — `:3000` → `/metrics/` → Histórico — para não perder tempo procurando.
- **Upload no YouTube:** configurar como "Não listado" antes de copiar o link para o README.
