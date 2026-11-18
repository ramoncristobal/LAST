"""Monte Carlo simulation batches."""
import math
import random

from engine import Shoe, play_round
from strategy import decide
from counting import bet_for, DEFAULT_RAMP


def simulate_batch(rules, hands, mode="flat", ramp=DEFAULT_RAMP, seed=None,
                   track_counts=False):
    """Play `hands` rounds. Returns a stats dict.

    mode:
      "flat"  -> always bet 1 unit (measures house edge vs basic strategy)
      "count" -> bet per Hi-Lo true-count ramp (measures the counter's real edge)
    """
    rng = random.Random(seed)
    shoe = Shoe(rules, rng)
    n = 0
    sum_net = 0.0
    sum_sq = 0.0
    sum_wagered = 0.0
    buckets = {}                      # tc -> [hands, net, wagered]

    for _ in range(hands):
        if shoe.needs_shuffle():
            shoe.reshuffle()
        if mode == "count":
            tc = shoe.true_count()
            bet = bet_for(tc, ramp)
        else:
            tc = 0
            bet = 1
        net = play_round(shoe, rules, decide, bet)

        n += 1
        sum_net += net
        sum_sq += net * net
        sum_wagered += bet

        if track_counts:
            key = max(-5, min(10, int(math.floor(tc))))
            b = buckets.get(key)
            if b is None:
                buckets[key] = [1, net, bet]
            else:
                b[0] += 1
                b[1] += net
                b[2] += bet

    return {
        "hands": n,
        "sum_net": sum_net,
        "sum_sq": sum_sq,
        "sum_wagered": sum_wagered,
        "buckets": {k: tuple(v) for k, v in buckets.items()},
    }
