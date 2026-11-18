"""Card counting: Hi-Lo bet ramp.

The engine's Shoe already tracks the Hi-Lo running count and exposes true_count().
This module only decides how many units to bet given the current true count.

A bet ramp is a list of (true_count_threshold, units) rising steps. Below the first
threshold you bet the base unit. This models a realistic hand-to-hand spread a solo
player can actually execute at the table.
"""

# Default 1-12 spread. Aggressive enough to show a clear edge, still table-plausible.
DEFAULT_RAMP = [(1, 1), (2, 2), (3, 4), (4, 8), (5, 12)]

# A conservative spread for lower variance / smaller bankroll.
CONSERVATIVE_RAMP = [(1, 1), (2, 2), (3, 3), (4, 5), (5, 6)]


def bet_for(true_count, ramp=DEFAULT_RAMP, base=1):
    units = base
    for threshold, u in ramp:
        if true_count >= threshold:
            units = u
    return units
