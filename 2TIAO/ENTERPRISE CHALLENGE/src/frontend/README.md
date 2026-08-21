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
├── services/api.js         # client único de API (mock -> real)
├── mocks/                  # dados mockados enquanto os endpoints M1–M4 não existem
└── hooks/usePacienteId.js  # centraliza o paciente_id
```

## Camada de dados (mock → real)

Os endpoints do backend (riscos, ancestralidade, histórico — tarefas M1–M4) ainda
não existem. Enquanto isso, `services/api.js` lê de `src/mocks/` com a flag
`USE_MOCKS = true`. Cada função já segue o contrato de API esperado, então trocar
para os endpoints reais é só virar a flag para `false` — os componentes não mudam.

### Ancestralidade: dados ilustrativos

A fonte estruturada (`proposta_estrutura_de_dados.json`) **não contém dados de
ancestralidade**. Conforme alinhado com o time, a tela de ancestralidade usa dados
fictícios (marcados com `ilustrativo: true` no mock e com aviso visível na UI),
apenas para demonstrar a visualização. O ponto de troca para o dado real fica
isolado em `services/api.js`.

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
