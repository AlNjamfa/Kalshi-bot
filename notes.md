# My Dev Notes

## American Odds Cheat Sheet

### Negative odds = FAVORITE (likely to win, low payout)
Example: -180 means bet $180 to WIN $100
Formula: |odds| / (|odds| + 100)
-180 → 180 / (180 + 100) = 180 / 280 = 64.3% probability

### Positive odds = UNDERDOG (unlikely to win, high payout)
Example: +155 means bet $100 to WIN $155
Formula: 100 / (odds + 100)
+155 → 100 / (155 + 100) = 100 / 255 = 39.2% probability

## No-Vig Formula
raw_prob_A + raw_prob_B = more than 100% (the extra % is the vig)
no_vig_prob = raw_prob / (raw_prob_A + raw_prob_B)

## API Call Pattern
1. url = endpoint address
2. params = what you're asking for
3. response = requests.get(url, params=params)
4. return response.json()

## Key Concepts
- Constant = ALL_CAPS, never changes
- f-string = f"text {variable} text"
- list comprehension = [item[1] for item in list]
- ternary = value_if_true if condition else value_if_false
- edge = true_prob - market_odds

## URL Construction Pattern
Base URL = where (never changes, stored as constant)
Endpoint = what (changes based on what data you need)
f-string = connects them dynamically

Example:
ODDS_BASE_URL = "https://api.the-odds-api.com/v4"
url = f"{ODDS_BASE_URL}/sports/{sport}/odds"
→ "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

Memory hook: "Base URL is where, endpoint is what, f-string connects them

## Edge Formula
edge = true_prob - market_odds

edge > 0  → Kalshi UNDERPRICING → bet YES (Kalshi is cheap)
edge < 0  → Kalshi OVERPRICING  → bet NO or pass (Kalshi is expensive)
edge = 0  → perfectly priced    → no edge, pass

Example:
true_prob   = 0.621  (Pinnacle sharp line, vig removed)
market_odds = 0.52   (what Kalshi is selling it for)
edge        = 0.101  = +10.1% edge → bet YES

## When To Bet
Only bet when |edge| > 0.05 (5% minimum edge)
Below 5% edge gets eaten by variance and fees

## The Full Signal Chain
Pinnacle American odds (-180)
→ convert_american_to_prob() → 0.643 raw prob
→ remove_vig()               → 0.621 true prob
→ subtract Kalshi price      → edge
→ edge > 0.05                → YES
→ edge < -0.05               → NO
→ |edge| < 0.05              → PASS

## Functions — Reference vs Call
function_name    → just a reference, does nothing
function_name()  → executes the function

## Substitution / Method Chaining
Like algebra - substitute a variable back into the equation:

# Two lines
props = data["properties"]
periods = props["periods"]

# One line (substituted)
periods = data["properties"]["periods"]

Rule: collapse when readable, keep separate when used multiple times
or when the combined line gets too long

## When to use one line vs two lines
- Need variable multiple times → separate lines
- Only need it once → can combine
- Line too long to read → separate lines
- Readability always wins over cleverness