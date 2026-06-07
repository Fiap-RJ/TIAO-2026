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
