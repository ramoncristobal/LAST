"""Correctness gates. Run: python tests.py

These prove the engine is right, not just that it runs:
  1. Basic-strategy house edge lands in the known-correct band (~0.3-0.6%).
  2. Dealer bust rate is realistic (~28%).
  3. Counting edge rises with the true count and is positive overall.
"""
import sys

from rules import Rules
from simulate import simulate_batch
from analysis import summarize, count_edge_table
from engine import Shoe, play_dealer
import random


def test_dealer_bust_rate():
    rules = Rules()
    rng = random.Random(7)
    shoe = Shoe(rules, rng)
    busts = 0
    trials = 300_000
    for _ in range(trials):
        if shoe.needs_shuffle():
            shoe.reshuffle()
        dealer = [shoe.draw(), shoe.draw()]
        t = play_dealer(dealer, shoe.draw, rules.h17)
        if t > 21:
            busts += 1
    rate = busts / trials
    ok = 0.26 <= rate <= 0.30
    print(f"[dealer bust] rate={rate:.4f}  expect ~0.28  -> {'PASS' if ok else 'FAIL'}")
    return ok


def test_basic_strategy_edge():
    rules = Rules()
    r = simulate_batch(rules, 2_000_000, mode="flat", seed=1)
    s = summarize(r["hands"], r["sum_net"], r["sum_sq"], r["sum_wagered"])
    he = s["house_edge_pct"]
    ok = 0.2 <= he <= 0.7
    print(f"[basic strategy] house edge={he:.3f}%  expect ~0.4%  "
          f"(sd/hand={s['sd_per_hand']:.3f})  -> {'PASS' if ok else 'FAIL'}")
    return ok


def test_counting_edge_monotonic():
    rules = Rules()
    r = simulate_batch(rules, 3_000_000, mode="count", seed=2, track_counts=True)
    s = summarize(r["hands"], r["sum_net"], r["sum_sq"], r["sum_wagered"])
    rows = [(tc, h, net, wag) for tc, (h, net, wag) in sorted(r["buckets"].items())]
    table = count_edge_table(rows)
    neg = [t["edge_pct"] for t in table if t["tc"] <= -2 and t["hands"] > 5000]
    pos = [t["edge_pct"] for t in table if t["tc"] >= 3 and t["hands"] > 5000]
    overall_ok = s["edge_per_unit_wagered"] > 0
    mono_ok = (sum(pos) / len(pos)) > (sum(neg) / len(neg)) if neg and pos else False
    print(f"[counting] overall edge/unit={s['edge_per_unit_wagered']*100:.3f}%  "
          f"per-100-hands={s['per_100_hands']:.3f}u  N0={s['N0']:.0f}")
    print("           edge by true count:")
    total_h = sum(t["hands"] for t in table)
    for t in table:
        print(f"             TC {t['tc']:+d}: edge {t['edge_pct']:+.2f}%  "
              f"({100*t['hands']/total_h:4.1f}% of hands)")
    print(f"           overall positive -> {'PASS' if overall_ok else 'FAIL'}; "
          f"edge rises with count -> {'PASS' if mono_ok else 'FAIL'}")
    return overall_ok and mono_ok


def main():
    results = [
        test_dealer_bust_rate(),
        test_basic_strategy_edge(),
        test_counting_edge_monotonic(),
    ]
    print()
    if all(results):
        print("ALL CORRECTNESS GATES PASSED")
        return 0
    print("SOME GATES FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
