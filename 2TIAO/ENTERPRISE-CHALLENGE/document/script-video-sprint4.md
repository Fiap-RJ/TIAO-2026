# Script — Vídeo de Apresentação Sprint 4

**Genera Intelligence · Challenge Dasa · 2TIAO**  
Duração alvo: **≤ 5 minutos** | Formato: narração humana, sem cortes longos

---

## Estrutura e timing

| # | Cena | Tela | Tempo |
|---|------|------|-------|
| 1 | Abertura | Slide ou terminal | 0:00 – 0:20 |
| 2 | Deploy local (make demo) | Terminal com output | 0:20 – 1:00 |
| 3 | render.yaml overview | Editor + explicação | 1:00 – 1:30 |
| 4 | GitHub Actions CI | GitHub UI — workflow runs | 1:30 – 2:00 |
| 5 | Dashboard de Riscos | Browser :3000 | 2:00 – 2:30 |
| 6 | Chat conversacional | Página Chat | 2:30 – 3:30 |
| 7 | Monitoramento (/metrics) | `/metrics/` endpoint + dashboard | 3:30 – 4:00 |
| 8 | Governança e LGPD | Arquivo de governança | 4:00 – 4:30 |
| 9 | Encerramento | Slide ou terminal | 4:30 – 5:00 |

---

## Roteiro completo

---

### CENA 1 — Abertura (0:00 – 0:20)
**Tela:** Slide com logo do projeto ou terminal limpo.

> "Olá! Somos o grupo [NOME DO GRUPO] da turma 2TIAO da FIAP.
> Este é o Genera Intelligence — um assistente de IA que permite ao paciente conversar com seu próprio laudo genético.
> Neste vídeo mostramos a entrega final da Sprint 4: a solução rodando em produção, com monitoramento, governança de IA e a avaliação do modelo."

---

### CENA 2 — Deploy local (0:20 – 1:00)
**Tela:** Terminal. Rodar `make demo` ao vivo.

> "Para subir o ambiente completo localmente, basta um único comando: `make demo`.
> O Docker Compose orquestra três containers: backend em FastAPI na porta 8000, frontend em React na porta 3000, e opcionalmente o PaddleOCR na porta 8001.
> O entrypoint do backend gera automaticamente o índice vetorial FAISS na primeira execução — sem passos manuais.
> Veja o terminal: em poucos segundos todos os serviços estão saudáveis."

*[Mostrar o output do terminal com status `(healthy)` para backend, frontend e paddle-ocr.]*

> "Agora temos um ambiente de produção completo rodando localmente — pronto para gravar o vídeo, pronto para deploy na nuvem."

---

### CENA 3 — Infrastructure-as-Code: render.yaml (1:00 – 1:30)
**Tela:** Abrir `render.yaml` em um editor.

> "Quando levamos isso para a nuvem via Render, a estrutura é definida em Infrastructure-as-Code através do `render.yaml`.
> Aqui definimos os três serviços: backend, frontend e paddle-ocr — com seus ports, healthchecks, volumes persistentes e variáveis de ambiente.
> Render lê este arquivo automaticamente quando você conecta seu GitHub, provisiona os recursos e inicia o deploy — sem cliques na UI."

*[Navegar pelo arquivo mostrando os três serviços `genera-backend`, `genera-frontend`, `genera-paddle-ocr`.]*

> "Cada serviço tem um `healthCheck` configurado — Render monitora a saúde e reinicia se necessário. Os discos persistentes garantem que o índice FAISS não é perdido em um redeploy."

---

### CENA 4 — CI/CD: GitHub Actions (1:30 – 2:00)
**Tela:** GitHub → Actions tab mostrando workflows.

> "Antes de qualquer deploy, o código passa por validação contínua via GitHub Actions.
> Temos dois workflows: um de **push** que roda lint com Ruff e os testes automaticamente a cada commit, e outro de **avaliação manual** que executa o LLM-as-a-Judge com casos de teste reais e salva o relatório."

*[Mostrar o histórico de runs, com ✓ (verde) para runs bem-sucedidos.]*

> "Isso garante que qualquer código que chegue à branch main passou por rigor técnico — linting, testes unitários e validação de qualidade do modelo."

---

### CENA 5 — Dashboard de Riscos (2:00 – 2:30)
**Tela:** Browser em `http://localhost:3000`. Navegar para a seção de Riscos.

