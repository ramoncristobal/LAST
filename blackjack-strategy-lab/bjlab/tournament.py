"""Run many strategies on IDENTICAL shoes and collect per-shoe + aggregate results.

Common random numbers: every strategy plays the same shuffled shoe each iteration, so the
comparison is paired (fair) and low-variance on the differences. The shoe list is only
read (never mutated), so all strategies can share it.
"""
import random

from .engine import make_shoe, play_shoe


def run_tournament(rules, num_shoes, roster, rng=None):
    rng = rng or random.Random()
    agg = {s.name: {"hands": 0, "sum_net": 0.0, "sum_sq": 0.0, "sum_wagered": 0.0,
                    "shoes": 0, "shoes_pos": 0, "best_shoes": 0,
                    "shoe_net_sum": 0.0, "shoe_net_sq": 0.0}
           for s in roster}

    for _ in range(num_shoes):
        cards, cut = make_shoe(rules, rng)
        best_name = None
        best_net = -1e18
        for s in roster:
            r = play_shoe(cards, cut, rules, s)
            a = agg[s.name]
            a["hands"] += r["hands"]
            a["sum_net"] += r["net"]
            a["sum_sq"] += r["sum_sq"]
            a["sum_wagered"] += r["wagered"]
            a["shoes"] += 1
            if r["net"] > 0:
                a["shoes_pos"] += 1
            a["shoe_net_sum"] += r["net"]
            a["shoe_net_sq"] += r["net"] * r["net"]
            if r["net"] > best_net:
                best_net = r["net"]
                best_name = s.name
        if best_name is not None:
            agg[best_name]["best_shoes"] += 1

    return agg
