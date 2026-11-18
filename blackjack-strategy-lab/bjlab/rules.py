"""Configurable blackjack rule set."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Rules:
    decks: int = 6
    h17: bool = False            # dealer Hits Soft 17 (False = Stands)
    das: bool = True             # Double After Split
    surrender: bool = True       # Late Surrender
    bj_payout: float = 1.5       # 3:2 (use 1.2 for 6:5 tables)
    max_hands: int = 4
    resplit_aces: bool = False
    penetration: float = 0.75    # fraction dealt before the cut card

    def label(self) -> str:
        return (f"{self.decks}D_{'H17' if self.h17 else 'S17'}_"
                f"DAS{int(self.das)}_LS{int(self.surrender)}_"
                f"BJ{self.bj_payout}_pen{self.penetration}")
