import os 
import requests 
from dotenv import load_dotenv

load_dotenv()

NOAA_BASE_URL = "https://api.weather.gov"

NOAA_HEADERS = {
    "User-Agent": "kalshi-bot/1.0 (Allenjamfa@gmail.com)",
    "Accept": "application/geo+json"
}


def get_grid(lat, lon):
    url = f"{NOAA_BASE_URL}/points/{lat},{lon}"
    response = requests.get(url, headers=NOAA_HEADERS)
    data = response.json()
    props = data["properties"]
    return {
        "gridId": props["gridId"],
        "gridX": props["gridX"],
        "gridY": props["gridY"],
        "forecast_url": props["forecast"],
    }

def get_forecast(forecast_url):
    response = requests.get(forecast_url, headers=NOAA_HEADERS)
    data = response.json()
    periods = data["properties"]["periods"]
    return periods
