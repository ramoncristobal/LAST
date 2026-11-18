# Strategy Lab - Status

**Rules:** 6D_S17_DAS1_LS1_BJ1.5_pen0.75  |  **Shoes simulated:** 40,000

> Measured on identical shoes (paired comparison). The headline ranking is **per shoe**, because one shoe is a fixed block of table time - that is the fair way to compare strategies that play different numbers of hands (e.g. Wonging). Per-hand EV alone is misleading: it is trivially maximized by playing only the best hands.

## Most viable (risk-adjusted, per shoe)

Ranked by per-shoe Desirability Index = mean shoe profit / shoe volatility.

| # | Strategy | EV/shoe (u) | Shoe DI | P(shoe wins) | EV/100 hands (u) | RoR@400u |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Hi-Lo 1-12 + I18 + Wong | +0.586 | 0.031 | 51% | +2.531 | 28% |
| 2 | Zen 1-12 | +0.424 | 0.023 | 51% | +0.972 | 38% |
| 3 | Hi-Lo 1-12 | +0.426 | 0.023 | 51% | +0.978 | 39% |
| 4 | Omega II 1-12 | +0.412 | 0.022 | 51% | +0.945 | 39% |
| 5 | Hi-Opt II 1-12 | +0.429 | 0.022 | 51% | +0.985 | 42% |
| 6 | Hi-Lo 1-12 + I18 | +0.314 | 0.016 | 51% | +0.722 | 53% |
| 7 | Hi-Lo 1-6 (low variance) | +0.155 | 0.012 | 50% | +0.355 | 46% |
| 8 | Flat Basic (baseline) | -0.163 | -0.022 | 49% | -0.374 | 100% |

## Most money per shoe (raw, ignores risk)

| # | Strategy | EV/shoe (u) | SD/shoe (u) | EV/100 hands (u) | Bankroll 5% RoR (u) |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | Hi-Lo 1-12 + I18 + Wong | +0.586 | 18.80 | +2.531 | 942 |
| 2 | Hi-Opt II 1-12 | +0.429 | 19.61 | +0.985 | 1,366 |
| 3 | Hi-Lo 1-12 | +0.426 | 18.80 | +0.978 | 1,266 |
| 4 | Zen 1-12 | +0.424 | 18.63 | +0.972 | 1,252 |
| 5 | Omega II 1-12 | +0.412 | 18.63 | +0.945 | 1,278 |
| 6 | Hi-Lo 1-12 + I18 | +0.314 | 19.49 | +0.722 | 1,888 |
| 7 | Hi-Lo 1-6 (low variance) | +0.155 | 12.41 | +0.355 | 1,524 |
| 8 | Flat Basic (baseline) | -0.163 | 7.48 | -0.374 | n/a |

## Verdict

- **Most viable (risk-adjusted per shoe): Hi-Lo 1-12 + I18 + Wong** - +0.586 units/shoe, wins 51% of shoes.
- Most money per shoe: Hi-Lo 1-12 + I18 + Wong (+0.586 u/shoe).
- At $25/unit, ~100 hands/hr: **$63.28/hr** average, hourly swing ±$998, bankroll for 5% ruin ≈ **$23,561**.

### Honest caveats

- A Wong strategy's high per-hand EV comes from playing few hands; judge it by EV/shoe (fixed table time) or, if you can hop tables freely, by per-hand EV.
- Edges are thin and variance is large: a losing week is normal even when the long-run edge is real. Casinos also bar counters.
