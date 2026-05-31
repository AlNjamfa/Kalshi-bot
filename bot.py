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
BANKROLL = float(os.getenv("BANKROLL", 500))
MAX_KELLY = float(os.getenv("MAX_KELLY_FRACTION", 0.25))

def calculate_bet_size(edge, true_prob):
    kelly = (edge / (1 - true_prob)) * MAX_KELLY
    bet = min(kelly * BANKROLL, BANKROLL * MAX_KELLY)
    return max(round(bet, 2), 0)

def run_bot():
    print("Fetching live markets...")
    markets = get_markets(100)
    print(f"Found {len(markets)} markets")

    for market in markets:
        ticker = market.get("ticker")
        title = market.get("title", "")
        yes_price = market.get("yes_ask_dollars", 0)
        if not ticker or not yes_price:
            continue

        market_odds = float(yes_price)
        if "bitcoin" in title.lower() or "btc" in title.lower():
            result = analyze_crypto_market("bitcoin", 0, market_odds)
        elif "ethereum" in title.lower() or "eth" in title.lower():
            result = analyze_crypto_market("ethereum", 0, market_odds)
        elif any(team in title for team in ["Baltimore", "Atlanta", "Boston", "New York", "Los Angeles"]):
            try:
                result = get_sports_edge("baseball_mlb", title.split(",")[0].replace("yes ", "").strip(), market_odds)
            except:
                result = None
    
        if result is None:
            continue
        edge = result.get("edge", 0)
        true_prob = result.get("true_prob", 0)
        recommendation = result.get("recommendation", "")

        if edge >= EDGE_THRESHOLD:
            bet_size = calculate_bet_size(edge, true_prob)
            price_cents = int(market_odds * 100)
            print(f"EDGE FOUND: {ticker} | {recommendation} | edge: {edge:.2%} | bet: ${bet_size}")
            place_order(ticker, "yes", 1, price_cents)

        else:
            print(f"No edge: {ticker} | edge: {edge:.2%}")

if __name__ == "__main__":
    run_bot()