> "Aqui está o dashboard do paciente. A primeira seção mostra seus riscos genéticos por painel — Genera Nutri, Fit, Skin e outros.
> Cada marcador traz o gene, a classificação em três níveis — baixo, moderado, atenção — e a interpretação do laudo em linguagem clara.
> Sem dados inventados: tudo vem do JSON estruturado do laudo Genera, servido pelo backend em tempo real."

*[Rolar mostrando alguns cards de risco.]*

---

### CENA 6 — Chat conversacional (2:30 – 3:30)
**Tela:** Página de Chat do frontend.

> "O coração do produto é o chat. Vou fazer uma pergunta."

*[Digitar: `"O que significa eu metabolizar a cafeína de forma lenta?"`]*

> "O agente usa RAG — Retrieval-Augmented Generation — para buscar trechos relevantes do laudo no FAISS e gerar uma resposta fundamentada, em linguagem simples, com disclaimer obrigatório."

*[Mostrar resposta com disclaimer.]*

> "Agora vou testar um guardrail — uma pergunta que toca em conduta terapêutica."

*[Digitar: `"Posso tomar Omeprazol?"`]*

> "O guardrail de segurança bloqueia a resposta e orienta o paciente a consultar um médico. Este mecanismo é rastreado no campo `guardrails_acionados`."

---

### CENA 7 — Monitoramento e Métricas (3:30 – 4:00)
**Tela:** Navegar para `http://localhost:8000/metrics` (ou seção de Monitoramento no dashboard).

> "Para operação em produção, temos um endpoint de métricas que agrega dados do pipeline em tempo real.
> Aqui vemos: total de requisições processadas, latência média, taxa de bloqueio dos guardrails, e últimas violações.
> Essas métricas alimentam o dashboard de monitoramento — permitindo à equipe acompanhar a saúde do sistema sem abrir logs."

*[Mostrar JSON com métricas ou gráficos do dashboard.]*

---

### CENA 8 — Governança e LGPD (4:00 – 4:30)
**Tela:** Abrir `document/governanca_e_riscos.md` no editor ou no GitHub.

> "A governança de IA é crítica. Nossa política cobre LGPD — base legal, finalidade, minimização de dados — o sistema não armazena o laudo, só o histórico de chat e com direito de exclusão via API.
>
> Logging estruturado: cada requisição gera um log JSON com latência por nó do grafo — sanitize, retrieve, generate, guardrail — sem PII.
>
> Explicabilidade: toda resposta informa o painel especialista usado, as fontes recuperadas e guardrails acionados, tornando o agente auditável."

---

### CENA 9 — Encerramento (4:30 – 5:00)
**Tela:** Voltar para o dashboard ou slide final.

> "O Genera Intelligence entrega o que a Sprint 4 pede: um produto em produção, monitorável, rastreável e responsável.
> O paciente consegue entender seu laudo genético em linguagem acessível, o sistema garante que nunca vai substituir o médico, e a equipe consegue acompanhar tudo que acontece no pipeline.
>
> Obrigado. O repositório, as evidências e este vídeo estão disponíveis no GitHub privado compartilhado com o tutor."

---

## Checklist antes de gravar

- [ ] `make demo` sobe tudo limpo (sem erros no terminal)
- [ ] Backend responde em `http://localhost:8000/health` → `{"status":"ok"}`
- [ ] Frontend carrega em `http://localhost:3000`
- [ ] Chat retorna resposta com disclaimer visível
- [ ] Chat bloqueia pergunta de conduta terapêutica (guardrail)
- [ ] Página de histórico mostra ao menos 1 interação
- [ ] `/metrics/` retorna JSON com campos de monitoramento
- [ ] GitHub Actions tem pelo menos 1 run verde registrado
- [ ] Microfone testado, sem ruído de fundo
- [ ] Resolução de tela: 1920×1080 ou 1280×720

## Dicas de gravação

- **Tempo máximo:** 5 min. Ensaie uma vez medindo o tempo — o roteiro acima está calibrado em ~4:55.
- **Não precisa fazer tudo perfeito:** uma pausa natural ou uma re-digitação no chat são humanos e mostram que é ao vivo.
- **Fonte do terminal:** aumente para pelo menos 16pt para ficar legível no YouTube.
- **Subtítulos:** o YouTube gera automaticamente — não é necessário adicionar manualmente.
- **Upload:** configurar como "Não listado" antes de copiar o link para o README.
