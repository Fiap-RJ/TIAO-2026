# Contrato da API consumido pelo Web e pelo Mobile

Formato que o front-end já espera do backend integrador. Os tipos completos estão em [`web/src/api/types.ts`](../web/src/api/types.ts). O objeto de avaliação (`RespostaAtendimento`) é **o mesmo schema da Fase 6** (`domain/schemas.py`), então o backend pode devolver a saída do pipeline sem conversão.

Se o backend precisar mudar algum campo, combine antes e atualize `types.ts` no web e no mobile.

## Regras gerais

- Prefixo `/api`, JSON em UTF-8, datas em ISO 8601 UTC (`2026-11-07T12:00:00Z`).
- Rotas autenticadas recebem `Authorization: Bearer <token>`. Token inválido ou expirado → **401** (o front volta para o login).
- Erros no formato do FastAPI: `{"detail": "mensagem legível"}`. O front mostra o `detail` ao usuário.
- CORS liberado para a URL da Vercel (e `http://localhost:5173` em desenvolvimento). O app Android não precisa de CORS.
- Perfil `paciente` só acessa o próprio `paciente_id` (**403** nos demais).

## Rotas

### `POST /api/auth/login`

```json
// requisição
{ "email": "medico@cardioia.com", "senha": "cardioia" }

// resposta 200
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "usuario": { "id": "u-medico", "nome": "Dra. Helena Prado", "perfil": "medico", "paciente_id": null }
}
```

`perfil` é `"medico"` ou `"paciente"`. Para o paciente, `paciente_id` aponta para o próprio cadastro. Credenciais inválidas → 401.

### `GET /api/pacientes`

Médico: todos os pacientes. Paciente: lista com um só item.

```json
[
  {
    "id": "p-001", "nome": "João Batista", "idade": 62, "leito": "UTI-C 04",
    "ultima_leitura": { "ts": "...", "temperatura": 37.5, "fc": 118, "spo2": 89, "estado": "critico" },
    "probabilidade": 0.99,
    "classificacao": "ALTO",
    "avaliado_em": "..."
  }
]
```

`ultima_leitura`, `probabilidade`, `classificacao` e `avaliado_em` podem ser `null` enquanto não houver dado.

### `GET /api/pacientes/{id}/status`

Consultada a cada 5 s pelo painel.

```json
{
  "paciente": { "id": "p-001", "nome": "João Batista", "idade": 62, "leito": "UTI-C 04" },
  "leituras": [ { "ts": "...", "temperatura": 37.5, "fc": 118, "spo2": 89, "estado": "critico" } ],
  "avaliacao": { /* RespostaAtendimento da Fase 6, ou null */ }
}
```

- `leituras`: até ~60 mais recentes, em **ordem cronológica crescente** (a última é a mais nova).
- `estado` (`normal` | `atencao` | `critico`) é a classificação local feita pelo dispositivo MicroPython.
- `avaliacao`: a avaliação mais recente do paciente.

### `POST /api/pacientes/{id}/avaliar`

Botão "Reavaliar agora" (só médico). Roda o pipeline da Fase 6 com as leituras atuais e devolve um `RespostaAtendimento`. Pode levar alguns segundos (agentes).

### `POST /api/chat`

```json
// requisição
{ "mensagem": "Por que o risco está alto?", "paciente_id": "p-001", "sessao_id": null }

// resposta 200
{ "resposta": "...", "sessao_id": "abc123", "origem": "watson" }
```

O front guarda o `sessao_id` e o reenvia nas próximas mensagens da mesma conversa. `origem`: `"watson"`, `"openai"` ou `"fallback"`.

### `POST /api/leituras` (ESP32, não usado pelo front)

```json
{ "paciente_id": "p-001", "temperatura": 37.5, "fc": 118, "spo2": 89, "estado": "critico", "ts": "..." }
```

Autenticada pelo header `X-Device-Key`. O front só lê essas leituras via `/status`.

## Como as features do modelo são montadas

O painel mostra o objeto `paciente` da avaliação (as 10 features). `fc_media`, `spo2_media` e `temperatura` vêm da média das leituras recentes do sensor. As outras 7 (carga do sistema, tempo de espera etc.) são indicadores operacionais simulados da unidade, guardados por paciente no backend.
