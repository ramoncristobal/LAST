"""Hi-Lo playing deviations (a validated subset of the 'Illustrious 18').

A deviation overrides basic strategy when the Hi-Lo TRUE COUNT crosses an index. These
are indexed for Hi-Lo specifically. Each returns an action ('H','S','D','P') or None
(use basic). Insurance is handled separately (take at TC >= 3).

The convention: for a hand whose basic play is HIT, we STAND once TC >= index. For a hand
whose basic play is STAND, we HIT once TC < index. Doubles turn on at TC >= index.

Correctness is gated by simulation: adding these must raise the measured edge vs plain
basic play. If a future edit makes the edge drop, a deviation is wrong.
"""
from .basic_strategy import hand_total


INSURANCE_INDEX = 3


def take_insurance(true_count):
    return true_count >= INSURANCE_INDEX


def hilo_deviation(cards, up, tc, can_double, rules):
    """Return an overriding action or None."""
    t, soft = hand_total(cards)
    is_pair = len(cards) == 2 and cards[0] == cards[1]

    # Pair of tens: split only at very high counts (otherwise stand).
    if is_pair and cards[0] == 10:
        if up == 5 and tc >= 5:
            return 'P'
        if up == 6 and tc >= 4:
            return 'P'
        return None

    if soft or is_pair:
        return None                     # remaining I18 entries are hard totals

    # Stand-if-count-high (basic = hit)
    if t == 16 and up == 10:
        return 'S' if tc >= 0 else None     # else basic (surrender/ stand)
    if t == 16 and up == 9:
        return 'S' if tc >= 5 else None
    if t == 15 and up == 10:
        return 'S' if tc >= 4 else None
    if t == 12 and up == 2:
        return 'S' if tc >= 3 else None
    if t == 12 and up == 3:
        return 'S' if tc >= 2 else None

    # Hit-if-count-low (basic = stand)
    if t == 13 and up == 2:
        return 'H' if tc < -1 else None
    if t == 13 and up == 3:
        return 'H' if tc < -2 else None
    if t == 12 and up == 4:
        return 'H' if tc < 0 else None
    if t == 12 and up == 5:
        return 'H' if tc < -2 else None
    if t == 12 and up == 6:
        return 'H' if tc < -1 else None

    # Doubles that switch on with the count (basic = hit)
    if can_double:
        if t == 11 and up == 11:
            return 'D' if tc >= 1 else None
        if t == 9 and up == 2:
            return 'D' if tc >= 1 else None
        if t == 9 and up == 7:
            return 'D' if tc >= 3 else None
        if t == 10 and up == 10:
            return 'D' if tc >= 4 else None
        if t == 10 and up == 11:
            return 'D' if tc >= 4 else None

    return None
