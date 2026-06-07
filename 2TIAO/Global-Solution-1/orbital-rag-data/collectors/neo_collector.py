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
