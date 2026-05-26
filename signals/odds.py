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