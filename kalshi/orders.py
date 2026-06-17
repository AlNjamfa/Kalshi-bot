import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from kalshi.auth import get_auth_headers

load_dotenv()

KALSHI_API_URL = "https://api.elections.kalshi.com/trade-api/v2"

def already_traded_today(ticker, path="logs/trades.jsonl"):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    try:
        with open(path, "r") as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get("ticker") == ticker and entry.get("timestamp", "").startswith(today):
                    return True
    except FileNotFoundError:
        return False
    return False

def place_order(ticker, side, count, price):
    if already_traded_today(ticker):
        print(f"SKIP - already traded {ticker} today")
        return None
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
