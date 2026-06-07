# 🛰️ Orbital RAG — Plano de Execução: Arthur

---

## ⚠️ Prioridade máxima: `context_data.json`

O Michael já finalizou o core da API. Ele está esperando o `context_data.json` para injetar na IA. **Esta é a tarefa mais crítica do projeto — execute antes de qualquer outra coisa.**

---

## 📋 Suas responsabilidades

| # | Tarefa | Prioridade |
|---|--------|-----------|
| 1 | Gerar e entregar o `context_data.json` (mock) | 🔴 CRÍTICO |
| 2 | Mapear e implementar os scripts Python de coleta | 🟠 Alta |
| 3 | Implementar o normalizador e pipeline completo | 🟠 Alta |
| 4 | Fluxograma da arquitetura (para o PDF da Nathalia) | 🟡 Média |
| 5 | Gravar a demonstração final | 🟡 Média |

---

## Tarefa 1 — Mock de dados: `context_data.json`

Gere este arquivo agora e envie ao Michael. Nenhum código Python é necessário para esta etapa — copie e salve.

```json
[
  {
    "id_evento": "NEO-2026-001",
    "tipo": "Asteroide",
    "nome": "Apophis",
    "data_aproximacao": "2026-06-15",
    "distancia_terra_km": 5000000,
    "risco_colisao": true,
    "resumo_alerta": "Asteroide de grande porte passando a uma distância segura, mas requer monitoramento contínuo pela proximidade com a órbita terrestre."
  },
  {
    "id_evento": "DONKI-2026-042",
    "tipo": "Tempestade Solar",
    "nome": "CME-X2.1",
    "data_aproximacao": "2026-06-10",
    "distancia_terra_km": 149600000,
    "risco_colisao": false,
    "resumo_alerta": "Ejeção de massa coronal de classe X2.1 detectada. Pode causar interferência em satélites em órbita baixa e interrupções em comunicações de rádio de alta frequência."
  },
  {
    "id_evento": "NEO-2026-007",
    "tipo": "Asteroide",
    "nome": "2023 DW",
    "data_aproximacao": "2026-07-02",
    "distancia_terra_km": 1800000,
    "risco_colisao": false,
    "resumo_alerta": "Objeto próximo à Terra de tamanho moderado (50m de diâmetro estimado). Passagem dentro da órbita lunar. Sem risco de impacto."
  },
  {
    "id_evento": "DONKI-2026-015",
    "tipo": "Tempestade Geomagnética",
    "nome": "GST-G3",
    "data_aproximacao": "2026-06-08",
    "distancia_terra_km": 149600000,
    "risco_colisao": false,
    "resumo_alerta": "Tempestade geomagnética de nível G3 em curso. Operadoras de satélites em órbita polar devem aumentar monitoramento."
  },
  {
    "id_evento": "DEBRIS-2026-099",
    "tipo": "Detrito Orbital",
    "nome": "SL-16 R/B",
    "data_aproximacao": "2026-06-12",
    "distancia_terra_km": 420,
    "risco_colisao": true,
    "resumo_alerta": "Fragmento de estágio de foguete russo em órbita decaindo. Probabilidade de reentrada atmosférica nos próximos 72h. Área de risco: Oceano Pacífico central."
  },
  {
    "id_evento": "DONKI-2026-031",
    "tipo": "Radiação Solar",
    "nome": "SEP-M7.4",
    "data_aproximacao": "2026-06-09",
    "distancia_terra_km": 149600000,
    "risco_colisao": false,
    "resumo_alerta": "Evento de partículas energéticas solares detectado após flare M7.4. Risco moderado para eletrônica de satélites não blindados."
  },
  {
    "id_evento": "NEO-2026-012",
    "tipo": "Asteroide",
    "nome": "Bennu",
    "data_aproximacao": "2026-09-22",
    "distancia_terra_km": 7400000,
    "risco_colisao": false,
    "resumo_alerta": "Asteroide carbonáceo bem estudado pela missão OSIRIS-REx. Próxima aproximação dentro do intervalo de monitoramento de rotina da NASA."
  }
]
```

---

## Tarefa 2 — Mapeamento das APIs

As chaves de API estão configuradas em `.env`. Os scripts assumem isso.

