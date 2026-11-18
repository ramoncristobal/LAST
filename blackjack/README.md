# Blackjack Research Engine

A rigorous Monte Carlo engine that finds and measures the **real** edge in blackjack:
optimal basic strategy and card counting. It simulates millions of realistic casino
shoes (multi-deck, cut-card penetration, reshuffle), accumulates data over time in a
local database, and generates a data-backed strategy guide.

Pure Python 3, standard library only. No dependencies, runs anywhere.

## The premise, stated honestly

There is **no winning pattern hidden in the order of a shuffled shoe**. Running
simulations to "discover" one is chasing something that does not exist. What this engine
proves and optimizes instead are the two edges that are mathematically real:

1. **Basic strategy** - the optimal play for every hand. Shrinks the house edge to ~0.36%.
2. **Card counting (Hi-Lo)** - tracks the *composition* of the remaining shoe and bets
   more when the odds genuinely favor the player. A small, real, high-variance edge.

Betting systems like Martingale do **not** work. The engine demonstrates this directly.

## Quick start

```bash
cd blackjack

python tests.py                   # prove the engine is correct
python run.py calibrate 5000000   # measure the basic-strategy house edge
python run.py count 10000000      # measure the counting edge (fills the count table)
python run.py guide               # write STRATEGY_GUIDE.md from all data so far
python run.py martingale          # show a betting system fails
python run.py loop                # run forever, accumulating data (Ctrl+C to stop)
```

Open **[STRATEGY_GUIDE.md](STRATEGY_GUIDE.md)** for the generated chart and measured edges.

## "Keep it running and learning"

`python run.py loop` runs 1,000,000-hand batches continuously and persists cumulative
stats to `data/results.db` after every batch, so the estimates get tighter the longer it
runs. All runs add to the same database. On Ctrl+C it regenerates the guide.

This directory is a cloud container that gets reclaimed when idle, so for truly 24/7
operation, clone the repo to your own always-on machine and run `python run.py loop`
there. The database and guide are the durable output.

## How it is structured

| File | Role |
| --- | --- |
| `rules.py` | Configurable rule set (decks, S17/H17, DAS, surrender, payout, penetration) |
| `engine.py` | Shoe, Hi-Lo-aware dealing, full hand resolution, dealer play |
| `strategy.py` | Correct multi-deck basic strategy (hard/soft/pairs/surrender) |
| `counting.py` | Hi-Lo true count + bet ramp |
| `simulate.py` | Monte Carlo batch runner |
| `analysis.py` | EV, variance, N0, risk of ruin |
| `storage.py` | SQLite cumulative aggregates + per-true-count edge |
| `guide.py` | Generates STRATEGY_GUIDE.md from code + data |
| `run.py` | CLI |
| `tests.py` | Correctness gates |

## Correctness

The chart in the guide is rendered by calling the same decision function the engine
plays with, so the printed advice can never drift from the simulated results. `tests.py`
gates on known-correct values: dealer bust rate ~28%, basic-strategy house edge
~0.3-0.6%, and a counting edge that is positive overall and rises with the true count.

## This is not financial advice

Card counting is legal but casinos will bar you for it, the edge is thin, variance is
brutal, and it requires a large bankroll and discipline. The guide reports the sobering
numbers (risk of ruin, bankroll needed, hourly swing) honestly. Treat this as the
mathematics of advantage play, not a money-making scheme.
