"""Turn accumulated aggregates into the numbers that actually matter."""
import math


def summarize(hands, sum_net, sum_sq, sum_wagered):
    """Per-hand expectation, variance, and advantage-play risk metrics (units)."""
    if hands == 0:
        return None
    mean = sum_net / hands                         # EV per hand, in units
    var = sum_sq / hands - mean * mean             # variance per hand
    if var < 0:
        var = 0.0
    sd = math.sqrt(var)
    edge = (sum_net / sum_wagered) if sum_wagered else 0.0   # return per unit wagered
    out = {
        "hands": hands,
        "mean_per_hand": mean,
        "sd_per_hand": sd,
        "variance_per_hand": var,
        "edge_per_unit_wagered": edge,
        "house_edge_pct": -edge * 100,             # positive = house wins
        "per_100_hands": mean * 100,
    }
    # N0: hands for cumulative EV to equal one standard deviation of results.
    if mean > 0 and var > 0:
        out["N0"] = var / (mean * mean)
    else:
        out["N0"] = float("inf")
    return out


def risk_of_ruin(mean_per_hand, variance_per_hand, bankroll_units):
    """Standard advantage-play RoR approximation. Returns probability in [0,1]."""
    if mean_per_hand <= 0 or variance_per_hand <= 0:
        return 1.0
    x = -2.0 * mean_per_hand * bankroll_units / variance_per_hand
    return math.exp(x)


def bankroll_for_ror(mean_per_hand, variance_per_hand, target_ror):
    """Units of bankroll needed to hit a target risk of ruin."""
    if mean_per_hand <= 0 or variance_per_hand <= 0 or not (0 < target_ror < 1):
        return float("inf")
    return -variance_per_hand * math.log(target_ror) / (2.0 * mean_per_hand)


def count_edge_table(rows):
    """rows: list of (tc, hands, sum_net, sum_wagered). Returns list of dicts."""
    out = []
    for tc, hands, sum_net, sum_wagered in rows:
        if hands == 0:
            continue
        edge = (sum_net / sum_wagered) if sum_wagered else 0.0
        out.append({
            "tc": tc,
            "hands": hands,
            "edge_pct": edge * 100,            # player return per unit wagered at this count
            "freq_pct": hands,                 # filled as fraction by caller
        })
    return out
