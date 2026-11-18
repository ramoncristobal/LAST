# Blackjack Strategy Lab

A research engine that compares many blackjack strategies **head-to-head on identical
shoes**, reports **per-shoe** results (which strategy wins the most shoes, and under what
conditions), ranks them by a risk-adjusted "most viable" metric, lets you plug in new
strategy ideas, and **learns** by optimizing parameters with a train/test split.

It runs locally and accumulates data over time so the estimates tighten the longer you run
it. Pure Python 3, standard library only, no dependencies.

## The one rule that makes this honest

**A strategy may only use information available at the moment of decision** - your cards,
the dealer's upcard, and the running count of cards already seen. Nothing may peek at
undealt cards. "Best strategy per shoe" means the best *pre-committed* strategy on that
shoe, never a strategy fitted to that shoe's card order (that would be hindsight and would
report a fantasy edge that vanishes at a real table). Card counting is the legitimate way
to adapt to a specific shoe in real time.

## Quick start

```bash
cd blackjack-strategy-lab
python tests.py                       # prove it's correct (unit + simulation gates)
python run.py list                    # show the strategy roster
python run.py tournament 40000        # one tournament; accumulates to data/lab.db
python run.py report                  # write STATUS.md
python run.py optimize "Hi-Lo" --dev  # tune ramp/wong, validate out-of-sample
python run.py loop                    # run forever, accumulating (Ctrl+C to stop)
```

Read **[STATUS.md](STATUS.md)** for the current standings.

## How to read the results (important)

Two rankings, because they answer different questions:

- **Per shoe (the headline).** One shoe is a fixed block of table time, so EV-per-shoe is
  the fair way to compare strategies that play different numbers of hands (a Wong strategy
  plays few hands but still occupies the shoe). "Most viable" is ranked by the per-shoe
  **Desirability Index** = mean shoe profit / shoe volatility.
- **Per 100 hands.** Useful only if you can freely hop tables and play unlimited hands.
  Per-hand EV is *trivially* maximized by playing only the very best hands, so never rank
  by it alone.

Also reported: probability a shoe ends profitable, risk of ruin, and the bankroll needed
for a 5% risk of ruin.

## What's built in

Counting systems (balanced, true-count normalized so they compare fairly):
Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Zen.

Strategies: flat basic (baseline), Hi-Lo bet spreads, Hi-Lo + Illustrious-18 playing
deviations, Wonging (back-counting / sit out low counts), and level-2 systems. Insurance
is taken by any counter when the count justifies it.

## Add your own strategy

Subclass `Strategy` (see `bjlab/strategies.py`) and implement `bet()` and/or `play()`,
using only `self.true_count(decks_left)` and the cards on the table. Then add it to
`default_roster()` or your own script. Example idea to test: a different bet ramp, a new
Wong-out threshold, or count-based insurance only above a higher index.

## The learning loop (optimizer)

`python run.py optimize <system> [--dev]` searches bet-ramp and Wong-out parameters on a
set of TRAIN shoes (all candidates on identical shoes, so the ranking is low-variance),
then validates the winner on a DISJOINT set of TEST shoes. A candidate only counts if it
holds up out-of-sample - this is how we avoid fooling ourselves.

## Daily / weekly check-in workflow

Every run appends a line to `logs/runs.jsonl` (timestamp, config, per-strategy EV/shoe,
EV/100, Desirability Index) and refreshes `STATUS.md`. At a check-in, share either file
(paste it, or commit and push it). From that log I can spot trends, tell you which
strategy is pulling ahead as the sample grows, and propose the next parameter change or a
new strategy to add.

## Honest findings so far (measured here)

- The **bet spread** delivers ~90% of a counter's edge. Playing deviations (Illustrious
  18) add only ~+0.1 u/100 on average and are **noisy** to measure - they need a large
  sample to show up. Don't over-value them.
- Level-2 systems (Hi-Opt II, Omega II, Zen) beat Hi-Lo slightly on betting, as their
  higher betting correlation predicts, at the cost of being harder to run by hand.
- The edge is thin and variance is large. Expect long losing stretches even when the
  long-run edge is real. A realistic bankroll is hundreds to ~1,000+ betting units.

## Not financial advice

Counting is legal but casinos will bar you for it. This is the mathematics of advantage
play, measured honestly, not a scheme to get rich. Treat the numbers as sobering.
