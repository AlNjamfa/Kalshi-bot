import os 
import requests 
from dotenv import load_dotenv
from kalshi.auth import get_auth_headers
load_dotenv()
KALSHI_API_URL = "https://api.elections.kalshi.com/trade-api/v2"

def place_order(ticker, side, count, price):
    url = f"{KALSHI_API_URL}/portfolio/orders"
    path = "/trade-api/v2/portfolio/orders"
    headers = get_auth_headers("POST", path)
    body = {
        "ticker": ticker,
        "side": side,
        "count": count,
        "yes_price": price,
        "no_price": 100 - price,
        "type": "limit",
        "action": "buy"
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()
