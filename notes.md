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

## Abstraction
Hiding complexity behind a simple interface.
The caller doesn't need to know HOW it works, just WHAT it returns.

Example:
analyze_weather_market(lat, lon, market_type, threshold, market_odds)
    → internally calls get_grid() then get_forecast()
    → caller never sees those functions
    → caller just gets back a YES/NO/PASS signal

Real world analogy:
You press a light switch - you don't need to know about
wiring, circuits, or electricity. The complexity is hidden.

## Function Composition
One function calling other functions to build complex behavior
from simple pieces.

analyze_weather_market() → calls get_grid() → calls get_forecast()

Each function does ONE thing. Combined they do something powerful.

## Single Responsibility Principle
Every function should have ONE job:
get_grid()     → finds WHERE the weather data is
get_forecast() → gets WHAT the weather data is
analyze_weather_market() → scores the Kalshi edge

If a function is doing two things → split it into two functions.

## Substitution / Method Chaining
Like algebra - substitute a variable back in:
props = data["properties"]
periods = props["periods"]
# same as:
periods = data["properties"]["periods"]

## When To Collapse vs Separate Lines
Collapse when: only used once, still readable
Separate when: used multiple times, line too long, needs explanation

## Headers vs Params
params  → appended to URL as ?key=value (visible in URL)
headers → sent in request envelope (invisible, more secure)
Use headers for: authentication, content type, user identification
Use params for: filtering, pagination, query options

## Data Extraction Pattern
Drilling down from a full API response to one specific value.
Each step navigates one level deeper into nested data.

Example - extracting temperature from NOAA:
response.json()              → full Python dictionary
data["properties"]           → navigate into properties section  
data["properties"]["periods"]→ navigate into periods list
periods[0]                   → grab first (most current) period
today["temperature"]         → extract just the temperature number
temp = 76                    → clean integer ready to use

Rule: extract values you use multiple times into named variables
temp is cleaner than writing today["temperature"] everywhere

## Indexing
list[0]  → first item (Python starts at 0, not 1)
list[1]  → second item
list[-1] → last item

NOAA returns periods in chronological order:
periods[0] = most current period (This Afternoon/Tonight)
periods[1] = next period
periods[13] = 7 days from now

## Why Extract Into Variables
today["temperature"]  ← have to remember what this means
temp                  ← instantly readable, used multiple times

Same value, better readability.
Extraction also gives you a place to add comments if needed.

## Two Types of Decision Trees

Quantity-based (how much?):
if diff_pct >= 5:   → many possible values
elif diff_pct >= 2:
elif diff_pct >= 0:

Category-based (which type?):
if market_type == "rain":      → fixed set of options
elif market_type == "temp_above":
elif market_type == "temp_below":

Use quantity-based when the input is a number on a scale.
Use category-based when the input is one of a fixed set of options.

## Consistent Interface Pattern
Every signal function returns the same core fields:
- true_prob    → what we think the probability is
- market_odds  → what Kalshi is pricing it at
- edge         → the difference (our edge)
- recommendation → YES/NO/PASS

Plus context-specific fields (coin, team, temp, etc.)

This is API design — consistent outputs make code maintainable.
Any caller knows exactly what fields to expect regardless of
which signal function they call.

## Paper Trading Rule
Always test on demo environment first.
demo-api.kalshi.com = fake money, real market data
trading-api.kalshi.com = real money

Never go live until 2+ weeks of demo results confirm edge is real.

