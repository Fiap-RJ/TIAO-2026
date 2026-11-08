# CardioIA — Mobile (React Native + Expo)

App Android da CardioIA (Expo SDK 58 + Expo Router): login, lista de pacientes, painel do paciente com risco e sinais vitais em tempo real, e chat com o assistente. Usa o mesmo contrato de API do web.

## Rodar localmente

```bash
cd 2TIAO/FASE7-CARDIOIA/mobile
npm install
cp .env.example .env   # opcional: preencha EXPO_PUBLIC_API_URL
npx expo start         # abra no Expo Go (QR Code) ou em um emulador
```

Sem `EXPO_PUBLIC_API_URL`, o app entra no **modo demonstração** (mesmas contas do web, senha `cardioia`: `medico@cardioia.com` e `paciente@cardioia.com`).

## Arquivos de configuração obrigatórios

| Arquivo | Configuração |
|---|---|
| [`app.json`](app.json) | `android.package: "br.com.fiap.cardioia"` (domínio invertido), nome, ícones e plugins |
| [`eas.json`](eas.json) | Perfil `preview` com `android.buildType: "apk"` e distribuição interna |

## Gerar o APK (Expo Build / EAS)

```bash
npx eas-cli@latest login                      # conta Expo
npx eas-cli@latest init                       # vincula o projeto (grava o projectId no app.json)
npx eas-cli@latest build -p android --profile preview
```

Antes do build final, preencha `EXPO_PUBLIC_API_URL` no perfil `preview` do [`eas.json`](eas.json) com a URL pública do backend. A URL é embutida no APK no momento do build, então trocar a URL exige um novo build.

No fim do build, o EAS mostra o link da página do build no dashboard do Expo, com o botão de download do `.apk` e um QR Code. Esse link vai no README principal da fase.

### Instalar no celular

1. No Android, abra o link do build (ou leia o QR Code) e baixe o `.apk`.
2. Permita a instalação de apps de fontes desconhecidas quando o Android pedir.
3. Abra o CardioIA, entre com uma das contas e confira o painel do paciente.

## Scripts

| Comando | O que faz |
|---|---|
| `npm start` | Servidor de desenvolvimento do Expo |
| `npm run typecheck` | Checagem de tipos |
| `npm run lint` | ESLint (config do Expo) |
| `npm run build:apk` | Build do APK no EAS (perfil `preview`) |

## Estrutura

```
src/
├── app/              # rotas (Expo Router)
│   ├── _layout.tsx   # sessão + rotas protegidas
│   ├── login.tsx
│   ├── pacientes/    # lista e painel do paciente
│   └── chat/         # assistente
├── api/              # contrato, cliente HTTP e modo demonstração (cópias do web)
├── auth/             # sessão (token no expo-secure-store)
├── components/       # medidor de risco, tendências, selos
├── hooks/            # usePolling (pausa com o app em segundo plano)
└── lib/              # formatação e rótulos
```

Os arquivos em `src/api/` (exceto `client.ts`) e `src/lib/format.ts` são cópias dos equivalentes em `web/src/`. Ao alterar o contrato, atualize os dois.
