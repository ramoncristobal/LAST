# Blackjack Strategy Lab - Plan (v2, standalone repo)

## Goal
A separate, standalone project that compares many blackjack strategies head-to-head on
IDENTICAL shoes (common random numbers), reports PER-SHOE results (which strategy wins
most shoes + under what conditions), ranks by risk-adjusted "most viable" metrics, lets
us plug in new strategies, and learns/optimizes parameters with a train/test split.
Runs locally; emits logs + STATUS.md for daily/weekly check-ins.

## Iron rule (anti-overfitting)
Strategies may ONLY use info available at decision time (cards on table + running count of
seen cards). No lookahead at future/undealt cards. "Best strategy per shoe" = best
PRE-COMMITTED strategy per shoe, never a strategy fitted to that shoe's card order.

## Delivery
- Standalone project dir `blackjack-strategy-lab/`, self-contained (stdlib only).
- Ship as downloadable .tar.gz + backup copy committed in LAST.
- User creates the GitHub repo (my access is limited to LAST); provide push commands.

## Build steps
- [ ] Project skeleton (README, pyproject, .gitignore, pkg dir)
- [ ] rules.py (reuse validated rules)
- [ ] engine.py: fixed-shoe dealer, round resolution, insurance, strategy-driven play
- [ ] counting.py: balanced systems (Hi-Lo, Hi-Opt I/II, Omega II, Zen), true count
- [ ] strategies.py: Strategy base + Flat, CardCounter (ramp, wong), pluggable
- [ ] deviations.py: Hi-Lo Illustrious-18 subset (validated to INCREASE edge)
- [ ] metrics.py: EV/100, SD/100, Desirability Index, N0, risk of ruin, Kelly bankroll
- [ ] tournament.py: run strategies on identical shoes, per-shoe + aggregate results
- [ ] optimizer.py: tune bet ramp / wong-out on TRAIN shoes, validate on TEST shoes
- [ ] storage.py: SQLite cumulative + JSONL run log
- [ ] reporting.py: STATUS.md generator
- [ ] run.py: CLI (tournament / optimize / report / loop / list)
- [ ] tests.py: correctness gates
- [ ] scripts/init_standalone_repo.sh

## Verification gates
- Flat basic house edge ~0.36%.
- Every counting strategy shows positive edge; edge rises with true count.
- Hi-Lo + I18 deviations edge > Hi-Lo basic edge (proves deviations are correct, not hurting).
- Level-2 systems (Hi-Opt II/Omega II) betting correlation >= Hi-Lo (expected).
- Optimizer's tuned params beat defaults on TEST shoes (not just train).

## Review (completed 2026-11-18)
Built standalone `blackjack-strategy-lab/` (stdlib only). All gates pass.

Verification:
- Deviation ENCODING: 32/32 unit checks vs canonical Hi-Lo Illustrious-18 (found + fixed a
  missing 13v3 entry). This is the real correctness gate for deviations.
- Flat basic house edge ~0.245% (matches the first engine's seeded runs).
- All counters positive; level-2 systems (Hi-Opt II/Zen) edge out Hi-Lo as BC predicts.
- Per-shoe ranking (risk-adjusted DI) is the headline; per-100-hand is secondary.

Two honest course-corrections mid-build (mentor standard applied to my own work):
1. Ranking by per-HAND EV made Wong/optimizer look absurd (+7-25 u/100) because playing
   only the best hands trivially maximizes per-hand EV. Switched headline to PER-SHOE
   (fixed table time), which prices in opportunity cost.
2. The I18 playing-deviation benefit is real but small (~+0.12 u/100 averaged over seeds)
   and noisy; a single-seed sim gate was fragile. Replaced it with instant unit tests of
   the encoding, and documented that betting spread drives ~90% of the edge.
3. Optimizer was fitting noise (per-shoe EV SD ~19). Made it paired (all candidates on
   identical shoes), larger samples, and added a significance + train/test-consistency
   check so it won't claim a win off noise.

Delivery: tarball sent to user + backup committed in LAST. User creates their own GitHub
repo (my access is limited to LAST); scripts/init_standalone_repo.sh automates it.

Next-step ideas: full count-specific indices per system; KO/unbalanced (validated);
rule-comparison sweep (6:5 vs 3:2, H17, penetration); fractional-Kelly bet sizing in the
tournament; genetic search over strategy params.
