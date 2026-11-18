"""Card counting systems (balanced).

Each system assigns an integer tag to every card value (10 covers T/J/Q/K). Balanced
systems sum to zero over a full deck, so a *true count* = running_count / decks_remaining
is meaningful and comparable across systems.

Betting Correlation (BC) roughly predicts how well a system sizes bets; Playing
Efficiency (PE) predicts how well it informs deviations. Higher-level systems trade
simplicity for correlation. These are the standard published systems.
"""


class CountingSystem:
    def __init__(self, name, tags, bc, pe, scale):
        self.name = name
        self.tags = tags           # dict: value(2..11) -> int
        self.bc = bc               # betting correlation (reference)
        self.pe = pe               # playing efficiency (reference)
        self.scale = scale         # normalizer so true counts compare across systems

    def tag(self, value):
        return self.tags[value]


# value order: 2,3,4,5,6,7,8,9,10,A(=11)
def _mk(name, seq, bc, pe):
    tags = {v: t for v, t in zip([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], seq)}
    # Positive tag mass per deck (2..9 appear 4x). Hi-Lo's is 20 -> scale 1.0.
    pos = sum(max(tags[v], 0) * 4 for v in range(2, 10))
    pos += max(tags[10], 0) * 16 + max(tags[11], 0) * 4
    scale = pos / 20.0
    return CountingSystem(name, tags, bc, pe, scale)


HI_LO     = _mk("Hi-Lo",     [1, 1, 1, 1, 1, 0, 0, 0, -1, -1], 0.97, 0.51)
HI_OPT_I  = _mk("Hi-Opt I",  [0, 1, 1, 1, 1, 0, 0, 0, -1, 0],  0.88, 0.61)
HI_OPT_II = _mk("Hi-Opt II", [1, 1, 2, 2, 1, 1, 0, 0, -2, 0],  0.91, 0.67)
OMEGA_II  = _mk("Omega II",  [1, 1, 2, 2, 2, 1, 0, -1, -2, 0], 0.92, 0.67)
ZEN       = _mk("Zen",       [1, 1, 2, 2, 2, 1, 0, 0, -2, -1], 0.96, 0.63)

ALL_SYSTEMS = {s.name: s for s in [HI_LO, HI_OPT_I, HI_OPT_II, OMEGA_II, ZEN]}
