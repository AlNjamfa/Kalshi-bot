import os
import requests
from dotenv import load_dotenv

load_dotenv()

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

def get_crypto_price(coin_id):
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    return response.json()

def get_price_history(coin_id, days=7):
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    response = requests.get(url, params=params)
    return response.json()