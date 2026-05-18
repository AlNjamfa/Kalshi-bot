import os
import requests
from dotenv import load_dotenv

# load_dotenv() reads your .env file and loads every line
# into Python's environment variables so os.getenv() can find them
# Without this line, os.getenv() would return None for everything
load_dotenv()

def test_coingecko():
    # No API key needed for basic price endpoint
    # This tests that requests library works and internet is reachable
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
    r = requests.get(url, params=params)
    print("✅ CoinGecko:", r.json())

def test_odds():
    # os.getenv reads the key from your .env file
    key = os.getenv("THE_ODDS_API_KEY")
    url = "https://api.the-odds-api.com/v4/sports"
    r = requests.get(url, params={"apiKey": key})
    print(f"✅ Odds API: {len(r.json())} sports available")

def test_weather():
    key = os.getenv("OPENWEATHER_API_KEY")
    url = "https://api.openweathermap.org/data/2.5/weather"
    r = requests.get(url, params={
        "q": "New York",
        "appid": key,
        "units": "imperial"  # imperial = Fahrenheit, metric = Celsius
    })
    temp = r.json().get("main", {}).get("temp")
    print(f"✅ Weather: {temp}°F in NYC")

def test_news():
    key = os.getenv("NEWS_API_KEY")
    url = "https://newsapi.org/v2/everything"
    r = requests.get(url, params={
        "q": "bitcoin",
        "apiKey": key,
        "pageSize": 3  # only get 3 articles, we just want to confirm it works
    })
    articles = r.json().get("articles", [])
    print(f"✅ News: {len(articles)} articles found for 'bitcoin'")

def test_noaa():
    # NOAA needs no API key but requires a User-Agent header
    # Without it NOAA will throttle or block your requests
    r = requests.get(
        "https://api.weather.gov/points/40.7128,-74.0060",
        headers={"User-Agent": "kalshi-bot/1.0 (test)"}
    )
    props = r.json()["properties"]
    print(f"✅ NOAA: NYC grid = {props['gridId']} {props['gridX']},{props['gridY']}")

if __name__ == "__main__":
    # __name__ == "__main__" means "only run this block if this file
    # is run directly, not if it's imported by another file"
    # This is a Python standard pattern you'll see in every project
    print("Testing all APIs...\n")
    test_coingecko()
    test_odds()
    test_weather()
    test_news()
    test_noaa()
    print("\nDone.")