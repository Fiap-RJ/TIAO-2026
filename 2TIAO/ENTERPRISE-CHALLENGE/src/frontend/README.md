# Frontend — Dashboard Genera (Sprint 3)

Interface do paciente para o Genera Intelligence: dashboard com cards de risco,
resumo de ancestralidade, histórico de interações e o chat com o agente RAG.

Stack: React 19 + Vite + Tailwind CSS + React Router. Gráficos com Recharts.
Testes com Vitest + Testing Library.

## Rodando localmente

```bash
npm install
npm run dev      # ambiente de desenvolvimento (proxy /api -> http://localhost:8000)
npm run build    # build de produção
npm run lint     # ESLint
npx vitest run   # testes
```

## Estrutura

```
src/
├── App.jsx                 # RouterProvider (rotas do dashboard)
├── pages/                  # HomePage, RiscosPage, AncestralidadePage, ChatPage, HistoricoPage
├── components/
│   ├── layout/             # AppShell (navegação + skip-link) e DisclaimerBar
│   ├── risco/              # RiskCard + riskLevelMap (categoria -> nível/cor)
│   ├── ancestralidade/     # AncestryChart (Recharts)
│   ├── historico/          # HistoryList (paginação client-side)
│   ├── chat/               # ChatWindow + MessageBubble
│   └── feedback/           # LoadingState, EmptyState, ErrorState
├── services/api.js         # client único de API (backend real)
├── test/fixtures/          # respostas reais do backend usadas nos testes
└── hooks/usePacienteId.js  # centraliza o paciente_id
```

## Camada de dados

`services/api.js` consome o backend real (`/api/riscos`, `/api/ancestralidade`,
`/api/historico`, `/api/chat/`) e adapta o contrato do servidor ao formato das
páginas. A base da URL vem de `VITE_API_BASE_URL`; vazio = caminhos relativos
(proxy do vite em dev, nginx no container). Os testes usam `fetch` mockado com
fixtures em `src/test/fixtures/`, copiadas de respostas reais do backend.

## Comunicação responsável

- Cores de risco usam uma escala **neutra** (baixo / moderado / atenção), sem
  vermelho puro nem termos alarmistas.
- `DisclaimerBar` fixo reforça que as informações não substituem avaliação médica.

## Acessibilidade

Práticas básicas cobertas nesta entrega:

- `lang="pt-BR"` no documento, skip-link "Pular para o conteúdo" e landmark `<main>`.
- Navegação por teclado com foco visível (`focus-visible:ring`) em links, botões e nav.
- Imagens com `alt`; o gráfico de ancestralidade tem `role="img"` + `aria-label` e
  legenda textual (não depende só de cor).
- Estados de carregamento (`role="status"`) e erro (`role="alert"`).
- Contraste: `genera-roxo` sobre branco ~17:1; para textos pequenos em magenta usamos
  o tom mais escuro `genera-magentahover` (~5.9:1) para ficar acima de 4.5:1.

> **Nota de honestidade:** este checklist cobre práticas básicas. Uma validação
> completa de conformidade WCAG exige testes manuais com tecnologias assistivas e
> revisão especializada, o que está fora do escopo desta sprint acadêmica.
