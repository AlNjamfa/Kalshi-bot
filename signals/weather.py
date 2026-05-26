import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NOAA_BASE_URL = "https://api.weather.gov"
NOAA_HEADERS = {
    "User-Agent": "kalshi-bot/1.0 (allenjamfa@gmail.com)",
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

def analyze_weather_market(lat, lon, market_type, threshold, market_odds):
    grid = get_grid(lat, lon)
    periods = get_forecast(grid["forecast_url"])
    today = periods[0]
    temp = today["temperature"]
    precip = today["probabilityOfPrecipitation"]["value"]

    if market_type == "rain":
        true_prob = precip / 100
        edge = true_prob - market_odds
        recommendation = "YES" if edge > 0.05 else "NO" if edge < -0.05 else "PASS"
        return {
            "market_type": market_type,
            "temp": temp,
            "precip_pct": precip,
            "true_prob": true_prob,
            "market_odds": market_odds,
            "edge": edge,
            "recommendation": recommendation,
        }

    elif market_type == "temp_above":
        diff = temp - threshold
        if diff >= 5:
            true_prob = 0.85
        elif diff >= 2:
            true_prob = 0.70
        elif diff >= 0:
            true_prob = 0.55
        else:
            true_prob = 0.25
        edge = true_prob - market_odds
        recommendation = "YES" if edge > 0.05 else "NO" if edge < -0.05 else "PASS"
        return {
            "market_type": market_type,
            "temp": temp,
            "threshold": threshold,
            "true_prob": true_prob,
            "market_odds": market_odds,
            "edge": edge,
            "recommendation": recommendation,
        }

    elif market_type == "temp_below":
        diff = temp - threshold
        if diff <= -5:
            true_prob = 0.85
        elif diff <= -2:
            true_prob = 0.70
        elif diff <= 0:
            true_prob = 0.55
        else:
            true_prob = 0.25
        edge = true_prob - market_odds
        recommendation = "YES" if edge > 0.05 else "NO" if edge < -0.05 else "PASS"
        return {
            "market_type": market_type,
            "temp": temp,
            "threshold": threshold,
            "true_prob": true_prob,
            "market_odds": market_odds,
            "edge": edge,
            "recommendation": recommendation,
        }

    return None
