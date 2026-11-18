"""Core blackjack engine: shoe, hand math, round resolution.

Cards are represented by value only (suits are irrelevant to blackjack math):
  2..9  -> pip value
  10    -> any ten-valued card (10, J, Q, K); 16 per deck
  11    -> ace

Hi-Lo count tag: 2-6 = +1, 7-9 = 0, 10/ace = -1.
"""
import random

# Hi-Lo tags indexed by card value.
HILO = {2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0, 8: 0, 9: 0, 10: -1, 11: -1}

# One deck as (value, count) pairs.
_DECK_SPEC = ((2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4),
              (8, 4), (9, 4), (10, 16), (11, 4))


def total(cards):
    """Return (best_total, is_soft). Soft = an ace is still counted as 11."""
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


class Shoe:
    """A multi-deck shoe with a cut card and a running Hi-Lo count."""

    def __init__(self, rules, rng=None):
        self.rules = rules
        self.rng = rng or random.Random()
        self.cards = []
        self.pos = 0
        self.running_count = 0
        self.cut = 0
        self._base = []
        for v, n in _DECK_SPEC:
            self._base.extend([v] * (n * rules.decks))
        self.reshuffle()

    def reshuffle(self):
        self.cards = self._base[:]
        self.rng.shuffle(self.cards)
        self.pos = 0
        self.running_count = 0
        self.cut = int(len(self.cards) * self.rules.penetration)

    def draw(self):
        v = self.cards[self.pos]
        self.pos += 1
        self.running_count += HILO[v]
        return v

    def cards_left(self):
        return len(self.cards) - self.pos

    def needs_shuffle(self):
        return self.pos >= self.cut

    def true_count(self):
        decks_left = self.cards_left() / 52.0
        if decks_left < 0.25:        # avoid blow-up at the tail
            decks_left = 0.25
        return self.running_count / decks_left


def play_dealer(cards, draw, h17):
    """Play the dealer out and return the final total."""
    while True:
        t, soft = total(cards)
        if t < 17:
            cards.append(draw())
        elif t == 17 and soft and h17:
            cards.append(draw())
        else:
            return t


def play_round(shoe, rules, decide, bet):
    """Deal and resolve one round. `bet` is in units. Returns net units."""
    draw = shoe.draw
    player = [draw(), draw()]
    dealer_up = draw()
    dealer_hole = draw()
    dealer = [dealer_up, dealer_hole]

    player_bj = (total(player)[0] == 21)
    dealer_bj = (total(dealer)[0] == 21)

    # US-style dealer peek on a ten or ace upcard.
    if dealer_up in (10, 11) and dealer_bj:
        return 0.0 if player_bj else -bet
    if player_bj:
        return bet * rules.bj_payout

    # Resolve all player hands (handles splits/doubles/surrender).
    final = []                       # list of (cards, bet, surrendered)
    num_hands = 1
    stack = [(player, bet, 0)]       # (cards, bet, splits_in_lineage)
    while stack:
        cards, b, splits = stack.pop()
        while True:
            t, _ = total(cards)
            if t > 21:
                final.append((cards, b, False))
                break
            n = len(cards)
            is_pair = (n == 2 and cards[0] == cards[1])
            can_double = (n == 2) and (splits == 0 or rules.das)
            can_split = is_pair and (num_hands < rules.max_hands)
            can_surrender = (n == 2 and splits == 0 and rules.surrender)

            action = decide(cards, dealer_up, can_double, can_split,
                            can_surrender, rules)

            if action == 'R':
                final.append((cards, b, True))
                break
            if action == 'P':
                c = cards[0]
                num_hands += 1
                if c == 11 and not rules.resplit_aces:
                    # Split aces: exactly one card each, no further action.
                    final.append(([11, draw()], b, False))
                    final.append(([11, draw()], b, False))
                    break
                stack.append(([c, draw()], b, splits + 1))
                cards = [c, draw()]
                splits += 1
                continue
            if action == 'D':
                cards.append(draw())
                final.append((cards, b * 2, False))
                break
            if action == 'H':
                cards.append(draw())
                continue
            # 'S'
            final.append((cards, b, False))
            break

    # Dealer only plays if some player hand can still win.
    need_dealer = any((not surr) and total(c)[0] <= 21 for c, b, surr in final)
    dealer_total = play_dealer(dealer, draw, rules.h17) if need_dealer else total(dealer)[0]

    net = 0.0
    for cards, b, surr in final:
        if surr:
            net -= 0.5 * b
            continue
        pt = total(cards)[0]
        if pt > 21:
            net -= b
        elif dealer_total > 21 or pt > dealer_total:
            net += b
        elif pt < dealer_total:
            net -= b
        # equal totals push
    return net
