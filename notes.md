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

## JWT - JSON Web Token
A string that proves you're authenticated without resending credentials.

Flow:
1. Send email + password → server verifies
2. Server returns JWT token
3. Include token in every subsequent request header
4. Token expires after set time → login again for new token

Analogy: wristband at an event. Show ID once, wear wristband all night.

Format: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

## Dictionary Access - [] vs .get()
data["key"]     → crashes if key missing (KeyError)
data.get("key") → returns None if key missing (safe)

Use [] when certain key exists
Use .get() when key might be missing

## String Slicing
string[:50]   → first 50 characters
string[50:]   → everything from position 50 onward
string[2:10]  → characters 2 through 9
string[-5:]   → last 5 characters

## API Debugging Process
1. Don't panic at errors
2. Print the raw response to see what server actually says
3. Check status codes:
   - 200 = success
   - 401 = unauthorized (wrong credentials OR wrong URL)
   - 404 = endpoint not found
   - 500 = server error on their end
4. Read the response body - it often tells you exactly what's wrong
5. Fix the root cause, not the symptom

## Why Constants Matter
Hardcoded URLs = change every function manually when API moves
Constants = change one line, everything updates

## APIs Change - Always Be Ready
- Companies rebrand
- Endpoints get deprecated  
- Versions get upgraded
- Always store URLs as constants
- Check API changelogs regularly

## Professional Debugging Framework

5 Levels:
1. Read full traceback bottom to top
2. Print everything before the crash line
3. Verify your inputs (None values cause silent failures)
4. Isolate the broken component and test alone
5. Read raw server responses before parsing

5 Questions Every Bug:
1. What line crashed?
2. What did it receive?
3. What did it expect?
4. Is the data what I think it is?
5. What does the server actually say?

Key debug lines for API calls:
print('Status:', r.status_code)
print('Response:', r.text[:500])
print('Input loaded:', bool(os.getenv('KEY_NAME')))

Misleading errors - the error you see isn't always
the real problem. Go one layer deeper.

## Common Status Codes to Memorize
200 → success, everything worked
201 → created, POST succeeded
400 → bad request, your data is malformed
401 → unauthorized, wrong credentials or wrong URL
403 → forbidden, you don't have permission
404 → not found, endpoint doesn't exist
429 → too many requests, slow down
500 → server error, their problem not yours
503 → service unavailable, server is down

## DRY vs Hardcoding
DRY = don't repeat the same value in multiple places
Hardcoding = embedding values directly in code instead of variables/constants

Both are problems. DRY violations make maintenance painful.
Hardcoding makes security and flexibility painful.

## Strings vs Variables in Dictionaries
{"key": variable}

"key"    → string literal, fixed text, the label
variable → refers to a variable's value, can change

Example:
limit = 100
{"limit": limit} → sends limit=100 to the API

"limit" is what Kalshi expects to see
limit is what you want to send

## Fixing Broken Indentation

When indentation gets messy in VSCode, never fix it line by line.
Use Python to rewrite the file programmatically instead.

**Step 1 — Write the file using Python:**
python3 -c "
lines = ['line1\n', 'line2\n']
with open('file.py', 'w') as f:
    f.writelines(lines)
print('written')
"

**Step 2 — Verify no syntax errors:**
python3 -c "import ast; ast.parse(open('file.py').read()); print('No syntax errors')"

**Step 3 — Run the file:**
python file.py

**Why this works:**
- Python writes each line exactly as specified
- No VSCode auto-indent interference
- ast.parse() catches all indentation errors before runtime
- Saves time vs debugging line by line

## series_ticker — Kalshi Market Filtering

The Kalshi API returns all market types by default, including parlay/multi-game
markets that have zero liquidity and no prices (yes_ask_dollars = 0.0).

Use series_ticker to filter to a specific group of related markets:
- series_ticker="KXBTCD" → Bitcoin price markets (have real prices)
- series_ticker="KXMVESPORTSMULTIGAMEEXTENDED" → parlay markets (no prices, useless)

Without this filter, edge calculations are meaningless because market_odds = 0.0
makes every signal look like it found massive edge.

Key lesson: always verify your input data before trusting your output.
Garbage in = garbage out.

