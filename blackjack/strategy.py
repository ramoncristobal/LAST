"""Optimal basic strategy for multi-deck games.

Encoded for 4-8 decks, S17, DAS, Late Surrender (the realistic default). Functions
accept `can_double` / `das` so the same code serves no-double and no-DAS situations.
The engine calls `decide`; the guide renders the chart by calling `decide` over every
hand, so the printed chart can never disagree with how the engine actually plays.

Upcard values: 2..10, and 11 for an ace.
"""
from engine import total


def hard_action(t, up, can_double):
    if t >= 17:
        return 'S'
    if t <= 8:
        return 'H'
    if t == 9:
        return 'D' if (3 <= up <= 6 and can_double) else 'H'
    if t == 10:
        return 'D' if (up <= 9 and can_double) else 'H'
    if t == 11:
        return 'D' if (up <= 10 and can_double) else 'H'   # S17: hit vs ace
    if t == 12:
        return 'S' if 4 <= up <= 6 else 'H'
    # 13..16
    return 'S' if 2 <= up <= 6 else 'H'


def soft_action(t, up, can_double):
    # t is the soft total (ace counted as 11), ranges 13..21.
    if t >= 19:                      # A8, A9 -> stand (S17)
        return 'S'
    if t == 18:                      # A7
        if 2 <= up <= 6:
            return 'D' if can_double else 'S'
        if up in (7, 8):
            return 'S'
        return 'H'                   # vs 9, 10, A
    if t == 17:                      # A6
        return 'D' if (3 <= up <= 6 and can_double) else 'H'
    if t in (15, 16):                # A4, A5
        return 'D' if (4 <= up <= 6 and can_double) else 'H'
    # A2, A3 (13, 14)
    return 'D' if (5 <= up <= 6 and can_double) else 'H'


def pair_split(c, up, das):
    """True if a pair of value `c` should be split vs upcard `up`."""
    if c == 11:
        return True                  # always split aces
    if c == 10:
        return False                 # never split tens
    if c == 9:
        return up in (2, 3, 4, 5, 6, 8, 9)   # stand vs 7, 10, A
    if c == 8:
        return True                  # always split eights
    if c == 7:
        return 2 <= up <= 7
    if c == 6:
        return (2 <= up <= 6) if das else (3 <= up <= 6)
    if c == 5:
        return False                 # treat as hard 10
    if c == 4:
        return (up in (5, 6)) if das else False
    if c in (2, 3):
        return (2 <= up <= 7) if das else (4 <= up <= 7)
    return False


def should_surrender(cards, up):
    if len(cards) != 2 or cards[0] == cards[1]:
        return False                 # don't surrender pairs (e.g. split 8,8)
    t, soft = total(cards)
    if soft:
        return False
    if t == 16:
        return up in (9, 10, 11)
    if t == 15:
        return up == 10
    return False


def decide(cards, up, can_double, can_split, can_surrender, rules):
    """Return one of 'H','S','D','P','R'."""
    if can_surrender and should_surrender(cards, up):
        return 'R'
    if can_split and len(cards) == 2 and cards[0] == cards[1]:
        if pair_split(cards[0], up, rules.das):
            return 'P'
    t, soft = total(cards)
    if soft:
        return soft_action(t, up, can_double)
    return hard_action(t, up, can_double)
