# Spec de Implementação — Dashboard Genera (parte do Arthur)

> Detalha como implementar as tarefas A1–A7 definidas em
> [`SPRINT3.md`](./SPRINT3.md). Este documento não repete o "porquê" (já coberto
> em `SPRINT3.md` e nos steering files `.kiro/steering/product.md` e
> `structure.md`) — foca no "como".

## 1. Escopo

**Dentro do escopo (Arthur):**
- Frontend em `src/frontend/` (React + Vite + Tailwind).
- Dashboard com cards de risco, resumo de ancestralidade, histórico de
  interações e integração com o chat já existente (`App.jsx`).

**Fora do escopo (não fazer aqui):**
- Endpoints novos no backend (M1–M4 em `SPRINT3.md`, responsabilidade do
  Michael) — este spec assume que eles ainda **não existem** e propõe uma
  camada de mock para não bloquear o trabalho.
- Lógica de personalização/simplificação/resumo do agente (N1–N6, Nathalia).
- Persistência real de histórico (M4) — o front só consome o endpoint quando
  ele existir.

## 2. Achado importante (bloqueio a resolver com o time)

O arquivo `proposta_estrutura_de_dados.json` (fonte de verdade dos dados
estruturados) **não contém nenhum campo de ancestralidade** — só painéis de
risco (`Genera Skin`, `Genera Fit`, `Genera Nutri`, etc., cada um com
`caracteristica`, `categoria_impacto`, `dados_tecnicos`, `conclusao_curta`,
`explicacao_detalhada`, `recomendacoes`).

Ação: alinhar com o time se (a) a ancestralidade virá de outro painel/fonte
de dados ainda não versionada, (b) será um dado mockado/fictício para fins
acadêmicos, ou (c) o requisito deve ser reinterpretado como "resumo do
perfil genético" em vez de ancestralidade genômica real. **Até essa decisão,
construir o componente A3 com dado mockado e a interface pronta para trocar
a fonte.**

## 3. Contratos de API esperados (a confirmar com Michael — M1–M4)

Como os endpoints ainda não existem, criar uma camada `src/services/api.js`
com funções que hoje leem de mocks locais (`src/mocks/`) e depois trocam para
`fetch` real sem alterar os componentes. Contratos propostos:

```
GET /api/riscos/{paciente_id}
→ [{ painel, caracteristica, categoria_impacto, conclusao_curta, explicacao_detalhada, recomendacoes[] }]

GET /api/ancestralidade/{paciente_id}
→ { componentes: [{ regiao, percentual }] }   // formato provisório, ver seção 2

GET /api/resumos/{paciente_id}
→ { resumo_relatorio: string, resumo_interacoes: string, atualizado_em: string }

GET /api/historico/{paciente_id}
→ [{ id, timestamp, pergunta, resposta, fontes[] }]
```

O `ChatResponse` já existe em `domain/schemas.py` (`resposta`, `fontes[]`) —
reutilizar esse formato para mensagens do chat dentro do histórico.

## 4. Dependências novas a instalar

```bash
npm install react-router-dom recharts
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

- `react-router-dom`: navegação entre seções (A1).
- `recharts`: gráfico de composição de ancestralidade (A3) — leve, sem
  dependência de canvas nativo, boa integração com Tailwind.
- `vitest` + `@testing-library/react`: não há setup de teste no frontend
  hoje; usar Vitest por já rodar sobre a config do Vite existente.

## 5. Estrutura de pastas proposta

```
src/frontend/src/
├── App.jsx                 # passa a ser só o <RouterProvider>
├── main.jsx
├── pages/
│   ├── HomePage.jsx         # A1 — landing do dashboard
│   ├── RiscosPage.jsx       # A2
│   ├── AncestralidadePage.jsx # A3
│   ├── ChatPage.jsx         # A5 — chat atual movido para cá
│   └── HistoricoPage.jsx    # A4
├── components/
│   ├── layout/
│   │   ├── AppShell.jsx     # header + navegação lateral/tab (A1)
│   │   └── DisclaimerBar.jsx # aviso fixo de governança (reaproveita texto do App.jsx atual)
│   ├── risco/
│   │   ├── RiskCard.jsx      # A2
│   │   └── riskLevelMap.js   # mapeamento categoria_impacto → cor/label (A2)
│   ├── ancestralidade/
│   │   └── AncestryChart.jsx # A3
│   ├── historico/
│   │   └── HistoryList.jsx   # A4
│   ├── chat/                 # conteúdo atual de App.jsx extraído
│   │   ├── ChatWindow.jsx
│   │   └── MessageBubble.jsx
│   └── feedback/
│       ├── LoadingState.jsx  # A6
│       ├── EmptyState.jsx    # A6
│       └── ErrorState.jsx    # A6
├── services/
│   └── api.js                # A5 — client único de API (mock → real)
├── mocks/
│   ├── riscos.mock.json
│   ├── ancestralidade.mock.json
│   └── historico.mock.json
└── hooks/
    └── usePacienteId.js       # centraliza o "uuid-123" hardcoded hoje no App.jsx
