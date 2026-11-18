"""Generate STRATEGY_GUIDE.md from the code + accumulated simulation data."""
import os

from rules import Rules
from strategy import decide
from analysis import summarize, risk_of_ruin, bankroll_for_ror
import storage

GUIDE_PATH = os.path.join(os.path.dirname(__file__), "STRATEGY_GUIDE.md")
UPCARDS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def _cell(cards, up, is_pair, rules):
    can_sur = (len(cards) == 2 and not is_pair and rules.surrender)
    a = decide(cards, up, True, is_pair, can_sur, rules)
    if a == 'R':
        return 'SUR'
    if a == 'P':
        return 'P'
    if a == 'D':
        a2 = decide(cards, up, False, is_pair, can_sur, rules)
        return 'Ds' if a2 == 'S' else 'D'
    return a


def _hdr():
    cols = " | ".join(f"{('A' if u == 11 else u):>3}" for u in UPCARDS)
    sep = " | ".join(["---"] * len(UPCARDS))
    return cols, sep


def chart_markdown(rules):
    cols, sep = _hdr()
    out = []

    out.append("### Hard totals (your two cards, no ace / no pair)\n")
    out.append(f"| Hand | {cols} |")
    out.append(f"| --- | {sep} |")
    # representative non-pair hard hands
    # Representative non-pair hard hands (hard 20 is only T,T, shown under Pairs).
    hard = {5: [2, 3], 6: [2, 4], 7: [2, 5], 8: [3, 5], 9: [2, 7], 10: [2, 8],
            11: [5, 6], 12: [10, 2], 13: [10, 3], 14: [10, 4], 15: [10, 5],
            16: [10, 6], 17: [10, 7], 18: [10, 8], 19: [10, 9]}
    for t in range(5, 20):
        cards = hard[t]
        row = " | ".join(f"{_cell(cards, u, False, rules):>3}" for u in UPCARDS)
        out.append(f"| **{t}** | {row} |")
    out.append("")

    out.append("### Soft totals (one ace counted as 11)\n")
    out.append(f"| Hand | {cols} |")
    out.append(f"| --- | {sep} |")
    for x in range(2, 10):           # A2..A9
        cards = [11, x]
        label = f"A,{x}"
        row = " | ".join(f"{_cell(cards, u, False, rules):>3}" for u in UPCARDS)
        out.append(f"| **{label}** | {row} |")
    out.append("")

    out.append("### Pairs\n")
    out.append(f"| Pair | {cols} |")
    out.append(f"| --- | {sep} |")
    for c in range(2, 12):
        cards = [c, c]
        name = "A,A" if c == 11 else ("T,T" if c == 10 else f"{c},{c}")
        row = " | ".join(f"{_cell(cards, u, True, rules):>3}" for u in UPCARDS)
        out.append(f"| **{name}** | {row} |")
    out.append("")

    out.append("**Legend:** H = hit · S = stand · D = double (hit if not allowed) · "
               "Ds = double (stand if not allowed) · P = split · SUR = surrender "
               "(hit if not allowed)\n")
    return "\n".join(out)


