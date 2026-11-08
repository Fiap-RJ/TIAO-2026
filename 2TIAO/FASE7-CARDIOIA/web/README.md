# CardioIA — Web (React + Vite)

Painel web da CardioIA: login, lista de pacientes ordenada por risco, painel do paciente (medidor de risco, sinais vitais em tempo real, protocolos, ações operacionais) e chat com o assistente.

## Rodar localmente

```bash
cd 2TIAO/FASE7-CARDIOIA/web
npm install
cp .env.example .env.local   # opcional: preencha VITE_API_URL
npm run dev                  # http://localhost:5173
```

Sem `VITE_API_URL`, o app entra no **modo demonstração**, com dados simulados no navegador. Contas de demonstração (senha `cardioia`):

| Perfil | E-mail | O que vê |
|---|---|---|
| Médico | `medico@cardioia.com` | Lista de pacientes e o painel de cada um, com reavaliação e indicadores do modelo |
| Paciente | `paciente@cardioia.com` | Só o próprio painel e o chat |

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `VITE_API_URL` | URL pública do backend integrador, sem barra no final (ex.: `https://cardioia-api.onrender.com`) |
| `VITE_USE_MOCK` | `true` força o modo demonstração |

As variáveis `VITE_*` são embutidas no build. Depois de alterar na Vercel, faça um novo deploy.

## Deploy na Vercel (CI/CD)

1. Em [vercel.com/new](https://vercel.com/new), importe o repositório `Fiap-RJ/TIAO-2026` (é preciso autorizar o acesso da Vercel à organização no GitHub).
2. **Root Directory:** `2TIAO/FASE7-CARDIOIA/web`. O framework (Vite), o build (`npm run build`) e a saída (`dist`) vêm do [`vercel.json`](vercel.json).
3. Em **Environment Variables**, cadastre `VITE_API_URL` com a URL do backend.
4. Clique em **Deploy**. A partir daí, cada push na `main` publica a produção, e cada PR gera uma URL de preview.

O [`vercel.json`](vercel.json) reescreve todas as rotas para `index.html`, para que recarregar ou abrir direto `/pacientes/p-001` funcione (rotas SPA).

Além da Vercel, o workflow [`fase7-cardioia.yml`](../../../.github/workflows/fase7-cardioia.yml) roda lint e build a cada push e PR que altere esta pasta.

## Scripts

| Comando | O que faz |
|---|---|
| `npm run dev` | Servidor de desenvolvimento |
| `npm run build` | Checagem de tipos + build de produção em `dist/` |
| `npm run preview` | Serve o build localmente |
| `npm run lint` | Oxlint |

## Estrutura

```
src/
├── api/          # contrato (types.ts), cliente HTTP, modo demonstração (mock.ts)
├── auth/         # sessão (token JWT no localStorage)
├── components/   # medidor de risco, gráficos, chat, layout
├── hooks/        # usePolling (atualização a cada 5–10 s)
├── lib/          # formatação e rótulos
└── pages/        # login, lista de pacientes, painel do paciente
```
