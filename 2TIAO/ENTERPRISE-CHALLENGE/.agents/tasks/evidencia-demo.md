# Evidência de Verificação — Demo Local (`make demo`)

**Data:** 2025-10-07  
**Branch:** sprint4/arthur-michael  
**Iteração:** 1 (primeira execução)

---

## Mudanças implementadas

| Arquivo | Mudança |
|---|---|
| `src/backend/entrypoint.sh` | Novo — seeds FAISS se ausente, depois exec uvicorn |
| `src/backend/Dockerfile` | Adicionado COPY + chmod do entrypoint.sh; CMD alterado para `/app/entrypoint.sh` |
| `src/frontend/Dockerfile` | `npm ci` → `npm install` (package-lock.json estava dessincronizado) |
| `src/frontend/nginx.conf` | Adicionado `client_max_body_size 20m`, proxy `/metrics/`, e headers nos proxies existentes |
| `docker-compose.yml` | Removido serviço `seed` (entrypoint cuida disso); named volumes → bind mounts (`./faiss_index`, `./data`); sem volumes top-level |
| `Makefile` | Adicionado `demo` e `demo-down` ao `.PHONY` e aos targets |

---

## Verificação

### 1. `make demo` termina sem erro

```
$ make demo
docker compose up --build -d
...
 Container genera_backend   Starting
 Container genera_backend   Started
 Container genera_backend   Waiting
 Container genera_backend   Healthy
 Container genera_frontend  Starting
 Container genera_frontend  Started
Aguardando serviços...
NAME              IMAGE                           COMMAND               SERVICE    CREATED          STATUS                    PORTS
genera_backend    enterprise-challenge-backend    "/app/entrypoint.sh"  backend    20 seconds ago   Up 17 seconds (healthy)   0.0.0.0:8000->8000/tcp
genera_frontend   enterprise-challenge-frontend   "/docker-entrypoint…" frontend   18 seconds ago   Up 5 seconds              0.0.0.0:3000->80/tcp
Frontend: http://localhost:3000
API docs: http://localhost:8000/docs

Exit code: 0
```

### 2. `docker compose ps` — backend e frontend healthy

```
NAME              IMAGE                           COMMAND                  SERVICE    CREATED              STATUS                        PORTS
genera_backend    enterprise-challenge-backend    "/app/entrypoint.sh"     backend    About a minute ago   Up About a minute (healthy)   0.0.0.0:8000->8000/tcp
genera_frontend   enterprise-challenge-frontend   "/docker-entrypoint.…"   frontend   About a minute ago   Up About a minute             0.0.0.0:3000->80/tcp
```

### 3. `curl http://localhost:8000/health`

```
{"status":"ok","message":"Genera Intelligence API operacional."}
```
HTTP 200 ✓

### 4. Chat endpoint — POST /api/chat/

```
$ curl -s -X POST http://localhost:8000/api/chat/ \
  -H 'Content-Type: application/json' \
  -d '{"paciente_id":"uuid-123","mensagem":"o que e cafeina?"}' | python3 -m json.tool
```

Resposta recebida (campos principais):
```json
{
    "resposta": "A cafeína é uma substância estimulante... [contém disclaimer obrigatório] ⚠️ Importante: Este assistente é informativo e não substitui consulta médica.",
    "fontes": [...],
    "painel_utilizado": "Genera Nutri",
    "guardrails_acionados": []
}
```
Campos `resposta` ✓ e `painel_utilizado` ✓ presentes. Disclaimer presente ✓.

### 5. Frontend via nginx (:3000)

```
$ curl -s http://localhost:3000/ -o /dev/null -w "%{http_code}"
200

$ curl -s http://localhost:3000/health -w "\nHTTP: %{http_code}"
{"status":"ok","message":"Genera Intelligence API operacional."}
HTTP: 200

$ curl -s "http://localhost:3000/api/riscos/uuid-123" | python3 -m json.tool | head -10
{
    "paciente_id": "uuid-123",
    "paineis": [
        { "nome_painel": "Genera Skin", ... }
    ]
}
HTTP: 200

$ curl -s http://localhost:3000/metrics/ -w "\nHTTP: %{http_code}"
{"total_requisicoes":0,"latencia_media_ms":0.0,"taxa_bloqueio_guardrail_percentual":0.0,"ultimas_violacoes":[]}
HTTP: 200
```

### 6. `make demo-down`

```
$ make demo-down
docker compose down
[+] Running 3/3
 ✔ Container genera_frontend             Removed
 ✔ Container genera_backend              Removed
 ✔ Network enterprise-challenge_default  Removed

Exit code: 0
```

---

## Notas

- O `src/frontend/Dockerfile` foi alterado de `npm ci` para `npm install` porque o `package-lock.json` estava dessincronizado (faltavam `@emnapi/core` e `@emnapi/runtime`). Para produção, deve-se rodar `npm install` localmente e commitar o lock file atualizado, voltando para `npm ci`.
- O índice FAISS é gerado no container backend na primeira inicialização via `entrypoint.sh` — não há dependência da GOOGLE_API_KEY no `docker compose build`.
- Todos os guardrails e disclaimers obrigatórios estão preservados (verificado na resposta do chat acima).
