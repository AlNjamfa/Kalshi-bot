import os
import json
from kalshi.markets import get_markets
from kalshi.orders import place_order
from signals.crypto import analyze_crypto_market
from signals.odds import get_sports_edge
from signals.weather import analyze_weather_market
from dotenv import load_dotenv
load_dotenv()

EDGE_THRESHOLD = 0.05
DRY_RUN = True
BANKROLL = float(os.getenv("BANKROLL", 500))
MAX_KELLY = float(os.getenv("MAX_KELLY_FRACTION", 0.25))

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
        yes_price = market.get("yes_ask_dollars", 0)
        if not ticker or not yes_price:
            continue

        market_odds = float(yes_price)
        threshold = extract_threshold(ticker)
        if threshold is None:
            continue

        result = analyze_crypto_market("bitcoin", threshold, market_odds)

        if result is None:
            continue
        edge = result.get("edge", 0)
        true_prob = result.get("true_prob", 0)
        recommendation = result.get("recommendation", "")

        if abs(edge) >= EDGE_THRESHOLD:
            bet_size = calculate_bet_size(abs(edge), true_prob)
            price_cents = int(market_odds * 100)
            print(f"EDGE FOUND: {ticker} | {recommendation} | edge: {edge:.2%} | bet: ")
            if DRY_RUN:
                print(f"DRY RUN - would place order: {ticker} {recommendation} @ {price_cents}c")
            else:
                side = "yes" if recommendation == "YES" else "no"
                place_order(ticker, side, 1, price_cents)
        else:
            print(f"No edge: {ticker} | edge: {edge:.2%}")

if __name__ == "__main__":
    run_bot()
