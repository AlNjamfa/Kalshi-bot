import os
import requests
from dotenv import load_dotenv

load_dotenv()

ODDS_API_KEY = os.getenv("THE_ODDS_API_KEY")
ODDS_BASE_URL = "https://api.the-odds-api.com/v4"

def convert_american_to_prob(american_odds):
    if american_odds < 0:
        return abs(american_odds) / (abs(american_odds) + 100)
    else:
        return 100 / (american_odds + 100)

def remove_vig(prob_a, prob_b):
    total = prob_a + prob_b
    return prob_a / total

def get_sports_edge(sport, team, market_odds):
    url = f"{ODDS_BASE_URL}/sports/{sport}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",
        "bookmakers": "pinnacle"
    }
    response = requests.get(url, params=params)
    data = response.json()
    for game in data:
        if team in game["home_team"] or team in game["away_team"]:
            for bookmaker in game["bookmakers"]:
                if bookmaker["key"] == "pinnacle":
                    for market in bookmaker["markets"]:
                        if market["key"] == "h2h":
                            outcomes = market["outcomes"]
                            team_odds = None
                            opponent_odds = None
                            for outcome in outcomes:
                                if team in outcome["name"]:
                                    team_odds = outcome["price"]
                                else:
                                    opponent_odds = outcome["price"]
                            if team_odds and opponent_odds:
                                team_prob = convert_american_to_prob(team_odds)
                                opponent_prob = convert_american_to_prob(opponent_odds)
                                true_prob = remove_vig(team_prob, opponent_prob)
                                edge = true_prob - market_odds
                                recommendation = "YES" if edge > 0.05 else "NO" if edge < -0.05 else "PASS"
                                return {
                                    "team": team,
                                    "sport": sport,
                                    "pinnacle_prob": true_prob,
                                    "market_odds": market_odds,
                                    "edge": edge,
                                    "recommendation": recommendation
                                }
    return None
