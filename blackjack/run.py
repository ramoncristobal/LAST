#!/usr/bin/env python3
"""Blackjack research engine - command line.

Usage:
  python run.py calibrate [hands]   Flat basic strategy; measures the house edge.
  python run.py count [hands]       Hi-Lo counting + bet spread; measures the real edge.
  python run.py loop [--mode M]     Run batches forever, accumulating data (Ctrl+C to stop).
  python run.py guide               Regenerate STRATEGY_GUIDE.md from accumulated data.
  python run.py martingale [hands]  Demonstrate that a betting progression does NOT win.

All results accumulate in data/results.db across runs.
"""
import sys
import time

from rules import Rules
from simulate import simulate_batch
from analysis import summarize, risk_of_ruin
import storage
import guide as guide_mod


def _persist(rules, mode, r):
    conn = storage.connect()
    cfg = rules.label()
    storage.update_aggregate(conn, cfg, mode, r["hands"], r["sum_net"],
                             r["sum_sq"], r["sum_wagered"])
    if r["buckets"]:
        storage.update_count_edge(conn, cfg, r["buckets"])
    conn.commit()
    row = storage.get_aggregate(conn, cfg, mode)
    conn.close()
    return summarize(*row)


def _print_summary(mode, s):
    print(f"  cumulative hands : {s['hands']:,}")
    if mode == "flat":
        print(f"  house edge       : {s['house_edge_pct']:.3f}%  (lower = better for you)")
    else:
        print(f"  player edge      : {s['edge_per_unit_wagered']*100:+.3f}% per unit wagered")
        print(f"  win rate         : {s['per_100_hands']:+.3f} units / 100 hands")
        print(f"  risk of ruin @400u: {risk_of_ruin(s['mean_per_hand'], s['variance_per_hand'], 400)*100:.1f}%")
    print(f"  std dev / hand   : {s['sd_per_hand']:.2f} units")


def cmd_calibrate(hands):
    rules = Rules()
    print(f"Calibrating basic strategy over {hands:,} hands ({rules.label()}) ...")
    r = simulate_batch(rules, hands, mode="flat", seed=None)
    s = _persist(rules, "flat", r)
    _print_summary("flat", s)


def cmd_count(hands):
    rules = Rules()
    print(f"Simulating Hi-Lo counting over {hands:,} hands ({rules.label()}) ...")
    r = simulate_batch(rules, hands, mode="count", seed=None, track_counts=True)
    s = _persist(rules, "count", r)
    _print_summary("count", s)


def cmd_loop(mode):
    rules = Rules()
    batch = 1_000_000
    print(f"Looping forever in {mode} mode, {batch:,} hands per batch. Ctrl+C to stop.")
    print(f"Rules: {rules.label()}   Data: {storage.DB_PATH}\n")
    b = 0
    try:
        while True:
            b += 1
            t0 = time.time()
            r = simulate_batch(rules, batch, mode=mode, seed=None,
                               track_counts=(mode == "count"))
            s = _persist(rules, mode, r)
            dt = time.time() - t0
            print(f"[batch {b}]  (+{batch:,} hands in {dt:.1f}s, "
                  f"{batch/dt:,.0f}/s)")
            _print_summary(mode, s)
            print()
    except KeyboardInterrupt:
        print("\nStopped. Regenerating guide from all accumulated data ...")
        path = guide_mod.build(rules)
        print(f"Guide written: {path}")


def cmd_martingale(sessions=20000):
    """Honest Martingale demo: many bankroll-limited sessions expose the bust tail.

    A single long run of Martingale is dominated by variance and can look like a win
    (that is exactly why it fools people). The truth shows up over many sessions: it
    wins a small amount most of the time, then a rare losing streak wipes out a whole
    bankroll, and the average result is still a loss.
    """
    import random
    from engine import Shoe, play_round
    from strategy import decide
    rules = Rules()
    bankroll0 = 200          # units you walk in with
    goal = 50                # quit when ahead by this
    table_cap = 500          # max single bet the table allows
    max_hands = 5000         # safety cap per session

    print(f"Martingale: {sessions:,} independent sessions, "
          f"start {bankroll0}u, quit at +{goal}u, table max {table_cap}u.\n")

    rng = random.Random()
    shoe = Shoe(rules, rng)
    busts = 0
    goals = 0
    walked = 0
    total_net = 0.0
    total_wagered = 0.0

    for _ in range(sessions):
        bankroll = bankroll0
        bet = 1
        outcome = "walk"
        for _h in range(max_hands):
            if shoe.needs_shuffle():
                shoe.reshuffle()
            wager = min(bet, int(bankroll), table_cap)
            if wager < 1:
                outcome = "bust"
                break
            result = play_round(shoe, rules, decide, wager)
            bankroll += result
            total_net += result
            total_wagered += wager
            if bankroll <= 0:
                outcome = "bust"
                break
            if result < 0:
                bet = bet * 2            # chase the loss
            else:
                bet = 1                  # reset after a win
            if bankroll - bankroll0 >= goal:
                outcome = "goal"
                break
        if outcome == "bust":
            busts += 1
        elif outcome == "goal":
            goals += 1
        else:
            walked += 1

    edge = (total_net / total_wagered * 100) if total_wagered else 0.0
    print(f"  reached +{goal}u goal : {goals:,} sessions ({100*goals/sessions:.1f}%)")
    print(f"  BUSTED (lost {bankroll0}u): {busts:,} sessions ({100*busts/sessions:.1f}%)")
    print(f"  still playing at cap : {walked:,} sessions ({100*walked/sessions:.1f}%)")
    print(f"  average net/session  : {total_net/sessions:+.2f} units")
    print(f"  edge per unit wagered: {edge:+.3f}%  (the house edge, unchanged by the system)")
    print("\n  Verdict: Martingale wins small, often - and then one bust erases it all.")
    print("  The edge per dollar wagered is UNCHANGED and negative. It is not a system.")
    print("  Flat basic strategy loses ~0.36% per unit with none of this ruin risk.")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "calibrate":
        cmd_calibrate(int(argv[2]) if len(argv) > 2 else 5_000_000)
    elif cmd == "count":
        cmd_count(int(argv[2]) if len(argv) > 2 else 10_000_000)
    elif cmd == "loop":
        mode = "count"
        if "--mode" in argv:
            mode = argv[argv.index("--mode") + 1]
        cmd_loop(mode)
    elif cmd == "guide":
        path = guide_mod.build(Rules())
        print(f"Guide written: {path}")
    elif cmd == "martingale":
        cmd_martingale(int(argv[2]) if len(argv) > 2 else 20_000)
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