## JSONL Logging Pattern
Append-only log format — one JSON object per line.
Use json.dumps(data) + chr(10) to write each line safely.
Open with "a" mode to append, never overwrite.
This is the industry standard for event logs.

## Session — June 16, 2026

### Price Filter (15–85 cent rule)
Markets below 15 cents or above 85 cents are already near-certain — the market has priced in reality. 
No edge exists there. Only trade markets in the 15–85 cent range where genuine uncertainty exists.
Added filter in bot.py to skip markets outside this range.

### Liquidity Filter
If volume_24h is 0, nobody is trading the market. The spread is fake and you can't get filled at a real price.
Added volume > 0 check to both loops in bot.py.

### Tomorrow's Markets > Today's Markets
Today's weather market is near-resolved by the time the bot runs — the temperature is already being observed.
Tomorrow's market has 24 hours of forecast uncertainty. That's where NOAA gives us a real signal edge.
Fixed weather.py to use periods[2] (tomorrow's daytime forecast) instead of periods[0] (today).

### The market_odds bug (yes/no price mapping)
bot.py was always reading yes_ask_dollars as market_odds, even when recommending NO.
A NO recommendation means you're buying the NO contract — so market_odds should be no_ask_dollars.
Fixed: market_odds = no_price if recommendation == "NO" else yes_price

### Edge formula reminder
edge = true_prob - market_odds
Positive edge = our signal thinks the event is MORE likely than the market does → trade it.
Negative edge = market knows more than us → skip it.

### Compounding principle
Fewer trades + higher quality = faster compounding.
Kelly sizing grows the bankroll proportionally to edge — never risks ruin.
The path to $400k from $10 is discipline, not volume.

## Session — June 17, 2026

### Sports loop wired into bot.py
odds.py was broken because it expected American odds but Pinnacle's API returns decimal odds (e.g. 3.93 not +393). Fixed by replacing convert_american_to_prob() with decimal_to_prob() which just does 1 / decimal_odds. Also added oddsFormat: "decimal" to the API params so Pinnacle returns the right format.

### SPORT_KEYS dict in odds.py
The Odds API uses specific sport key strings like "baseball_mlb" not just "baseball". Added a SPORT_KEYS lookup dict so get_sports_edge("baseball", team, odds) maps cleanly to the right endpoint.

### Team name matching in bot.py
Kalshi MLB tickers look like KXMLBGAME-26JUN201915NYMPHI-NYM. To match them to Pinnacle team names we extract the last 3 letters of each team abbreviation from the ticker and check if they appear in the full team name. Not perfect but works for most cases.

### Bot now has three loops
Crypto (KXBTCD) → weather (WEATHER_MARKETS dict) → sports (KXMLBGAME). All run in DRY_RUN mode. Sports is finding real edges on MLB games — 9.44% and 7.44% on NY Mets games today.

### forecast_temp key fix (weather.py)
weather.py was returning "temp" but bot.py was looking for "forecast_temp". Renamed the key in all three return blocks (rain, temp_above, temp_below) so the Why column in the SHEETS ROW prints the actual forecast temperature vs the threshold. Small key name mismatch — big diagnostic difference.

### Signal failure thresholds — defined June 19, 2026

These are the conditions under which I pause a signal and recalibrate
before placing any more trades. Non-negotiable.

Sports (Pinnacle vs Kalshi):
- Minimum sample before trusting: 30 resolved trades
- Pause if: win rate drops below 52% after 30 trades
- Pause if: 5 consecutive losses at any point
- Why 52%: below this the Pinnacle edge isn't overcoming Kalshi's
  pricing efficiently enough to be profitable after variance

Weather (NOAA tiers):
- Minimum sample before trusting: 30 resolved trades
- Pause if: win rate drops below 55% after 30 trades
- Pause if: same city is wrong 3 times in a row
- Why 55%: weather tiers are heuristic not backtested, need higher
  bar to confirm they're calibrated

Crypto (momentum tiers):
- Minimum sample before trusting: 50 resolved trades
- Pause if: win rate drops below 55% after 50 trades
- Currently producing no DRY_RUN trades — Bitcoin above all
  thresholds. Will revisit when crypto market conditions change.

What "pause" means:
- Set DRY_RUN = True for that signal only
- Do not remove until win rate recovers above threshold
  on next 20 trades
- Document the pause and reason in notes.md

