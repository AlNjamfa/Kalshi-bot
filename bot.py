import os
import json
from datetime import datetime
from kalshi.markets import get_markets
from kalshi.orders import place_order
from signals.crypto import analyze_crypto_market
from signals.weather import analyze_weather_market
from dotenv import load_dotenv
load_dotenv()

EDGE_THRESHOLD = 0.05
DRY_RUN = True
BANKROLL = float(os.getenv("BANKROLL", 500))
MAX_KELLY = float(os.getenv("MAX_KELLY_FRACTION", 0.25))
LOG_FILE = "logs/trades.jsonl"

WEATHER_MARKETS = {
    "KXHIGHTHOU":   {"lat": 29.7604, "lon": -95.3698, "market_type": "temp_above", "city": "Houston"},
    "KXHIGHCHI":    {"lat": 41.8781, "lon": -87.6298, "market_type": "temp_above", "city": "Chicago"},
    "KXHIGHTDC":    {"lat": 38.9072, "lon": -77.0369, "market_type": "temp_above", "city": "Washington DC"},
    "KXHIGHTEMPDEN":{"lat": 39.7392, "lon": -104.9903, "market_type": "temp_above", "city": "Denver"},
    "KXLOWTNYC":    {"lat": 40.7128, "lon": -74.0060, "market_type": "temp_below", "city": "NYC"},
    "KXLOWDEN":     {"lat": 39.7392, "lon": -104.9903, "market_type": "temp_below", "city": "Denver"},
}

def log_decision(data):
    data["timestamp"] = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + chr(10))

def extract_threshold(ticker):
    try:
        parts = ticker.split("-")
        for part in parts:
            if part.startswith("T"):
                return float(part[1:])
        return None
    except:
        return None

def calculate_bet_size(edge, true_prob):
    kelly = (edge / (1 - true_prob)) * MAX_KELLY
    bet = min(kelly * BANKROLL, BANKROLL * MAX_KELLY)
    return max(round(bet, 2), 0)

def run_bot():
    print("Fetching live Bitcoin markets...")
    markets = get_markets(100, series_ticker="KXBTCD")
    print(f"Found {len(markets)} markets")

    for market in markets:
        ticker = market.get("ticker")
        title = market.get("title", "")
        yes_price = float(market.get("yes_ask_dollars", 0))
        no_price = float(market.get("no_ask_dollars", 0))
        volume = float(market.get("volume_24h_fp", 0))
        if not ticker or not yes_price or volume == 0:
            continue
        if yes_price < 0.15 or yes_price > 0.85:
            continue

        threshold = extract_threshold(ticker)
        if threshold is None:
            continue

        result = analyze_crypto_market("bitcoin", threshold, 0.5)
        if result is None:
            continue

        recommendation = result.get("recommendation", "")
        true_prob = result.get("true_prob", 0)
        market_odds = no_price if recommendation == "NO" else yes_price
        edge = true_prob - market_odds

        if edge >= EDGE_THRESHOLD:
            bet_size = calculate_bet_size(abs(edge), true_prob)
            price_cents = int(market_odds * 100)
            print(f"EDGE FOUND: {ticker} | {recommendation} | edge: {edge:.2%} | bet: ${bet_size}")
            log_decision({"ticker": ticker, "title": title, "recommendation": recommendation, "edge": edge, "true_prob": true_prob, "market_odds": market_odds, "bet_size": bet_size, "action": "DRY_RUN" if DRY_RUN else "ORDER_PLACED"})
            if DRY_RUN:
                print(f"DRY RUN - would place order: {ticker} {recommendation} @ {price_cents}c")
            else:
                side = "yes" if recommendation == "YES" else "no"
                place_order(ticker, side, 1, price_cents)
        else:
            print(f"No edge: {ticker} | edge: {edge:.2%}")
            log_decision({"ticker": ticker, "title": title, "recommendation": "PASS", "edge": edge, "true_prob": true_prob, "market_odds": market_odds, "bet_size": 0, "action": "NO_EDGE"})

    # --- WEATHER MARKETS ---
    print("\nFetching live weather markets...")
    for series_ticker, config in WEATHER_MARKETS.items():
        markets = get_markets(20, series_ticker=series_ticker)
        for market in markets:
            ticker = market.get("ticker")
            title = market.get("title", "")
            yes_price = float(market.get("yes_ask_dollars", 0))
            no_price = float(market.get("no_ask_dollars", 0))
            volume = float(market.get("volume_24h_fp", 0))
            if not ticker or not yes_price or volume == 0:
                continue
            if yes_price < 0.15 or yes_price > 0.85:
                continue

            threshold = extract_threshold(ticker)
            if threshold is None:
                continue

            result = analyze_weather_market(config["lat"], config["lon"], config["market_type"], threshold, 0.5)
            if result is None:
                continue

            recommendation = result.get("recommendation", "")
            true_prob = result.get("true_prob", 0)
            market_odds = no_price if recommendation == "NO" else yes_price
            edge = true_prob - market_odds

            if edge >= EDGE_THRESHOLD:
                bet_size = calculate_bet_size(abs(edge), true_prob)
                price_cents = int(market_odds * 100)
                print(f"EDGE FOUND: {ticker} | {recommendation} | edge: {edge:.2%} | bet: ${bet_size}")
                log_decision({"ticker": ticker, "title": title, "recommendation": recommendation, "edge": edge, "true_prob": true_prob, "market_odds": market_odds, "bet_size": bet_size, "action": "DRY_RUN" if DRY_RUN else "ORDER_PLACED"})
                if DRY_RUN:
                    print(f"DRY RUN - would place order: {ticker} {recommendation} @ {price_cents}c")
                else:
                    side = "yes" if recommendation == "YES" else "no"
                    place_order(ticker, side, 1, price_cents)
            else:
                print(f"No edge: {ticker} | edge: {edge:.2%}")

if __name__ == "__main__":
    run_bot()
