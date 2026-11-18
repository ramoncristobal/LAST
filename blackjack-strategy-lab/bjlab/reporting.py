"""Generate STATUS.md and the per-run snapshot from accumulated data."""
import os

from .metrics import (summarize, summarize_shoe, risk_of_ruin, bankroll_for_ror)
from . import storage

STATUS_PATH = os.path.join(storage.ROOT, "STATUS.md")


def snapshot(agg):
    """Compact per-strategy summary (for JSONL logs)."""
    out = []
    for name, a in agg.items():
        s = summarize(a["hands"], a["sum_net"], a["sum_sq"], a["sum_wagered"])
        sh = summarize_shoe(a["shoes"], a["shoe_net_sum"], a["shoe_net_sq"])
        if s is None or sh is None:
            continue
        out.append({"name": name, "ev_per_100": round(s["ev_per_100"], 4),
                    "ev_per_shoe": round(sh["ev_per_shoe"], 4),
                    "shoe_di": round(sh["shoe_di"], 4),
                    "edge_pct": round(s["edge_pct"], 4), "hands": int(a["hands"])})
    out.sort(key=lambda r: r["shoe_di"], reverse=True)
    return out


def _rows(agg):
    rows = []
    for name, a in agg.items():
        s = summarize(a["hands"], a["sum_net"], a["sum_sq"], a["sum_wagered"])
        sh = summarize_shoe(a["shoes"], a["shoe_net_sum"], a["shoe_net_sq"])
        if s is None or sh is None:
            continue
        rows.append({
            "name": name, "s": s, "sh": sh,
            "pos_pct": 100 * a["shoes_pos"] / (a["shoes"] or 1),
            "best_pct": 100 * a["best_shoes"] / (a["shoes"] or 1),
            "ror400": risk_of_ruin(s["mean_per_hand"], s["variance_per_hand"], 400) * 100,
        })
    return rows


def build_status(config, rules, unit_dollars=25, hands_per_hour=100):
    conn = storage.connect()
    agg = storage.load(conn, config)
    conn.close()
    if not agg:
        return None
    rows = _rows(agg)
    by_viable = sorted(rows, key=lambda r: r["sh"]["shoe_di"], reverse=True)
    by_money = sorted(rows, key=lambda r: r["sh"]["ev_per_shoe"], reverse=True)
    total_shoes = int(list(agg.values())[0]["shoes"])

    L = []
    L.append("# Strategy Lab - Status\n")
    L.append(f"**Rules:** {config}  |  **Shoes simulated:** {total_shoes:,}\n")
    L.append("> Measured on identical shoes (paired comparison). The headline ranking is "
             "**per shoe**, because one shoe is a fixed block of table time - that is the "
             "fair way to compare strategies that play different numbers of hands (e.g. "
             "Wonging). Per-hand EV alone is misleading: it is trivially maximized by "
             "playing only the best hands.\n")

    L.append("## Most viable (risk-adjusted, per shoe)\n")
    L.append("Ranked by per-shoe Desirability Index = mean shoe profit / shoe volatility.\n")
    L.append("| # | Strategy | EV/shoe (u) | Shoe DI | P(shoe wins) | EV/100 hands (u) | RoR@400u |")
    L.append("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for i, r in enumerate(by_viable, 1):
        sh, s = r["sh"], r["s"]
        L.append(f"| {i} | {r['name']} | {sh['ev_per_shoe']:+.3f} | {sh['shoe_di']:.3f} | "
                 f"{100*sh['prob_profit']:.0f}% | {s['ev_per_100']:+.3f} | {r['ror400']:.0f}% |")
    L.append("")

    L.append("## Most money per shoe (raw, ignores risk)\n")
    L.append("| # | Strategy | EV/shoe (u) | SD/shoe (u) | EV/100 hands (u) | Bankroll 5% RoR (u) |")
    L.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for i, r in enumerate(by_money, 1):
        sh, s = r["sh"], r["s"]
        b5 = bankroll_for_ror(s["mean_per_hand"], s["variance_per_hand"], 0.05)
        b5s = f"{b5:,.0f}" if b5 != float("inf") else "n/a"
        L.append(f"| {i} | {r['name']} | {sh['ev_per_shoe']:+.3f} | {sh['sd_per_shoe']:.2f} | "
                 f"{s['ev_per_100']:+.3f} | {b5s} |")
    L.append("")

    top = by_viable[0]
    s, sh = top["s"], top["sh"]
    ev_hr = s["ev_per_100"] * (hands_per_hour / 100.0) * unit_dollars
    sd_hr = s["sd_per_100"] * ((hands_per_hour / 100.0) ** 0.5) * unit_dollars
    b5 = bankroll_for_ror(s["mean_per_hand"], s["variance_per_hand"], 0.05)
    L.append("## Verdict\n")
    L.append(f"- **Most viable (risk-adjusted per shoe): {top['name']}** - "
             f"{sh['ev_per_shoe']:+.3f} units/shoe, wins {100*sh['prob_profit']:.0f}% of shoes.")
    L.append(f"- Most money per shoe: {by_money[0]['name']} "
             f"({by_money[0]['sh']['ev_per_shoe']:+.3f} u/shoe).")
    if b5 != float("inf"):
        L.append(f"- At ${unit_dollars}/unit, ~{hands_per_hour} hands/hr: **${ev_hr:,.2f}/hr** "
                 f"average, hourly swing ±${sd_hr:,.0f}, bankroll for 5% ruin ≈ "
                 f"**${b5*unit_dollars:,.0f}**.")
    L.append("\n### Honest caveats\n")
    L.append("- A Wong strategy's high per-hand EV comes from playing few hands; judge it "
             "by EV/shoe (fixed table time) or, if you can hop tables freely, by per-hand EV.")
    L.append("- Edges are thin and variance is large: a losing week is normal even when "
             "the long-run edge is real. Casinos also bar counters.\n")

    with open(STATUS_PATH, "w") as f:
        f.write("\n".join(L))
    return STATUS_PATH
