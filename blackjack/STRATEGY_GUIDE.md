# Blackjack Strategy Guide (data-backed)

> Generated from millions of simulated shoes by this engine. Every number below is measured, not quoted.

**Rules modeled:** 6 decks · dealer stands on soft 17 · DAS · late surrender · blackjack pays 1.5:1 · 75% penetration

## The honest bottom line

- **Basic strategy alone does not win.** It only shrinks the house edge to a small loss. You cannot bet your way out of a negative edge.
- **Card counting is the only legal, proven edge**, and it is small, high-variance, and slow. It tracks the *composition* of the remaining shoe (not the order of cards), bets big when few high cards are gone.
- **Betting systems (Martingale, etc.) do nothing** to the edge. Run `python run.py martingale` to watch one fail.

## 1. Basic strategy (measured)

- Hands simulated: **5,000,000**
- House edge: **0.357%** per hand (you lose about this fraction of each bet on average)
- Std dev per hand: **1.14 units** (this is why short-term swings feel random)

## 2. The optimal basic strategy chart

Memorize this. It is derived directly from the engine, so it matches exactly how the winning simulations played.

### Hard totals (your two cards, no ace / no pair)

| Hand |   2 |   3 |   4 |   5 |   6 |   7 |   8 |   9 |  10 |   A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **5** |   H |   H |   H |   H |   H |   H |   H |   H |   H |   H |
| **6** |   H |   H |   H |   H |   H |   H |   H |   H |   H |   H |
| **7** |   H |   H |   H |   H |   H |   H |   H |   H |   H |   H |
| **8** |   H |   H |   H |   H |   H |   H |   H |   H |   H |   H |
| **9** |   H |   D |   D |   D |   D |   H |   H |   H |   H |   H |
| **10** |   D |   D |   D |   D |   D |   D |   D |   D |   H |   H |
| **11** |   D |   D |   D |   D |   D |   D |   D |   D |   D |   H |
| **12** |   H |   H |   S |   S |   S |   H |   H |   H |   H |   H |
| **13** |   S |   S |   S |   S |   S |   H |   H |   H |   H |   H |
| **14** |   S |   S |   S |   S |   S |   H |   H |   H |   H |   H |
| **15** |   S |   S |   S |   S |   S |   H |   H |   H | SUR |   H |
| **16** |   S |   S |   S |   S |   S |   H |   H | SUR | SUR | SUR |
| **17** |   S |   S |   S |   S |   S |   S |   S |   S |   S |   S |
| **18** |   S |   S |   S |   S |   S |   S |   S |   S |   S |   S |
| **19** |   S |   S |   S |   S |   S |   S |   S |   S |   S |   S |

### Soft totals (one ace counted as 11)

| Hand |   2 |   3 |   4 |   5 |   6 |   7 |   8 |   9 |  10 |   A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A,2** |   H |   H |   H |   D |   D |   H |   H |   H |   H |   H |
| **A,3** |   H |   H |   H |   D |   D |   H |   H |   H |   H |   H |
| **A,4** |   H |   H |   D |   D |   D |   H |   H |   H |   H |   H |
| **A,5** |   H |   H |   D |   D |   D |   H |   H |   H |   H |   H |
| **A,6** |   H |   D |   D |   D |   D |   H |   H |   H |   H |   H |
| **A,7** |  Ds |  Ds |  Ds |  Ds |  Ds |   S |   S |   H |   H |   H |
| **A,8** |   S |   S |   S |   S |   S |   S |   S |   S |   S |   S |
| **A,9** |   S |   S |   S |   S |   S |   S |   S |   S |   S |   S |

### Pairs

