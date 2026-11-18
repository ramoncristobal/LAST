"""Strategy interface + implementations.

A Strategy decides, using ONLY information available at decision time (cards on the table
and the running count of cards already seen), how much to bet and how to play. Add a new
idea by subclassing Strategy or constructing a CardCounter with new parameters.

True counts are normalized by the counting system's scale so every system is ramped on the
same footing (see counting.py).
"""
from .basic_strategy import basic_decide
from .deviations import hilo_deviation, take_insurance
from .counting import HI_LO, HI_OPT_I, HI_OPT_II, OMEGA_II, ZEN


class Strategy:
    name = "base"

    def __init__(self, counting=None):
        self.counting = counting
        self.rc = 0

    def start_shoe(self, decks):
        self.rc = 0

    def observe(self, card):
        if self.counting is not None:
            self.rc += self.counting.tag(card)

    def true_count(self, decks_left):
        if self.counting is None:
            return 0.0
        dl = decks_left if decks_left > 0.25 else 0.25
        return (self.rc / self.counting.scale) / dl

    def bet(self, decks_left):
        return 1.0

    def insurance(self, decks_left):
        return False

    def play(self, cards, up, decks_left, can_double, can_split, can_surrender, rules):
        return basic_decide(cards, up, can_double, can_split, can_surrender, rules)


class FlatBasic(Strategy):
    def __init__(self):
        super().__init__(counting=None)
        self.name = "Flat Basic (baseline)"


class CardCounter(Strategy):
    """Counting + bet ramp. Optional Hi-Lo deviations and Wong-out."""

    def __init__(self, name, counting, ramp, use_deviations=False,
                 wong_out=None, base=1.0, max_bet=None):
        super().__init__(counting=counting)
        self.name = name
        self.ramp = ramp                 # list of (normalized_tc_threshold, units)
        self.use_deviations = use_deviations
        self.wong_out = wong_out
        self.base = base
        self.max_bet = max_bet

    def bet(self, decks_left):
        tc = self.true_count(decks_left)
        if self.wong_out is not None and tc < self.wong_out:
            return 0.0
        units = self.base
        for thr, u in self.ramp:
            if tc >= thr:
                units = u
        if self.max_bet is not None:
            units = min(units, self.max_bet)
        return units

    def insurance(self, decks_left):
        return take_insurance(self.true_count(decks_left))

    def play(self, cards, up, decks_left, can_double, can_split, can_surrender, rules):
        if self.use_deviations:
            tc = self.true_count(decks_left)
            dev = hilo_deviation(cards, up, tc, can_double, rules)
            if dev is not None:
                # A deviation can override surrender; only return legal actions.
                if dev == 'D' and not can_double:
                    dev = 'H'
                if dev == 'P' and not can_split:
                    dev = None
                if dev is not None:
                    return dev
        return basic_decide(cards, up, can_double, can_split, can_surrender, rules)


# --- Standard bet ramps (normalized true count -> units) ---
SPREAD_1_12 = [(1, 1), (2, 2), (3, 4), (4, 8), (5, 12)]
SPREAD_1_6 = [(1, 1), (2, 2), (3, 3), (4, 5), (5, 6)]
SPREAD_1_20 = [(1, 1), (2, 4), (3, 8), (4, 14), (5, 20)]


def default_roster():
    """The strategies compared by default. Extend freely."""
    return [
        FlatBasic(),
        CardCounter("Hi-Lo 1-12", HI_LO, SPREAD_1_12),
        CardCounter("Hi-Lo 1-12 + I18", HI_LO, SPREAD_1_12, use_deviations=True),
        CardCounter("Hi-Lo 1-12 + I18 + Wong", HI_LO, SPREAD_1_12,
                    use_deviations=True, wong_out=0.0),
        CardCounter("Hi-Lo 1-6 (low variance)", HI_LO, SPREAD_1_6),
        CardCounter("Hi-Opt II 1-12", HI_OPT_II, SPREAD_1_12),
        CardCounter("Omega II 1-12", OMEGA_II, SPREAD_1_12),
        CardCounter("Zen 1-12", ZEN, SPREAD_1_12),
    ]
