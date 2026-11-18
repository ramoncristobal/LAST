"""Core engine: deal a fixed shoe and play it out under a given strategy.

Shoes are pre-shuffled fixed lists so the tournament can replay the SAME shoe for every
strategy (common random numbers), giving a fair per-shoe comparison.

Card values: 2..9 pip, 10 = any ten-valued card (16/deck), 11 = ace.
"""
from .basic_strategy import hand_total, basic_decide

_DECK_SPEC = ((2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4),
              (8, 4), (9, 4), (10, 16), (11, 4))

# Minimum cards left to safely deal one more round (worst-case splits/hits).
_MIN_TAIL = 30


def make_shoe(rules, rng):
    cards = []
    for v, n in _DECK_SPEC:
        cards.extend([v] * (n * rules.decks))
    rng.shuffle(cards)
    cut = int(len(cards) * rules.penetration)
    return cards, cut


class ShoeDealer:
    __slots__ = ("cards", "pos")

    def __init__(self, cards):
        self.cards = cards
        self.pos = 0

    def draw(self):
        v = self.cards[self.pos]
        self.pos += 1
        return v

    def left(self):
        return len(self.cards) - self.pos


def _play_dealer(cards, draw, h17, dealt):
    while True:
        t, soft = hand_total(cards)
        if t < 17 or (t == 17 and soft and h17):
            c = draw()
            cards.append(c)
            dealt.append(c)
        else:
            return t


def play_round(dealer, rules, decide, bet, insurance, dealt):
    """Deal and resolve one round. Returns (net_units, wagered_units).

    `decide(cards, up, can_double, can_split, can_surrender)` -> action.
    `insurance` is a bool (offered only on an ace upcard).
    Every dealt card is appended to `dealt` so the caller can update the count after.
    """
    draw = dealer.draw
    net = 0.0
    wagered = bet

    player = [draw(), draw()]
    dealer_up = draw()
    dealer_hole = draw()
    dealt.extend(player)
    dealt.append(dealer_up)
    dealt.append(dealer_hole)
    dh = [dealer_up, dealer_hole]

    player_bj = (hand_total(player)[0] == 21)
    dealer_bj = (hand_total(dh)[0] == 21)

    # Insurance side bet (only meaningful on an ace upcard).
    if dealer_up == 11 and insurance:
        ins = 0.5 * bet
        wagered += ins
        net += (ins * 2) if dealer_bj else (-ins)

    if dealer_up in (10, 11) and dealer_bj:
        net += 0.0 if player_bj else -bet
        return net, wagered
    if player_bj:
        net += bet * rules.bj_payout
        return net, wagered

    final = []
    num_hands = 1
    stack = [(player, bet, 0)]
    while stack:
        cards, b, splits = stack.pop()
        while True:
            t, _ = hand_total(cards)
            if t > 21:
                final.append((cards, b, False))
                break
            n = len(cards)
            is_pair = (n == 2 and cards[0] == cards[1])
            can_double = (n == 2) and (splits == 0 or rules.das)
            can_split = is_pair and (num_hands < rules.max_hands)
            can_surrender = (n == 2 and splits == 0 and rules.surrender)
            action = decide(cards, dealer_up, can_double, can_split, can_surrender)

            if action == 'R':
                final.append((cards, b, True))
                break
            if action == 'P':
                c = cards[0]
                num_hands += 1
                if c == 11 and not rules.resplit_aces:
                    c1, c2 = draw(), draw()
                    dealt.append(c1)
                    dealt.append(c2)
                    final.append(([11, c1], b, False))
                    final.append(([11, c2], b, False))
                    wagered += b
                    break
                c1 = draw()
                c2 = draw()
                dealt.append(c1)
                dealt.append(c2)
                wagered += b
                stack.append(([c, c1], b, splits + 1))
                cards = [c, c2]
                splits += 1
                continue
            if action == 'D':
                c = draw()
                cards.append(c)
                dealt.append(c)
                wagered += b
                final.append((cards, b * 2, False))
                break
            if action == 'H':
                c = draw()
                cards.append(c)
                dealt.append(c)
                continue
            final.append((cards, b, False))  # 'S'
            break

    need_dealer = any((not surr) and hand_total(c)[0] <= 21 for c, b, surr in final)
    dealer_total = (_play_dealer(dh, draw, rules.h17, dealt)
                    if need_dealer else hand_total(dh)[0])

    for cards, b, surr in final:
        if surr:
            net -= 0.5 * b
            continue
        pt = hand_total(cards)[0]
        if pt > 21:
            net -= b
        elif dealer_total > 21 or pt > dealer_total:
            net += b
        elif pt < dealer_total:
            net -= b
    return net, wagered


def play_shoe(cards, cut, rules, strategy):
    """Play one fixed shoe under `strategy`. Returns a per-shoe stats dict."""
    dealer = ShoeDealer(cards)
    strategy.start_shoe(rules.decks)
    net = 0.0
    wagered = 0.0
    sum_sq = 0.0            # sum of per-round net^2 (for per-hand variance)
    hands_played = 0

    while dealer.pos < cut and dealer.left() >= _MIN_TAIL:
        decks_left = dealer.left() / 52.0
        bet = strategy.bet(decks_left)
        dealt = []
        if bet <= 0:
            # Wong-out: watch the table. Advance/observe a basic-play round, wager nothing.
            play_round(dealer, rules,
                       lambda c, u, cd, cs, cr: basic_decide(c, u, cd, cs, cr, rules),
                       0.0, False, dealt)
        else:
            ins = strategy.insurance(decks_left)
            n, w = play_round(
                dealer, rules,
                lambda c, u, cd, cs, cr: strategy.play(c, u, decks_left, cd, cs, cr, rules),
                bet, ins, dealt)
            net += n
            wagered += w
            sum_sq += n * n
            hands_played += 1
        obs = strategy.observe
        for c in dealt:
            obs(c)

    return {"net": net, "wagered": wagered, "sum_sq": sum_sq, "hands": hands_played}
