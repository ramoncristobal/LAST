"""Canonical multi-deck basic strategy (S17, DAS, Late Surrender).

Validated in the companion engine to produce a ~0.36% house edge. Upcard values 2..10,
and 11 for an ace.
"""


def hand_total(cards):
    t = 0
    aces = 0
    for c in cards:
        t += c
        if c == 11:
            aces += 1
    while t > 21 and aces:
        t -= 10
        aces -= 1
    return t, aces > 0


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
        return 'D' if (up <= 10 and can_double) else 'H'
    if t == 12:
        return 'S' if 4 <= up <= 6 else 'H'
    return 'S' if 2 <= up <= 6 else 'H'


def soft_action(t, up, can_double):
    if t >= 19:
        return 'S'
    if t == 18:
        if 2 <= up <= 6:
            return 'D' if can_double else 'S'
        if up in (7, 8):
            return 'S'
        return 'H'
    if t == 17:
        return 'D' if (3 <= up <= 6 and can_double) else 'H'
    if t in (15, 16):
        return 'D' if (4 <= up <= 6 and can_double) else 'H'
    return 'D' if (5 <= up <= 6 and can_double) else 'H'


def pair_split(c, up, das):
    if c == 11:
        return True
    if c == 10:
        return False
    if c == 9:
        return up in (2, 3, 4, 5, 6, 8, 9)
    if c == 8:
        return True
    if c == 7:
        return 2 <= up <= 7
    if c == 6:
        return (2 <= up <= 6) if das else (3 <= up <= 6)
    if c == 5:
        return False
    if c == 4:
        return (up in (5, 6)) if das else False
    if c in (2, 3):
        return (2 <= up <= 7) if das else (4 <= up <= 7)
    return False


def should_surrender(cards, up):
    if len(cards) != 2 or cards[0] == cards[1]:
        return False
    t, soft = hand_total(cards)
    if soft:
        return False
    if t == 16:
        return up in (9, 10, 11)
    if t == 15:
        return up == 10
    return False


def basic_decide(cards, up, can_double, can_split, can_surrender, rules):
    if can_surrender and should_surrender(cards, up):
        return 'R'
    if can_split and len(cards) == 2 and cards[0] == cards[1]:
        if pair_split(cards[0], up, rules.das):
            return 'P'
    t, soft = hand_total(cards)
    if soft:
        return soft_action(t, up, can_double)
    return hard_action(t, up, can_double)
