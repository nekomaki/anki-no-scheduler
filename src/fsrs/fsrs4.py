import math
from functools import cache
from typing import Optional

from . import FSRS
from .types import State

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

DECAY = -0.5
FACTOR = 0.9 ** (1 / DECAY) - 1


class FSRS4(FSRS):
    EXPECTED_LENGTH = 17
    VERSION = 4

    def __init__(self, params: tuple[float, ...]):
        super().__init__(params=params)

    @property
    def decay(self) -> float:
        return DECAY

    @property
    def factor(self) -> float:
        return FACTOR

    @classmethod
    def power_forgetting_curve(cls, t: float, s: float) -> float:
        return (1 + FACTOR * t / s) ** DECAY

    @classmethod
    def interval_from_retention(cls, state: State, retention: float) -> float:
        alpha = (retention ** (1 / DECAY) - 1) / FACTOR
        interval = state.stability * alpha
        return interval

    @cache
    def simulate(
        self,
        state: State,
        t_review: float,
        retention: Optional[float] = None,
    ) -> list[tuple[float, State]]:
        w = self.params
        (D, S), R = (state.difficulty, state.stability), retention

        if R is None:
            R = self.power_forgetting_curve(t_review, S)

        # We only consider two outcomes
        ratings = [1, 3]
        probs = [1 - R, R]
        D03 = w[4]

        res = []
        for prob, rating in zip(probs, ratings):
            # Compute new difficulty
            new_difficulty = w[7] * D03 + (1 - w[7]) * (D - w[6] * (rating - 3))

            if rating == 1:
                # Forget
                new_stability = (
                    w[11]
                    * (D ** -w[12])
                    * ((S + 1) ** w[13] - 1)
                    * math.exp(w[14] * (1 - R))
                )
            else:
                new_stability = S * (
                    math.exp(w[8])
                    * (11 - D)
                    * S ** (-w[9])
                    * (math.exp(w[10] * (1 - R)) - 1)
                    * (w[15] if rating == 2 else 1)
                    * (w[16] if rating == 4 else 1)
                    + 1
                )

            new_difficulty = min(D_MAX, max(D_MIN, new_difficulty))
            new_stability = min(S_MAX, max(S_MIN, new_stability))

            res.append((prob, State(new_difficulty, new_stability)))

        return res
