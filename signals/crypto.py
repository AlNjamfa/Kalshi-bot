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

def analyze_crypto_market(coin_id, threshold, market_odds):
    try:
        current_data = get_crypto_price(coin_id)
        if coin_id not in current_data:
            return None
        current_price = current_data[coin_id]["usd"]
        history_data = get_price_history(coin_id)
        prices = [p[1] for p in history_data.get("prices", [])]
        if not prices:
            return None
        price_7d_ago = prices[0]
        trend = "up" if current_price > price_7d_ago else "down"
        diff_pct = ((current_price - threshold) / threshold) * 100
        if diff_pct >= 5 and trend == "up":
            true_prob = 0.82
            recommendation = "YES"
        elif diff_pct >= 2 and trend == "up":
            true_prob = 0.65
            recommendation = "YES"
        elif diff_pct >= 0 and trend == "up":
            true_prob = 0.55
            recommendation = "YES"
        elif diff_pct >= -3 and trend == "down":
            true_prob = 0.35
            recommendation = "NO"
        else:
            true_prob = 0.18
            recommendation = "NO"
        edge = true_prob - market_odds
        return {
            "coin": coin_id,
            "current_price": current_price,
            "threshold": threshold,
            "true_prob": true_prob,
            "market_odds": market_odds,
            "edge": edge,
            "recommendation": recommendation,
        }
    except Exception as e:
        print(f"crypto signal error: {e}")
        return None
