"""Configurable blackjack rule set."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Rules:
    decks: int = 6
    h17: bool = False            # dealer Hits Soft 17 (False = Stands on Soft 17)
    das: bool = True             # Double After Split allowed
    surrender: bool = True       # Late Surrender allowed
    bj_payout: float = 1.5       # 3:2. Set 1.2 for the awful 6:5 tables.
    max_hands: int = 4           # max hands from splitting (3 resplits)
    resplit_aces: bool = False
    penetration: float = 0.75    # fraction of shoe dealt before the cut card

    def label(self) -> str:
        return (
            f"{self.decks}D_"
            f"{'H17' if self.h17 else 'S17'}_"
            f"DAS{int(self.das)}_"
            f"LS{int(self.surrender)}_"
            f"BJ{self.bj_payout}_"
            f"pen{self.penetration}"
        )
