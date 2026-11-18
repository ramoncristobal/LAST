#!/usr/bin/env python3
"""Blackjack Strategy Lab - command line.

  python run.py list                      Show the strategy roster.
  python run.py tournament [shoes]        Run a tournament, accumulate data, log it.
  python run.py report                    Write STATUS.md from accumulated data.
  python run.py loop [--shoes N]          Run tournaments forever (Ctrl+C to stop).
  python run.py optimize [system] [--dev] Tune ramp/wong on train shoes, test out-of-sample.

Data accumulates in data/lab.db; each run appends to logs/runs.jsonl. Default rules:
6 decks, S17, DAS, late surrender, 3:2, 75% penetration.
"""
import sys
import time

from bjlab.rules import Rules
from bjlab.strategies import default_roster
from bjlab.tournament import run_tournament
from bjlab.metrics import summarize
from bjlab.counting import ALL_SYSTEMS, HI_LO
from bjlab import storage, reporting, optimizer


def _print_standings(agg):
    rows = []
    for name, a in agg.items():
        s = summarize(a["hands"], a["sum_net"], a["sum_sq"], a["sum_wagered"])
        if s:
            rows.append((name, s, a))
    rows.sort(key=lambda r: r[1]["ev_per_100"], reverse=True)
    print(f"  {'strategy':32s} {'EV/100':>9s} {'edge%':>8s} {'DI':>6s} {'+shoes':>7s}")
    for name, s, a in rows:
        pos = 100 * a["shoes_pos"] / (a["shoes"] or 1)
        print(f"  {name:32s} {s['ev_per_100']:+9.3f} {s['edge_pct']:+8.3f} "
              f"{s['di']:6.0f} {pos:6.0f}%")


def cmd_tournament(shoes):
    rules = Rules()
    roster = default_roster()
    print(f"Tournament: {len(roster)} strategies x {shoes:,} identical shoes "
          f"({rules.label()}) ...")
    t0 = time.time()
    agg = run_tournament(rules, shoes, roster)
    conn = storage.connect()
    storage.accumulate(conn, rules.label(), agg)
    cum = storage.load(conn, rules.label())
    conn.close()
    storage.log_run(rules.label(), shoes, reporting.snapshot(cum))
    print(f"  done in {time.time()-t0:.1f}s. Cumulative standings:")
    _print_standings(cum)


def cmd_report():
    rules = Rules()
    path = reporting.build_status(rules.label(), rules)
    print(f"STATUS written: {path}" if path else "No data yet. Run a tournament first.")


def cmd_loop(shoes):
    rules = Rules()
    roster = default_roster()
    print(f"Looping: {len(roster)} strategies x {shoes:,} shoes/batch. Ctrl+C to stop.")
    print(f"Rules: {rules.label()}   DB: {storage.DB_PATH}\n")
    b = 0
    try:
        while True:
            b += 1
            t0 = time.time()
            agg = run_tournament(rules, shoes, roster)
            conn = storage.connect()
            storage.accumulate(conn, rules.label(), agg)
            cum = storage.load(conn, rules.label())
            conn.close()
            storage.log_run(rules.label(), shoes, reporting.snapshot(cum))
            reporting.build_status(rules.label(), rules)
            print(f"[batch {b}] +{shoes:,} shoes in {time.time()-t0:.1f}s")
            _print_standings(cum)
            print()
    except KeyboardInterrupt:
        reporting.build_status(rules.label(), rules)
        print("\nStopped. STATUS.md updated.")


def cmd_optimize(system_name, use_dev):
    rules = Rules()
    system = ALL_SYSTEMS.get(system_name, HI_LO)
    print(f"Optimizing {system.name} (deviations={'on' if use_dev else 'off'}) "
          "on train shoes, validating on disjoint test shoes ...\n")
    res = optimizer.optimize(rules, system, use_deviations=use_dev)
    best = res["best"]
    bt, tt, base = best["train"], best["test"], res["baseline_test"]
    bt_hps = bt["hands"] / bt["shoes"]
    tt_hps = tt["hands"] / tt["shoes"]
    base_hps = base["hands"] / base["shoes"]
    print(f"  Best params: ramp={best['ramp_name']}  wong_out={best['wong']}")
    print(f"    TRAIN : EV/shoe={bt['ev_per_shoe']:+.3f}  ({bt_hps:.1f} hands/shoe)")
    print(f"    TEST  : EV/shoe={tt['ev_per_shoe']:+.3f}  ({tt_hps:.1f} hands/shoe)  (out-of-sample)")
    print(f"  Baseline 1-12 no-wong TEST: EV/shoe={base['ev_per_shoe']:+.3f}  "
          f"({base_hps:.1f} hands/shoe)")

    diff = tt["ev_per_shoe"] - base["ev_per_shoe"]
    se = ((tt["sd_per_shoe"] ** 2) / tt["shoes"] +
          (base["sd_per_shoe"] ** 2) / base["shoes"]) ** 0.5
    z = diff / se if se > 0 else 0.0
    ratio = (tt["ev_per_shoe"] / bt["ev_per_shoe"]) if bt["ev_per_shoe"] else 0.0
    stable = 0.6 <= ratio <= 1.6         # train and test estimates roughly agree
    if z >= 2 and stable and diff > 0:
        verdict = f"BEATS baseline ({diff:+.3f} u/shoe, ~{z:.1f} SE, train/test consistent)"
    elif diff > 0:
        why = "estimate unstable (train vs test differ a lot)" if not stable else \
              f"only ~{z:.1f} SE - not yet significant"
        verdict = f"looks better ({diff:+.3f} u/shoe) but {why}; run more shoes to confirm"
    else:
        verdict = f"does NOT beat baseline ({diff:+.3f} u/shoe)"
    print(f"\n  Verdict: tuned params {verdict}.")
    print("  Note: configs that play few hands/shoe (heavy Wong + wide spread) earn more "
          "per shoe but with brutal variance and a much larger bankroll; per-shoe EV is\n"
          "  high-variance, so treat single runs as indicative, not final.")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "list":
        for s in default_roster():
            print(" -", s.name)
    elif cmd == "tournament":
        cmd_tournament(int(argv[2]) if len(argv) > 2 else 20000)
    elif cmd == "report":
        cmd_report()
    elif cmd == "loop":
        shoes = 20000
        if "--shoes" in argv:
            shoes = int(argv[argv.index("--shoes") + 1])
        cmd_loop(shoes)
    elif cmd == "optimize":
        name = argv[2] if len(argv) > 2 and not argv[2].startswith("--") else "Hi-Lo"
        cmd_optimize(name, "--dev" in argv)
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
