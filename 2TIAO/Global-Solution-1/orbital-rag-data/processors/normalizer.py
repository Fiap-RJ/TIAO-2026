import json
import os


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
        "resumo_alerta": resumo,
    }


def normalize_cme(raw: dict) -> dict:
    analyses = raw.get("cmeAnalyses") or [{}]
    cme_type = analyses[0].get("type", "N/A") if analyses else "N/A"
    return {
        "id_evento": f"CME-{raw.get('activityID', 'UNKNOWN')}",
        "tipo": "Tempestade Solar",
        "nome": raw.get("activityID", "CME"),
        "data_aproximacao": (raw.get("startTime") or "")[:10],
        "distancia_terra_km": 149600000,
        "risco_colisao": False,
        "resumo_alerta": f"Ejeção de massa coronal detectada. Classe: {cme_type}. Pode afetar satélites em órbita baixa.",
    }


def save_context_data(events: list, path: str = "output/context_data.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"✅ Salvo: {len(events)} eventos em {path}")
