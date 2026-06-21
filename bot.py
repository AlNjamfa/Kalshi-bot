import os
import json
import requests
from datetime import datetime
from kalshi.markets import get_markets
from kalshi.orders import place_order
from signals.crypto import analyze_crypto_market
from signals.weather import analyze_weather_market
from signals.odds import get_sports_edge
from dotenv import load_dotenv

load_dotenv()

EDGE_THRESHOLD = 0.05
DRY_RUN = True
BANKROLL = float(os.getenv("BANKROLL", 500))
MAX_KELLY = float(os.getenv("MAX_KELLY_FRACTION", 0.25))
LOG_FILE = "logs/trades.jsonl"
MIN_MARKET_ODDS = 0.10

WEATHER_MARKETS = {
    "KXHIGHTHOU":    {"lat": 29.7604, "lon": -95.3698, "market_type": "temp_above", "city": "Houston"},
    "KXHIGHCHI":     {"lat": 41.8781, "lon": -87.6298, "market_type": "temp_above", "city": "Chicago"},
    "KXHIGHTDC":     {"lat": 38.9072, "lon": -77.0369, "market_type": "temp_above", "city": "Washington DC"},
    "KXHIGHTEMPDEN": {"lat": 39.7392, "lon": -104.9903, "market_type": "temp_above", "city": "Denver"},
    "KXLOWTNYC":     {"lat": 40.7128, "lon": -74.0060, "market_type": "temp_below", "city": "NYC"},
    "KXLOWDEN":      {"lat": 39.7392, "lon": -104.9903, "market_type": "temp_below", "city": "Denver"},
}

MLB_ABBREV = {
    "ARI": "Arizona Diamondbacks",
    "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CWS": "Chicago White Sox",
    "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians",
    "COL": "Colorado Rockies",
    "DET": "Detroit Tigers",
    "HOU": "Houston Astros",
    "KCR": "Kansas City Royals",
    "LAA": "Los Angeles Angels",
    "LAD": "Los Angeles Dodgers",
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SDP": "San Diego Padres",
    "SFG": "San Francisco Giants",
    "SEA": "Seattle Mariners",
    "STL": "St. Louis Cardinals",
    "TBR": "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSH": "Washington Nationals",
}

def log_decision(data):
    data["timestamp"] = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + chr(10))
    if data.get("action") == "DRY_RUN":
        signal = "Weather" if any(x in data["ticker"] for x in ["HIGH", "LOW"]) else "Sports" if "MLB" in data["ticker"] else "Crypto"
        date = datetime.utcnow().strftime("%b %d")
        print(f"\n  ── SHEETS ROW ──────────────────────────────────────")
        print(f"  Date:         {date}")
        print(f"  Ticker:       {data['ticker']}")
        print(f"  Name:         {data.get('human_name', data['ticker'])}")
        print(f"  Signal:       {signal}")
        print(f"  Prediction:   {data['recommendation']}")
        print(f"  Why:          {data.get('reason', 'N/A')}")
        print(f"  True Prob:    {data['true_prob']:.2f}")
        print(f"  Market Price: {data['market_odds']:.2f}")
        print(f"  Edge:         {data['edge']:.2%}")
        print(f"  Bet Size:     ${data['bet_size']}")
        print(f"  Resolved:     [fill in tonight]")
        print(f"  Correct:      [fill in tonight]")
        print(f"  ────────────────────────────────────────────────────")