```

## 6. Detalhamento por tarefa

### A1 — Layout base do dashboard
- Adicionar `react-router-dom`, criar rotas: `/`, `/riscos`, `/ancestralidade`,
  `/chat`, `/historico`.
- `AppShell.jsx`: cabeçalho com logo (reaproveitar `assets/logo-genera.png`) +
  navegação (tabs no mobile, sidebar no desktop ≥ `md:`).
- Critério de aceite: navegar entre as 4 seções sem reload, com a seção
  atual destacada visualmente.

### A2 — Cards de risco
- `riskLevelMap.js`: mapear `categoria_impacto` (valores vistos no JSON:
  `"Cuidados relevantes"`, `"Pontos de atenção"`) para um nível neutro
  (`baixo` / `moderado` / `atencao`) e cor Tailwind — **nunca vermelho puro
  nem palavras como "risco alto"/"perigo"**. Sugestão de paleta:
  - `baixo` → tons de verde-acinzentado (`bg-emerald-50 text-emerald-800`)
  - `moderado` → tons neutros âmbar (`bg-amber-50 text-amber-800`)
  - `atencao` → tom `genera-magenta` suave (`bg-pink-50 text-genera-magenta`),
    mantendo a identidade visual já definida em `tailwind.config.js`.
- `RiskCard.jsx`: exibe `painel`, `caracteristica`, `conclusao_curta` e um
  botão "ver detalhes" que expande `explicacao_detalhada` + `recomendacoes`.
- Agrupar cards por `painel` (accordion ou seção por painel) na
  `RiscosPage.jsx`.
- Critério de aceite: nenhum card usa cor de alerta agressiva; todo card tem
  estado expandido/colapsado; dados vêm de `services/api.js` (mock por ora).

### A3 — Resumo de ancestralidade
- `AncestryChart.jsx` usando `recharts` (`PieChart` ou `BarChart`).
- Consumir `mocks/ancestralidade.mock.json` até M2 (Michael) ficar pronto —
  ver bloqueio da seção 2.
- Critério de aceite: gráfico renderiza com legenda acessível (texto
  alternativo, não depender só de cor para diferenciar categorias).

### A4 — Histórico de interações
- `HistoryList.jsx`: lista cronológica reversa (mais recente primeiro) de
  pergunta/resposta, reaproveitando `MessageBubble.jsx` do chat para
  consistência visual.
- Paginação simples (client-side, ex.: 10 itens por página) já que o volume
  é pequeno neste estágio.
- Critério de aceite: histórico carrega via `services/api.js`; estado vazio
  tratado (ver A6).

### A5 — Integração do chat existente
- Extrair a lógica de `App.jsx` atual para `ChatWindow.jsx` +
  `MessageBubble.jsx`, mantendo o comportamento existente (envio de
  mensagem, upload de PDF, exibição de fontes).
- Trocar o `paciente_id` hardcoded (`"uuid-123"`) por `usePacienteId()` (por
  ora pode continuar retornando um valor fixo, mas centralizado em um único
  lugar).
- Quando Nathalia expuser resumo/personalização na resposta, exibir
  disclaimer e resumo conforme formato que ela definir (N3–N5) — **não
  implementar a lógica de simplificação aqui, só o espaço de exibição**.
- Critério de aceite: comportamento do chat atual preservado 1:1 após a
  extração (regressão zero).

### A6 — Estados de carregamento e erro
- Componentes genéricos `LoadingState`, `EmptyState`, `ErrorState` em
  `components/feedback/`, reutilizados em todas as páginas que buscam dados
  via `services/api.js`.
- Critério de aceite: toda chamada de API tem os 3 estados cobertos (nunca
  tela branca em caso de falha).

### A7 — Responsividade e acessibilidade básica
- Testar em breakpoints `sm`/`md`/`lg` do Tailwind.
- Checklist mínimo:
  - Contraste de texto ≥ 4.5:1 (validar cores customizadas `genera-roxo` /
    `genera-magenta` sobre fundo branco).
  - Todos os elementos interativos alcançáveis por `Tab`, com `:focus`
    visível.
  - Imagens com `alt` (logo já tem, gráfico de ancestralidade precisa).
- Critério de aceite: navegação completa do dashboard só com teclado, sem
  perder o foco visualmente.

> Nota de honestidade: este checklist cobre práticas básicas de
> acessibilidade. Validação completa de conformidade WCAG exige testes
> manuais com tecnologias assistivas e revisão especializada — fora do
> escopo desta sprint acadêmica, mas vale citar essa limitação no README.

## 7. Testes

- Configurar Vitest (`vite.config.js` já existe, adicionar bloco `test`).
- Cobertura mínima sugerida: `riskLevelMap.js` (mapeamento categoria→cor),
  `RiskCard.jsx` (renderiza dados corretamente), `services/api.js` (mock
  responde formato esperado).
- Não é necessário cobertura exaustiva — este é um projeto acadêmico; o
  objetivo é mostrar rigor técnico, não 100% de cobertura.

## 8. Definição de Pronto (DoD) desta parte

- [ ] Rotas A1 funcionando sem reload de página.
- [ ] Cards de risco (A2) renderizando os painéis do JSON estruturado com
      paleta não-alarmista.
- [ ] Gráfico de ancestralidade (A3) renderizando com dado mock e ponto de
      troca claro para dado real.
- [ ] Histórico (A4) listando itens mockados/reais.
- [ ] Chat (A5) extraído para componentes, comportamento preservado.
- [ ] Estados de loading/empty/erro (A6) em todas as telas com fetch.
- [ ] Checklist de acessibilidade básica (A7) validado manualmente.
- [ ] `npm run lint` e `npm run build` passam sem erro.
- [ ] Testes novos (`npx vitest run`) passam.

## 9. Referências

- Tarefas e distribuição do time: [`SPRINT3.md`](./SPRINT3.md) (seção Arthur, A1–A7)
- Contexto de produto: `.kiro/steering/product.md`
- Convenções de estrutura: `.kiro/steering/structure.md`
- Stack e comandos: `.kiro/steering/tech.md`
- Dados estruturados fonte: `proposta_estrutura_de_dados.json`
- Contrato atual de chat: `src/backend/domain/schemas.py`, `src/backend/api/routes/chat.py`
- Estado atual do frontend: `src/frontend/src/App.jsx`
