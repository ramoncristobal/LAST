"""Correctness gates. Run from project root: python tests.py

Two layers:
  A. Unit tests (instant) - verify each playing deviation matches the canonical Hi-Lo
     Illustrious-18 index. This is the real correctness check; it does not depend on
     simulation noise.
  B. Simulation gates - flat-basic house edge in the known band, and every counting
     strategy showing a positive edge, measured on identical shoes.

(The per-shoe benefit of deviations is small and noisy - ~+0.12 u/100 averaged over
seeds - so it is validated by the unit tests above, not by a single noisy sim run.)
"""
import random
import sys

from bjlab.rules import Rules
from bjlab.strategies import FlatBasic, CardCounter, SPREAD_1_12
from bjlab.counting import HI_LO, OMEGA_II, HI_OPT_II, ZEN
from bjlab.deviations import hilo_deviation, take_insurance
from bjlab.tournament import run_tournament
from bjlab.metrics import summarize

RULES = Rules()


def _dev(cards, up, tc, cd=True):
    return hilo_deviation(cards, up, tc, cd, RULES)


def unit_tests():
    checks = []

    def c(label, got, want):
        ok = got == want
        checks.append(ok)
        if not ok:
            print(f"    FAIL {label}: got {got!r}, want {want!r}")

    # Insurance index +3
    c("insurance@3", take_insurance(3), True)
    c("insurance@2", take_insurance(2), False)
    # Stand-if-high (basic hit)
    c("16v10@0", _dev([10, 6], 10, 0), 'S')
    c("16v10@-1", _dev([10, 6], 10, -1), None)
    c("16v9@5", _dev([10, 6], 9, 5), 'S')
    c("16v9@4", _dev([10, 6], 9, 4), None)
    c("15v10@4", _dev([10, 5], 10, 4), 'S')
    c("15v10@3", _dev([10, 5], 10, 3), None)
    c("12v3@2", _dev([10, 2], 3, 2), 'S')
    c("12v3@1", _dev([10, 2], 3, 1), None)
    c("12v2@3", _dev([10, 2], 2, 3), 'S')
    c("12v2@2", _dev([10, 2], 2, 2), None)
    # Hit-if-low (basic stand)
    c("13v2@-2", _dev([10, 3], 2, -2), 'H')
    c("13v2@-1", _dev([10, 3], 2, -1), None)
    c("13v3@-3", _dev([10, 3], 3, -3), 'H')
    c("13v3@-2", _dev([10, 3], 3, -2), None)
    c("12v4@-1", _dev([10, 2], 4, -1), 'H')
    c("12v4@0", _dev([10, 2], 4, 0), None)
    c("12v5@-3", _dev([10, 2], 5, -3), 'H')
    c("12v5@-2", _dev([10, 2], 5, -2), None)
    c("12v6@-2", _dev([10, 2], 6, -2), 'H')
    c("12v6@-1", _dev([10, 2], 6, -1), None)
    # Doubles that switch on (basic hit)
    c("11vA@1", _dev([6, 5], 11, 1), 'D')
    c("11vA@0", _dev([6, 5], 11, 0), None)
    c("9v2@1", _dev([5, 4], 2, 1), 'D')
    c("9v7@3", _dev([5, 4], 7, 3), 'D')
    c("10v10@4", _dev([6, 4], 10, 4), 'D')
    c("10v10@3", _dev([6, 4], 10, 3), None)
    c("10vA@4", _dev([6, 4], 11, 4), 'D')
    # Pair-ten splits
    c("TTv5@5", _dev([10, 10], 5, 5), 'P')
    c("TTv6@4", _dev([10, 10], 6, 4), 'P')
    c("TTv6@3", _dev([10, 10], 6, 3), None)

    ok = all(checks)
    print(f"[A] deviation encoding: {sum(checks)}/{len(checks)} checks "
          f"-> {'PASS' if ok else 'FAIL'}")
    return ok


def sim_gates():
    roster = [
        FlatBasic(),
        CardCounter("Hi-Lo", HI_LO, SPREAD_1_12, use_deviations=True),
        CardCounter("Omega II", OMEGA_II, SPREAD_1_12),
        CardCounter("Hi-Opt II", HI_OPT_II, SPREAD_1_12),
        CardCounter("Zen", ZEN, SPREAD_1_12),
    ]
    shoes = 40000
    print(f"[B] simulating {len(roster)} strategies x {shoes:,} identical shoes ...")
    agg = run_tournament(RULES, shoes, roster, rng=random.Random(2024))

    def s(name):
        a = agg[name]
        return summarize(a["hands"], a["sum_net"], a["sum_sq"], a["sum_wagered"])

    flat = s("Flat Basic (baseline)")
    counters = {n: s(n) for n in ("Hi-Lo", "Omega II", "Hi-Opt II", "Zen")}

    g1 = -0.6 <= flat["edge_pct"] <= -0.1
    g2 = all(v["edge_pct"] > 0 for v in counters.values())
    print(f"    flat basic house edge {-flat['edge_pct']:.3f}%  -> {'PASS' if g1 else 'FAIL'}")
    for n, v in counters.items():
        print(f"    {n:10s} edge {v['edge_pct']:+.3f}%  ev/100 {v['ev_per_100']:+.3f}")
    print(f"    all counters positive -> {'PASS' if g2 else 'FAIL'}")
    return g1 and g2


def main():
    print("== Unit tests ==")
    a = unit_tests()
    print("\n== Simulation gates ==")
    b = sim_gates()
    ok = a and b
    print("\nALL GATES PASSED" if ok else "\nSOME GATES FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