| Pair |   2 |   3 |   4 |   5 |   6 |   7 |   8 |   9 |  10 |   A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **2,2** |   P |   P |   P |   P |   P |   P |   H |   H |   H |   H |
| **3,3** |   P |   P |   P |   P |   P |   P |   H |   H |   H |   H |
| **4,4** |   H |   H |   H |   P |   P |   H |   H |   H |   H |   H |
| **5,5** |   D |   D |   D |   D |   D |   D |   D |   D |   H |   H |
| **6,6** |   P |   P |   P |   P |   P |   H |   H |   H |   H |   H |
| **7,7** |   P |   P |   P |   P |   P |   P |   H |   H |   H |   H |
| **8,8** |   P |   P |   P |   P |   P |   P |   P |   P |   P |   P |
| **9,9** |   P |   P |   P |   P |   P |   S |   P |   P |   S |   S |
| **T,T** |   S |   S |   S |   S |   S |   S |   S |   S |   S |   S |
| **A,A** |   P |   P |   P |   P |   P |   P |   P |   P |   P |   P |

**Legend:** H = hit · S = stand · D = double (hit if not allowed) · Ds = double (stand if not allowed) · P = split · SUR = surrender (hit if not allowed)

## 3. Card counting (Hi-Lo) - the real edge, measured

- Hands simulated with a 1-12 bet spread: **12,000,000**
- Overall edge: **+0.606%** per unit wagered
- Win rate: **+0.972 units per 100 hands**
- Std dev per hand: **2.90 units**
- N0 (hands until expected win = one std dev): **88,818** - this is how long variance can hide your edge.

### Edge by true count

The whole game is here: raise your bet as this rises.

| True count | Player edge | Share of hands | What to do |
| --- | --- | --- | --- |
| -5 | -3.51% | 4.8% | min bet (or leave the table) |
| -4 | -2.19% | 3.9% | min bet (or leave the table) |
| -3 | -1.90% | 6.8% | min bet (or leave the table) |
| -2 | -1.21% | 12.4% | min bet (or leave the table) |
| -1 | -0.61% | 19.0% | min bet (or leave the table) |
| +0 | -0.12% | 26.6% | min bet (or leave the table) |
| +1 | +0.60% | 11.7% | min bet |
| +2 | +1.11% | 6.4% | bet ~2 units |
| +3 | +1.61% | 3.7% | bet ~4 units |
| +4 | +2.05% | 2.1% | bet ~8 units |
| +5 | +2.69% | 1.2% | bet ~12 units |
| +6 | +2.43% | 0.7% | bet ~12 units |
| +7 | +3.25% | 0.4% | bet ~12 units |
| +8 | +1.65% | 0.2% | bet ~12 units |
| +9 | +4.06% | 0.1% | bet ~12 units |
| +10 | +5.83% | 0.1% | bet ~12 units |

### Recommended bet spread

| True count | Units to bet |
| --- | --- |
| 0 or less | 1 |
| 1 | 1 |
| 2 | 2 |
| 3 | 4 |
| 4 | 8 |
| 5 | 12 |

## 4. Bankroll and risk of ruin (measured)

Risk of ruin = chance you lose your whole bankroll before your edge pays off. Units are multiples of your base bet.

| Bankroll (units) | Risk of ruin |
| --- | --- |
| 100 | 79.3% |
| 200 | 62.9% |
| 400 | 39.6% |
| 800 | 15.7% |
| 1600 | 2.5% |

- For a **5% risk of ruin** you need about **1,292 units**.
- For a **1% risk of ruin** you need about **1,987 units**.

## 5. What this means in real money

Example: base unit = $25, ~100 hands/hour.

- Expected win: **$24.29 per hour** on average.
- Hourly swing (1 std dev): **±$724** - so a losing night is completely normal even though you have the edge.
- Bankroll for 5% ruin at this unit: **$32,312**.

> Reality check: the edge is real but thin. This is a grind requiring discipline, a big bankroll, and tolerance for long losing stretches. Casinos also bar counters. Treat this as the math of advantage play, not a get-rich scheme.

## How to keep it running and learning

```
python run.py calibrate 5000000   # measure basic-strategy edge
python run.py count 10000000      # measure counting edge, fills count table
python run.py loop                # run forever, accumulating data (Ctrl+C to stop)
python run.py guide               # regenerate this guide from all data so far
python run.py martingale          # prove a betting system fails
```

All data accumulates in `data/results.db`. The more you run, the tighter these numbers get. Run it on your own always-on machine for continuous learning.