### APIs a implementar

**NASA NeoWs — Asteroids Near Earth Objects**
- Endpoint: `GET https://api.nasa.gov/neo/rest/v1/feed`
- Parâmetros: `start_date`, `end_date`, `api_key`
- Dados relevantes: diâmetro, velocidade, distância de aproximação, flag `is_potentially_hazardous_asteroid`

**NASA DONKI — Space Weather**
- Tempestades solares (CME): `GET https://api.nasa.gov/DONKI/CME`
- Tempestades geomagnéticas: `GET https://api.nasa.gov/DONKI/GST`
- Radiação solar: `GET https://api.nasa.gov/DONKI/SEP`
- Mesma `NASA_API_KEY` da NeoWs

**Space-Track — Debris / TLEs** *(complementar)*
- Requer autenticação via POST de login antes de cada sessão
- Endpoint: `https://www.space-track.org/basicspacedata/`

### Mapeamento de campos NeoWs → `context_data.json`

| Campo NASA (NeoWs) | Campo no JSON |
|---|---|
| `neo_reference_id` | `id_evento` |
| `name` | `nome` |
| `close_approach_data[0].close_approach_date` | `data_aproximacao` |
| `close_approach_data[0].miss_distance.kilometers` | `distancia_terra_km` |
| `is_potentially_hazardous_asteroid` | `risco_colisao` |
| *(gerado no normalizer)* | `resumo_alerta` |

---

## Tarefa 3 — Scripts Python

### Estrutura de pastas

```
orbital-rag-data/
├── .env
├── requirements.txt
├── collectors/
│   ├── neo_collector.py
│   └── donki_collector.py
├── processors/
│   └── normalizer.py
├── output/
│   └── context_data.json
└── main.py
```

### `.env`

```
NASA_API_KEY=sua_chave_aqui
SPACE_TRACK_USER=seu_usuario
SPACE_TRACK_PASS=sua_senha
```

### `requirements.txt`

```
requests==2.31.0
python-dotenv==1.0.0
```

### `collectors/neo_collector.py`

```python
import requests
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
NASA_KEY = os.getenv("NASA_API_KEY")

def fetch_asteroids(days_ahead: int = 7) -> list:
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=days_ahead)).isoformat()
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    params = {"start_date": start, "end_date": end, "api_key": NASA_KEY}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()
    asteroids = []
    for date_key, objs in raw["near_earth_objects"].items():
        asteroids.extend(objs)
    return asteroids
```

### `collectors/donki_collector.py`

```python
import requests
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
NASA_KEY = os.getenv("NASA_API_KEY")
BASE = "https://api.nasa.gov/DONKI"

def fetch_events(endpoint: str, days_back: int = 7) -> list:
    start = (date.today() - timedelta(days=days_back)).isoformat()
    end = date.today().isoformat()
    params = {"startDate": start, "endDate": end, "api_key": NASA_KEY}
    response = requests.get(f"{BASE}/{endpoint}", params=params, timeout=10)
    response.raise_for_status()
    return response.json() or []

def fetch_cme() -> list:
    return fetch_events("CME")

def fetch_gst() -> list:
    return fetch_events("GST")

def fetch_sep() -> list:
    return fetch_events("SEP")
```

### `processors/normalizer.py`