def build(rules=None, unit_dollars=25, hands_per_hour=100):
    rules = rules or Rules()
    conn = storage.connect()
    cfg = rules.label()

    flat = storage.get_aggregate(conn, cfg, "flat")
    cnt = storage.get_aggregate(conn, cfg, "count")
    edges = storage.get_count_edge(conn, cfg)

    L = []
    L.append("# Blackjack Strategy Guide (data-backed)\n")
    L.append("> Generated from millions of simulated shoes by this engine. "
             "Every number below is measured, not quoted.\n")
    L.append(f"**Rules modeled:** {rules.decks} decks · "
             f"{'dealer hits soft 17' if rules.h17 else 'dealer stands on soft 17'} · "
             f"{'DAS' if rules.das else 'no DAS'} · "
             f"{'late surrender' if rules.surrender else 'no surrender'} · "
             f"blackjack pays {rules.bj_payout}:1 · "
             f"{int(rules.penetration*100)}% penetration\n")

    L.append("## The honest bottom line\n")
    L.append("- **Basic strategy alone does not win.** It only shrinks the house edge to "
             "a small loss. You cannot bet your way out of a negative edge.")
    L.append("- **Card counting is the only legal, proven edge**, and it is small, "
             "high-variance, and slow. It tracks the *composition* of the remaining "
             "shoe (not the order of cards), bets big when few high cards are gone.")
    L.append("- **Betting systems (Martingale, etc.) do nothing** to the edge. Run "
             "`python run.py martingale` to watch one fail.\n")

    if flat:
        s = summarize(*flat)
        L.append("## 1. Basic strategy (measured)\n")
        L.append(f"- Hands simulated: **{s['hands']:,}**")
        L.append(f"- House edge: **{s['house_edge_pct']:.3f}%** per hand "
                 f"(you lose about this fraction of each bet on average)")
        L.append(f"- Std dev per hand: **{s['sd_per_hand']:.2f} units** "
                 "(this is why short-term swings feel random)\n")

    L.append("## 2. The optimal basic strategy chart\n")
    L.append("Memorize this. It is derived directly from the engine, so it matches "
             "exactly how the winning simulations played.\n")
    L.append(chart_markdown(rules))

    if cnt and edges:
        s = summarize(*cnt)
        L.append("## 3. Card counting (Hi-Lo) - the real edge, measured\n")
        L.append(f"- Hands simulated with a 1-12 bet spread: **{s['hands']:,}**")
        L.append(f"- Overall edge: **{s['edge_per_unit_wagered']*100:+.3f}%** per unit wagered")
        L.append(f"- Win rate: **{s['per_100_hands']:+.3f} units per 100 hands**")
        L.append(f"- Std dev per hand: **{s['sd_per_hand']:.2f} units**")
        n0 = s['N0']
        L.append(f"- N0 (hands until expected win = one std dev): **{n0:,.0f}** "
                 "- this is how long variance can hide your edge.\n")

        L.append("### Edge by true count\n")
        L.append("The whole game is here: raise your bet as this rises.\n")
        L.append("| True count | Player edge | Share of hands | What to do |")
        L.append("| --- | --- | --- | --- |")
        total_h = sum(r[1] for r in edges)
        for tc, h, net, wag in edges:
            if h < 1000:
                continue
            edge = (net / wag * 100) if wag else 0.0
            freq = 100 * h / total_h if total_h else 0
            if tc <= 0:
                todo = "min bet (or leave the table)"
            elif tc == 1:
                todo = "min bet"
            else:
                todo = f"bet ~{min(12, 2**(tc-1) if tc<=4 else 12)} units"
            L.append(f"| {tc:+d} | {edge:+.2f}% | {freq:.1f}% | {todo} |")
        L.append("")

        L.append("### Recommended bet spread\n")
        L.append("| True count | Units to bet |")
        L.append("| --- | --- |")
        for thr, u in [(0, 1), (1, 1), (2, 2), (3, 4), (4, 8), (5, 12)]:
            lab = f"{thr} or less" if thr == 0 else f"{thr}"
            L.append(f"| {lab} | {u} |")
        L.append("")

        L.append("## 4. Bankroll and risk of ruin (measured)\n")
        mean, var = s['mean_per_hand'], s['variance_per_hand']
        L.append("Risk of ruin = chance you lose your whole bankroll before your edge "
                 "pays off. Units are multiples of your base bet.\n")
        L.append("| Bankroll (units) | Risk of ruin |")
        L.append("| --- | --- |")
        for B in [100, 200, 400, 800, 1600]:
            ror = risk_of_ruin(mean, var, B) * 100
            L.append(f"| {B} | {ror:.1f}% |")
        L.append("")
        b5 = bankroll_for_ror(mean, var, 0.05)
        b1 = bankroll_for_ror(mean, var, 0.01)
        L.append(f"- For a **5% risk of ruin** you need about **{b5:,.0f} units**.")
        L.append(f"- For a **1% risk of ruin** you need about **{b1:,.0f} units**.\n")

        L.append("## 5. What this means in real money\n")
        ev_hr = s['per_100_hands'] * (hands_per_hour / 100.0) * unit_dollars
        sd_hr = s['sd_per_hand'] * (hands_per_hour ** 0.5) * unit_dollars
        L.append(f"Example: base unit = ${unit_dollars}, ~{hands_per_hour} hands/hour.\n")
        L.append(f"- Expected win: **${ev_hr:,.2f} per hour** on average.")
        L.append(f"- Hourly swing (1 std dev): **±${sd_hr:,.0f}** - so a losing night "
                 "is completely normal even though you have the edge.")
        L.append(f"- Bankroll for 5% ruin at this unit: **${b5*unit_dollars:,.0f}**.\n")
        L.append("> Reality check: the edge is real but thin. This is a grind requiring "
                 "discipline, a big bankroll, and tolerance for long losing stretches. "
                 "Casinos also bar counters. Treat this as the math of advantage play, "
                 "not a get-rich scheme.\n")

    L.append("## How to keep it running and learning\n")
    L.append("```\n"
             "python run.py calibrate 5000000   # measure basic-strategy edge\n"
             "python run.py count 10000000      # measure counting edge, fills count table\n"
             "python run.py loop                # run forever, accumulating data (Ctrl+C to stop)\n"
             "python run.py guide               # regenerate this guide from all data so far\n"
             "python run.py martingale          # prove a betting system fails\n"
             "```\n")
    L.append("All data accumulates in `data/results.db`. The more you run, the tighter "
             "these numbers get. Run it on your own always-on machine for continuous learning.\n")

    text = "\n".join(L)
    with open(GUIDE_PATH, "w") as f:
        f.write(text)
    conn.close()
    return GUIDE_PATH
