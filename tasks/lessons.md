# Lessons

Patterns learned from user corrections. Review at session start.

## Session 2026-11-18 (project start)
- User initially framed blackjack as a "find the winning card-order pattern" problem
  (crypto-mining analogy). Corrected: no such edge exists in a shuffled shoe. The real,
  mathematically proven edges are (1) basic strategy and (2) card counting (composition,
  not order). Always correct a flawed premise before building, per user's mentor preference.
- User wants honesty over agreement. Report measured numbers, including unfavorable ones
  (high variance, slow grind, large bankroll needed). Never oversell the edge.
- Container is ephemeral; "runs forever" must be designed as resumable + portable to the
  user's own machine, with data persisted locally and accumulating across runs.
- A demo must actually demonstrate the claim. First Martingale demo (one long run) showed
  a positive net from variance, contradicting the "it fails" narrative. Lesson: for a
  claim about EV/variance, show a DISTRIBUTION over many sessions, not one sample. Caught
  it by reading the output critically instead of shipping a result that contradicted the
  text next to it.
