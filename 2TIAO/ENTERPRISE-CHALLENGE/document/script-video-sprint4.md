# Script — Vídeo de Apresentação Sprint 4
**Genera Intelligence · Challenge Dasa · 2TIAO**  
Duração alvo: **≤ 5 minutos** | Formato: narração humana, sem cortes longos

---

## Estrutura e timing

| # | Cena | Tela | Tempo |
|---|------|------|-------|
| 1 | Abertura | Slide ou terminal | 0:00 – 0:20 |
| 2 | Stack rodando local | Terminal — `make demo` | 0:20 – 0:50 |
| 3 | Dashboard de Riscos | Browser :3000 | 0:50 – 1:25 |
| 4 | Chat conversacional | Página Chat | 1:25 – 2:30 |
| 5 | Histórico de Interações | Página Histórico | 2:30 – 2:50 |
| 6 | Monitoramento de Pipeline | `/metrics/` no browser | 2:50 – 3:20 |
| 7 | Governança e LGPD | Arquivo de governança / código | 3:20 – 4:00 |
| 8 | CI e Automações | GitHub Actions | 4:00 – 4:30 |
| 9 | Encerramento | Slide ou terminal | 4:30 – 4:55 |

---

## Roteiro completo

---

### CENA 1 — Abertura (0:00 – 0:20)
**Tela:** Slide com logo do projeto ou terminal limpo.

> "Olá! Somos o grupo [NOME DO GRUPO] da turma 2TIAO da FIAP.
> Este é o Genera Intelligence — um assistente de IA que permite ao paciente conversar com seu próprio laudo genético.
> Neste vídeo mostramos a entrega final da Sprint 4: a solução rodando em produção, com monitoramento, governança de IA e a avaliação do modelo."

---

### CENA 2 — Stack subindo (0:20 – 0:50)
**Tela:** Terminal. Rodar `make demo` ao vivo.

> "Para subir o ambiente completo, basta um único comando: `make demo`.
> O Docker Compose constrói as imagens do backend em FastAPI e do frontend em React, e o entrypoint do backend gera automaticamente o índice vetorial FAISS na primeira execução — sem precisar de nenhum passo manual.
> Em segundos temos o backend saudável na porta 8000 e o frontend na porta 3000."

*[Mostrar o output do terminal com os dois containers `(healthy)`.]*

---

### CENA 3 — Dashboard de Riscos (0:50 – 1:25)
**Tela:** Browser em `http://localhost:3000`. Navegar para a seção de Riscos.

> "Aqui está o dashboard. A primeira seção mostra os riscos genéticos do paciente organizados por painel — Genera Nutri, Genera Fit, Genera Skin e outros.
> Cada marcador traz o gene envolvido, a classificação normalizada em três níveis — baixo, moderado e atenção — e a conclusão do laudo em linguagem acessível.
> Nenhum dado é inventado: tudo vem do JSON estruturado do laudo Genera, servido pelo backend em tempo real."

*[Rolar a página mostrando alguns cards de risco.]*

---

### CENA 4 — Chat conversacional (1:25 – 2:30)
**Tela:** Página de Chat do frontend. Digitar a primeira pergunta.

> "O coração do produto é o chat. Vou fazer uma pergunta real."

*[Digitar: `"O que significa eu metabolizar a cafeína de forma lenta?"`]*

> "O agente usa RAG — Retrieval-Augmented Generation — para buscar os trechos relevantes do laudo no FAISS e gerar uma resposta fundamentada.
> Veja: a resposta está em linguagem simples, dentro do limite de palavras configurado para o modo resumido, e termina sempre com o disclaimer obrigatório indicando que o assistente é informativo e não substitui consulta médica."

*[Mostrar a resposta com o disclaimer visível.]*

> "Vou fazer uma segunda pergunta para testar um guardrail."

*[Digitar: `"Posso tomar Omeprazol?"`]*

> "Quando a pergunta envolve conduta terapêutica — prescrição, automedicação — o guardrail de segurança é acionado. O agente recusa a resposta e orienta o paciente a procurar um médico. Esse mecanismo está registrado no campo `guardrails_acionados` da resposta."

---

### CENA 5 — Histórico de Interações (2:30 – 2:50)
**Tela:** Navegar para a página de Histórico.

> "Todo diálogo é persistido em SQLite e pode ser consultado na tela de histórico.
> Isso fecha o requisito de rastreabilidade — cada interação tem timestamp, paciente ID e o painel genético utilizado na resposta."

---

### CENA 6 — Monitoramento de Pipeline (2:50 – 3:20)
**Tela:** Navegar para a seção de Monitoramento no dashboard (ou abrir `http://localhost:3000/metrics/` no browser).

> "Para operação em produção, implementamos um endpoint de métricas que agrega dados do pipeline em tempo real.
> Aqui vemos o total de requisições processadas, a latência média, a taxa de bloqueio dos guardrails e as últimas violações registradas.
> Essas métricas alimentam o dashboard de monitoramento do frontend, permitindo acompanhar a saúde do sistema sem precisar abrir logs."

---

### CENA 7 — Governança e LGPD (3:20 – 4:00)
**Tela:** Abrir `document/governanca_e_riscos.md` no editor ou no GitHub.

> "A governança de IA é documentada na nossa Política de Governança, que cobre três eixos.
>
> Primeiro, LGPD: base legal, finalidade, minimização de dados — o sistema não armazena o laudo, só o histórico de chat — e o direito de exclusão implementado via `DELETE /api/historico/{paciente_id}`.
>
> Segundo, logging estruturado: cada requisição gera um log JSON com request ID, latência por nó do grafo — sanitize, retrieve, generate, guardrail — e violações registradas sem PII.
>
> Terceiro, explicabilidade: toda resposta do chat informa o painel especialista usado, as fontes recuperadas e os guardrails acionados, tornando o raciocínio do agente auditável."

---

### CENA 8 — CI e Automações (4:00 – 4:30)
**Tela:** Aba do GitHub Actions ou arquivo `.github/workflows/`.

> "Para automação, configuramos o GitHub Actions com dois workflows.
> O workflow de push roda lint com Ruff e o conjunto de testes a cada commit.
> O workflow de avaliação — que também pode ser disparado manualmente — executa o LLM-as-a-Judge com 30 casos de teste e salva o relatório comparativo em `document/evidencias/`, permitindo rastrear a evolução da qualidade do modelo sprint a sprint."

---

### CENA 9 — Encerramento (4:30 – 4:55)
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
