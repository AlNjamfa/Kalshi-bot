import os
import requests
from dotenv import load_dotenv
from kalshi.auth import get_auth_headers

load_dotenv()
KALSHI_API_URL = "https://api.elections.kalshi.com/trade-api/v2"

def get_markets(limit=100, series_ticker=None):
    url = f"{KALSHI_API_URL}/markets"
    params = {"limit": limit, "status": "open", "series_ticker": series_ticker}
    path = "/trade-api/v2/markets"
    headers = get_auth_headers("GET", path)
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("markets", [])
