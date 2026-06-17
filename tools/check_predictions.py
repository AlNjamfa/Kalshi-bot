import json
import requests
from kalshi.auth import get_auth_headers
from datetime import datetime

def load_predictions(path="logs/trades.jsonl"):
    predictions = []
    with open(path, "r") as f:
        for line in f:
            predictions.append(json.loads(line.strip()))
    return predictions

def get_market_result(ticker):
    path = f"/trade-api/v2/markets/{ticker}"
    headers = get_auth_headers("GET", path)
    r = requests.get(f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}", headers=headers)
    market = r.json().get("market", {})
    return {
        "status": market.get("status"),
        "result": market.get("result"),
        "ticker": ticker
    }

def check_predictions():
    predictions = load_predictions()
    correct = 0
    total = 0

    for p in predictions:
        if p.get("action") != "DRY_RUN":
            continue
        result = get_market_result(p["ticker"])
        if result["status"] != "finalized":
            continue
        total += 1
        resolved_yes = result["result"] == "yes"
        we_said_yes = p["recommendation"] == "YES"
        was_correct = resolved_yes == we_said_yes
        if was_correct:
            correct += 1
        print(f"{p['ticker']} | predicted: {p['recommendation']} @ {p['true_prob']} | resolved: {result['result']} | {'✓' if was_correct else '✗'}")

    if total > 0:
        print(f"\nAccuracy: {correct}/{total} = {round(correct/total * 100, 1)}%")
    else:
        print("No finalized markets yet.")

if __name__ == "__main__":
    check_predictions()