"""Risk and edge metrics. All in betting units."""
import math


def summarize(hands, sum_net, sum_sq, sum_wagered):
    if hands == 0:
        return None
    mean = sum_net / hands                       # EV per hand (round)
    var = sum_sq / hands - mean * mean
    if var < 0:
        var = 0.0
    sd = math.sqrt(var)
    edge = (sum_net / sum_wagered) if sum_wagered else 0.0
    di = (1000.0 * mean / sd) if sd > 0 else 0.0  # Desirability Index
    n0 = (var / (mean * mean)) if mean > 0 else float("inf")
    return {
        "hands": hands,
        "mean_per_hand": mean,
        "sd_per_hand": sd,
        "variance_per_hand": var,
        "edge_pct": edge * 100,                  # player return per unit wagered
        "ev_per_100": mean * 100,
        "sd_per_100": sd * 10.0,                 # sd scales with sqrt(100)=10
        "di": di,                                # higher = more viable (risk-adjusted)
        "n0": n0,
    }


def summarize_shoe(shoes, shoe_net_sum, shoe_net_sq):
    """Per-shoe metrics. One shoe ~ one fixed block of table time, so this is the fair
    unit for 'most viable': it prices in opportunity cost that per-hand EV ignores
    (e.g. a Wong strategy plays few hands but each shoe still takes the same time)."""
    import math as _m
    if shoes == 0:
        return None
    mean = shoe_net_sum / shoes                  # EV per shoe (units)
    var = shoe_net_sq / shoes - mean * mean
    if var < 0:
        var = 0.0
    sd = _m.sqrt(var)
    di = (mean / sd) if sd > 0 else 0.0          # per-shoe risk-adjusted score
    # Normal-approx probability a single shoe ends profitable.
    prob_profit = 0.5 * (1.0 + _m.erf(mean / (sd * _m.sqrt(2)))) if sd > 0 else (
        1.0 if mean > 0 else 0.0)
    return {"ev_per_shoe": mean, "sd_per_shoe": sd, "shoe_di": di,
            "prob_profit": prob_profit, "shoes": shoes}


def risk_of_ruin(mean_per_hand, variance_per_hand, bankroll_units):
    if mean_per_hand <= 0 or variance_per_hand <= 0:
        return 1.0
    return math.exp(-2.0 * mean_per_hand * bankroll_units / variance_per_hand)


def bankroll_for_ror(mean_per_hand, variance_per_hand, target_ror):
    if mean_per_hand <= 0 or variance_per_hand <= 0 or not (0 < target_ror < 1):
        return float("inf")
    return -variance_per_hand * math.log(target_ror) / (2.0 * mean_per_hand)


def kelly_unit_fraction(mean_per_hand, variance_per_hand):
    """Fraction of bankroll the AVERAGE bet should be for full-Kelly growth."""
    if variance_per_hand <= 0:
        return 0.0
    return max(0.0, mean_per_hand / variance_per_hand)