```python
import json

def normalize_asteroid(raw: dict) -> dict:
    approach = raw.get("close_approach_data", [{}])[0]
    dist_km = float(approach.get("miss_distance", {}).get("kilometers", 0))
    is_hazardous = raw.get("is_potentially_hazardous_asteroid", False)

    if is_hazardous and dist_km < 1_000_000:
        resumo = f"ALERTA: {raw['name']} se aproxima a {dist_km:,.0f} km. Classificado como potencialmente perigoso pela NASA."
    elif is_hazardous:
        resumo = f"{raw['name']} é potencialmente perigoso, mas a aproximação atual ocorre a distância segura de {dist_km:,.0f} km."
    else:
        resumo = f"Asteroide {raw['name']} com passagem prevista a {dist_km:,.0f} km. Sem risco de impacto identificado."

    return {
        "id_evento": f"NEO-{raw.get('neo_reference_id', 'UNKNOWN')}",
        "tipo": "Asteroide",
        "nome": raw.get("name", "Desconhecido"),
        "data_aproximacao": approach.get("close_approach_date", ""),
        "distancia_terra_km": round(dist_km),
        "risco_colisao": is_hazardous,
        "resumo_alerta": resumo
    }

def normalize_cme(raw: dict) -> dict:
    return {
        "id_evento": f"CME-{raw.get('activityID', 'UNKNOWN')}",
        "tipo": "Tempestade Solar",
        "nome": raw.get("activityID", "CME"),
        "data_aproximacao": raw.get("startTime", "")[:10],
        "distancia_terra_km": 149600000,
        "risco_colisao": False,
        "resumo_alerta": f"Ejeção de massa coronal detectada. Classe: {raw.get('cmeAnalyses', [{}])[0].get('type', 'N/A') if raw.get('cmeAnalyses') else 'N/A'}. Pode afetar satélites em órbita baixa."
    }

def save_context_data(events: list, path: str = "output/context_data.json"):
    import os
    os.makedirs("output", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"✅ Salvo: {len(events)} eventos em {path}")
```

### `main.py`

```python
from collectors.neo_collector import fetch_asteroids
from collectors.donki_collector import fetch_cme, fetch_gst
from processors.normalizer import normalize_asteroid, normalize_cme, save_context_data

if __name__ == "__main__":
    print("🛰️  Coletando dados da NASA...")
    events = []

    raw_asteroids = fetch_asteroids(days_ahead=7)
    events += [normalize_asteroid(a) for a in raw_asteroids]
    print(f"  → {len(raw_asteroids)} asteroides coletados")

    raw_cmes = fetch_cme()
    events += [normalize_cme(c) for c in raw_cmes]
    print(f"  → {len(raw_cmes)} eventos CME coletados")

    save_context_data(events)
    print(f"🎯 Pipeline concluído. {len(events)} eventos exportados.")
```

---

## Tarefa 4 — Fluxograma (para o PDF)

O fluxograma está gerado e disponível para screenshot neste chat. Para o PDF, faça um print da imagem em alta resolução. A arquitetura representada:

```
[NASA NeoWs] [NASA DONKI] [Space-Track] [News+PDFs]
      │            │            │              │
      └────────────┴────────────┴──────────────┘
                           │
                    collectors/ (Python)
                           │
                    normalizer.py
                           │
               ┌───────────┴────────────┐
               │                        │
        context_data.json         vectorstore/
               │                  (ChromaDB)
               └───────────┬────────────┘
                            │
                   LangGraph Agent (Michael)
                            │
                    LLM (OpenAI/Gemini)
                            │
                   POST /api/chat
                            │
              ┌─────────────┴─────────────┐
              │                           │
          Dashboard                    Chat UI
                    (Nathalia)
```

---

## Tarefa 5 — Gravação da demonstração

**Regras obrigatórias:**
- Duração máxima: 5 minutos
- Falar **"QUERO CONCORRER"** nos primeiros 30 segundos
- Subir no YouTube como **Não Listado** e passar o link para a Nathalia

### Roteiro sugerido

| Tempo | Conteúdo |
|---|---|
| 0:00–0:20 | Apresentação + "QUERO CONCORRER" |
| 0:20–1:00 | Contexto do problema |
| 1:00–2:00 | Mostrar o dashboard |
| 2:00–3:30 | Demo ao vivo: digitar pergunta no chat, IA responde com dados da NASA |
| 3:30–4:30 | Mostrar brevemente o código e o `context_data.json` |
| 4:30–5:00 | Conclusão |

---

## Checklist de execução

- [ ] Criar e enviar `context_data.json` para o Michael
- [ ] Criar pasta `orbital-rag-data/` e instalar dependências
- [ ] Implementar e testar `neo_collector.py`
- [ ] Implementar e testar `donki_collector.py`
- [ ] Implementar `normalizer.py` e gerar JSON com dados reais
- [ ] Confirmar que o `context_data.json` final está funcionando no backend do Michael
- [ ] Enviar fluxograma (screenshot) para a Nathalia incluir no PDF
- [ ] Gravar demonstração e subir no YouTube como Não Listado
- [ ] Passar link do YouTube para a Nathalia