def format_ticker(ticker):
    try:
        if "KXBTCD" in ticker:
            parts = ticker.split("-")
            date = parts[1][2:7]
            threshold = parts[2].replace("T", "$")
            return f"Bitcoin | {date} | Above {threshold}"
        elif "KXMLBGAME" in ticker:
            parts = ticker.split("-")
            date_time = parts[1][2:9]
            team_abbrev = parts[-1].upper()
            team_name = MLB_ABBREV.get(team_abbrev, team_abbrev)
            return f"MLB | {date_time} | {team_name}"
        else:
            parts = ticker.split("-")
            series = parts[0].replace("KXHIGH", "").replace("KXLOW", "LOW ")
            date = parts[1][2:7]
            threshold = parts[2].replace("T", "")
            direction = "Above" if "HIGH" in ticker else "Below"
            return f"{series} Temp | {date} | {direction} {threshold}°"
    except:
        return ticker

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
    print("=" * 60)
    print(f"BOT RUN — {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")
    print("=" * 60)

    # --- CRYPTO LOOP ---
    print("\nFetching live Bitcoin markets...")
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
        current_price = result.get("current_price", 0)
        market_odds = no_price if recommendation == "NO" else yes_price
        if market_odds < MIN_MARKET_ODDS:
            print(f"  SKIPPED (market too certain): {format_ticker(ticker)} | odds: {market_odds:.2f}")
            continue
        edge = true_prob - market_odds
        reason = f"BTC ${current_price:,.0f} vs threshold ${threshold:,.0f} — {'above' if current_price > threshold else 'below'}"
        human_name = format_ticker(ticker)
        if edge >= EDGE_THRESHOLD:
            bet_size = calculate_bet_size(abs(edge), true_prob)
            price_cents = int(market_odds * 100)
            print(f"\n  EDGE FOUND: {human_name}")
            print(f"  {recommendation} | Edge: {edge:.2%} | Bet: ${bet_size} | Price: {price_cents}c")
            log_decision({"ticker": ticker, "human_name": human_name, "title": title, "recommendation": recommendation, "edge": edge, "true_prob": true_prob, "market_odds": market_odds, "bet_size": bet_size, "reason": reason, "action": "DRY_RUN" if DRY_RUN else "ORDER_PLACED"})
            if DRY_RUN:
                print(f"  DRY RUN — would place: {ticker} {recommendation} @ {price_cents}c")
            else:
                side = "yes" if recommendation == "YES" else "no"
                place_order(ticker, side, 1, price_cents)
        else:
            print(f"  No edge: {human_name} | {edge:.2%}")
            log_decision({"ticker": ticker, "human_name": human_name, "title": title, "recommendation": "PASS", "edge": edge, "true_prob": true_prob, "market_odds": market_odds, "bet_size": 0, "reason": reason, "action": "NO_EDGE"})

    # --- WEATHER LOOP ---
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
            forecast_temp = result.get("forecast_temp", 0)
            market_odds = no_price if recommendation == "NO" else yes_price
            if market_odds < MIN_MARKET_ODDS:
                print(f"  SKIPPED (market too certain): {format_ticker(ticker)} | odds: {market_odds:.2f}")
                continue
            edge = true_prob - market_odds
            direction = "above" if config["market_type"] == "temp_above" else "below"
            reason = f"{config['city']} forecast {forecast_temp}° vs threshold {threshold}° — NOAA says {direction}"
            human_name = format_ticker(ticker)
            if edge >= EDGE_THRESHOLD:
                bet_size = calculate_bet_size(abs(edge), true_prob)
                price_cents = int(market_odds * 100)
                print(f"\n  EDGE FOUND: {human_name}")
                print(f"  {recommendation} | Edge: {edge:.2%} | Bet: ${bet_size} | Price: {price_cents}c")
                log_decision({"ticker": ticker, "human_name": human_name, "title": title, "recommendation": recommendation, "edge": edge, "true_prob": true_prob, "market_odds": market_odds, "bet_size": bet_size, "reason": reason, "action": "DRY_RUN" if DRY_RUN else "ORDER_PLACED"})
                if DRY_RUN:
                    print(f"  DRY RUN — would place: {ticker} {recommendation} @ {price_cents}c")
                else:
                    side = "yes" if recommendation == "YES" else "no"
                    place_order(ticker, side, 1, price_cents)
            else:
                print(f"  No edge: {human_name} | {edge:.2%}")

    # --- SPORTS LOOP ---
    print("\nFetching live sports markets...")
    sports_markets = get_markets(100, series_ticker="KXMLBGAME")
    print(f"Found {len(sports_markets)} MLB game markets")

    for market in sports_markets:
        ticker = market.get("ticker")
        title = market.get("title", "")
        yes_price = float(market.get("yes_ask_dollars", 0))
        no_price = float(market.get("no_ask_dollars", 0))
        volume = float(market.get("volume_24h_fp", 0))
        if not ticker or not yes_price or volume == 0:
            continue
        if yes_price < 0.15 or yes_price > 0.85:
            continue
        ticker_suffix = ticker.split("-")[-1].upper()
        matched_team = MLB_ABBREV.get(ticker_suffix)
        if matched_team is None:
            continue
        result = get_sports_edge("baseball", matched_team, yes_price)
        if result is None:
            continue
        recommendation = result.get("recommendation", "")
        true_prob = result.get("pinnacle_prob", 0)
        market_odds = no_price if recommendation == "NO" else yes_price
        if market_odds < MIN_MARKET_ODDS:
            print(f"  SKIPPED (market too certain): {format_ticker(ticker)} | odds: {market_odds:.2f}")
            continue
        edge = true_prob - market_odds
        reason = f"Pinnacle: {matched_team} {true_prob:.0%} vs Kalshi: {yes_price:.0%} — {edge:.1%} gap"
        human_name = format_ticker(ticker)
        if edge >= EDGE_THRESHOLD:
            bet_size = calculate_bet_size(abs(edge), true_prob)
            price_cents = int(market_odds * 100)
            print(f"\n  EDGE FOUND: {human_name}")
            print(f"  {recommendation} | Edge: {edge:.2%} | Bet: ${bet_size} | Price: {price_cents}c")
            log_decision({"ticker": ticker, "human_name": human_name, "title": title, "recommendation": recommendation, "edge": edge, "true_prob": true_prob, "market_odds": market_odds, "bet_size": bet_size, "reason": reason, "action": "DRY_RUN" if DRY_RUN else "ORDER_PLACED"})
            if DRY_RUN:
                print(f"  DRY RUN — would place: {ticker} {recommendation} @ {price_cents}c")
            else:
                side = "yes" if recommendation == "YES" else "no"
                place_order(ticker, side, 1, price_cents)
        else:
            print(f"  No edge: {human_name} | {edge:.2%}")

    print("\n" + "=" * 60)
    print("RUN COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    run_bot()
