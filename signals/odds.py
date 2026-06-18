import os
import requests
from dotenv import load_dotenv

load_dotenv()

ODDS_API_KEY = os.getenv("THE_ODDS_API_KEY")
ODDS_BASE_URL = "https://api.the-odds-api.com/v4"

def decimal_to_prob(decimal_odds):
    return 1 / decimal_odds

def remove_vig(prob_a, prob_b):
    total = prob_a + prob_b
    return prob_a / total

SPORT_KEYS = {
    "baseball": "baseball_mlb",
    "soccer": "soccer_fifa_world_cup",
    "basketball": "basketball_nba",
}

def get_sports_edge(sport, team, market_odds):
    sport_key = SPORT_KEYS.get(sport, sport)
    url = f"{ODDS_BASE_URL}/sports/{sport_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",
        "bookmakers": "pinnacle",
        "oddsFormat": "decimal",
    }
    response = requests.get(url, params=params)
    data = response.json()
    for game in data:
        home = game.get("home_team", "")
        away = game.get("away_team", "")
        if team not in home and team not in away:
            continue
        for bookmaker in game.get("bookmakers", []):
            if bookmaker["key"] != "pinnacle":
                continue
            for market in bookmaker.get("markets", []):
                if market["key"] != "h2h":
                    continue
                outcomes = market["outcomes"]
                team_odds = None
                opponent_odds = None
                for outcome in outcomes:
                    if team in outcome["name"]:
                        team_odds = outcome["price"]
                    else:
                        opponent_odds = outcome["price"]
                if team_odds and opponent_odds:
                    team_prob = decimal_to_prob(team_odds)
                    opponent_prob = decimal_to_prob(opponent_odds)
                    true_prob = remove_vig(team_prob, opponent_prob)
                    edge = true_prob - market_odds
                    recommendation = "YES" if edge > 0.05 else "NO" if edge < -0.05 else "PASS"
                    return {
                        "team": team,
                        "sport": sport,
                        "pinnacle_prob": true_prob,
                        "market_odds": market_odds,
                        "edge": edge,
                        "recommendation": recommendation,
                    }
    return None
