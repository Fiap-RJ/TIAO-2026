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
