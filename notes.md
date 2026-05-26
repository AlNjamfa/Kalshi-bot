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