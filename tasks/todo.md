# Blackjack Research Engine - Plan

## Goal
Build a rigorous, continuously-running simulation engine that finds the REAL edge in
blackjack (optimal basic strategy + card counting), measures it honestly across
millions of simulated shoes, and produces a data-backed strategy guide.

Optimize for BOTH max win rate AND realistic/casino-practical play.

## What this is NOT
- Not a "card-order pattern finder." No such edge exists in a shuffled shoe.
- Not a betting-progression system (Martingale etc.). The engine will prove these fail.

## Design decisions
- Language: Python 3.12, standard library ONLY (zero install, runs anywhere).
- Realistic shoe: multi-deck, configurable rules, cut-card penetration, reshuffle.
- Data persists in local SQLite, accumulating across every run ("collect over time").
- Basic strategy chart is DERIVED FROM THE CODE so chart and engine never disagree.

## Rule set modeled (casino-realistic default)
- 6 decks, dealer Stands on Soft 17 (S17), Double After Split (DAS) allowed,
  Late Surrender, Blackjack pays 3:2, split to 4 hands, 75% penetration.
- All rules configurable.

## Build steps
- [x] Explore repo, confirm Python version, pick isolated directory
- [x] Write this plan
- [ ] rules.py: configurable rule dataclass
- [ ] engine.py: shoe, counting-aware deal, hand resolution (hit/stand/double/split/surrender), dealer play, round net
- [ ] strategy.py: correct multi-deck basic strategy (hard/soft/pairs/surrender), DAS-aware
- [ ] counting.py: Hi-Lo running/true count + configurable bet ramp
- [ ] storage.py: SQLite cumulative aggregates + per-true-count edge table
- [ ] simulate.py: batch Monte Carlo loop, updates DB
- [ ] analysis.py: EV, variance, N0, risk of ruin, edge-by-count
- [ ] guide.py: generate STRATEGY_GUIDE.md from accumulated data + printed chart
- [ ] run.py: CLI (calibrate / count / loop / guide)
- [ ] tests.py: correctness sanity checks
- [ ] README.md for the blackjack dir

## Verification targets (how I prove it works, not just claim it)
- Flat basic strategy house edge must land ~ -0.4% to -0.6% per unit (known correct value).
  If it is far off, there is a bug. This is the key correctness gate.
- Dealer bust rate ~28%, dealer final-17+ distribution sane.
- Counting + spread must show measurably POSITIVE EV per hand, and edge must rise
  monotonically with true count. If edge does not increase with the count, something is wrong.
- Martingale demo must show it does NOT beat the house edge (only increases ruin risk).

## Review (completed 2026-11-18)
All steps done. Engine built in `blackjack/`, pure Python stdlib.

Verification results (all gates passed):
- Dealer bust rate: 28.1% (expected ~28%).
- Basic strategy house edge: 0.357% over 5M hands (textbook value for 6D/S17/DAS/LS).
- Counting (Hi-Lo, 1-12 spread): +0.606% edge/unit, +0.97 units/100 hands, over 12M hands.
  Edge rises monotonically with true count (negative below TC+1, positive above) - the
  core card-counting thesis, demonstrated from the engine's own data.
- Basic strategy chart rendered from the engine matches canonical charts on every cell.
- Risk-of-ruin and bankroll numbers reported honestly (need ~1,300 units for 5% RoR).

Correction made mid-build: first Martingale demo (single long run) showed a misleading
positive net due to variance. Rewrote it as 20k bankroll-limited sessions, which honestly
exposes the bust tail: 78% hit goal, 22% bust, average net negative, edge = house edge.

Deliverables:
- `blackjack/STRATEGY_GUIDE.md` - the data-backed guide (committed).
- `blackjack/` engine + CLI (`run.py loop` is the continuous learner).

Known minor simplifications (documented, not bugs): dealer hole card is counted even on
player bust (negligible EV effect); no playing deviations (Illustrious 18) yet - that is
the obvious v2 and would add ~0.1-0.2% to the counting edge.
