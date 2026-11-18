"""Parameter optimizer with a train/test split (guards against overfitting).

Searches bet-ramp and Wong-out parameters for a counting system, scoring candidates on a
fixed set of TRAIN shoes (common random numbers), then reports the winner's performance on
a DISJOINT set of TEST shoes. A candidate only 'wins' if it also holds up out-of-sample.
"""
import random

from .strategies import CardCounter
from .tournament import run_tournament
from .metrics import summarize, summarize_shoe

CANDIDATE_RAMPS = {
    "1-6":   [(1, 1), (2, 2), (3, 3), (4, 5), (5, 6)],
    "1-8":   [(1, 1), (2, 2), (3, 4), (4, 6), (5, 8)],
    "1-12":  [(1, 1), (2, 2), (3, 4), (4, 8), (5, 12)],
    "1-16":  [(1, 1), (2, 3), (3, 6), (4, 10), (5, 16)],
    "1-20":  [(1, 1), (2, 4), (3, 8), (4, 14), (5, 20)],
    "topcap@2": [(1, 1), (2, 4), (3, 8), (4, 12), (5, 12)],
}
CANDIDATE_WONGS = [None, -1.0, 0.0, 1.0, 2.0]


def _metrics(agg, name):
    a = agg[name]
    s = summarize(a["hands"], a["sum_net"], a["sum_sq"], a["sum_wagered"])
    sh = summarize_shoe(a["shoes"], a["shoe_net_sum"], a["shoe_net_sq"])
    s.update(sh)                          # merge per-hand + per-shoe metrics
    return s


def _candidates(system, use_deviations):
    out = []
    for rname, ramp in CANDIDATE_RAMPS.items():
        for wong in CANDIDATE_WONGS:
            name = f"{rname} wong={wong}"
            out.append((name, rname, ramp, wong,
                        CardCounter(name, system, ramp,
                                    use_deviations=use_deviations, wong_out=wong)))
    return out


def optimize(rules, system, use_deviations=False, score="ev_per_shoe",
             train_shoes=12000, test_shoes=12000, train_seed=1001, test_seed=9001):
    """score: 'ev_per_shoe' (raw per-shoe profit, default - most stable) or 'shoe_di'.

    All candidates are evaluated in ONE tournament on identical shoes (paired), so the
    ranking reflects low-variance differences, not noisy absolute estimates. The caller
    should still check the out-of-sample margin against its standard error (per-shoe EV is
    high-variance; small edges need large samples to confirm).
    """
    cands = _candidates(system, use_deviations)
    roster = [c[4] for c in cands]

    train_agg = run_tournament(rules, train_shoes, roster, rng=random.Random(train_seed))
    results = []
    for name, rname, ramp, wong, _s in cands:
        results.append({"ramp_name": rname, "ramp": ramp, "wong": wong,
                        "train": _metrics(train_agg, name)})
    results.sort(key=lambda r: r["train"][score], reverse=True)
    best = results[0]

    # Out-of-sample: best vs baseline on DISJOINT shoes, paired.
    best_strat = CardCounter("BEST", system, best["ramp"],
                             use_deviations=use_deviations, wong_out=best["wong"])
    baseline = CardCounter("BASE", system, CANDIDATE_RAMPS["1-12"],
                           use_deviations=use_deviations, wong_out=None)
    test_agg = run_tournament(rules, test_shoes, [best_strat, baseline],
                              rng=random.Random(test_seed))
    best["test"] = _metrics(test_agg, "BEST")
    base_test = _metrics(test_agg, "BASE")

    return {"best": best, "baseline_test": base_test, "ranked": results,
            "score": score, "system": system.name, "use_deviations": use_deviations}
