import math
from functools import cache
from typing import Optional

from . import FSRS
from .types import State

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500


class FSRS6(FSRS):
    EXPECTED_LENGTH = 21
    VERSION = 6

    def __init__(self, params: tuple[float, ...]):
        super().__init__(params=params)
        self._decay = -params[20]
        self._factor = 0.9 ** (1 / self._decay) - 1

    @property
    def decay(self) -> float:
        return self._decay

    @property
    def factor(self) -> float:
        return self._factor

    def power_forgetting_curve(self, t: float, s: float) -> float:
        return (1 + self._factor * t / s) ** self._decay

    def interval_from_retention(self, state: State, retention: float) -> float:
        alpha = (retention ** (1 / self._decay) - 1) / self._factor
        interval = state.stability * alpha

        return interval

    @cache
    def simulate(
        self,
        state: State,
        t_review: float,
    ) -> list[tuple[float, State]]:
        w = self.params
        D, S = state.difficulty, state.stability
        R = self.power_forgetting_curve(t_review, S)

        # We only consider two outcomes
        ratings = [1, 3]
        probs = [1 - R, R]
        D04 = w[4] - math.exp(w[5] * (4 - 1)) + 1

        res = []
        for prob, rating in zip(probs, ratings):
            # Compute new difficulty
            delta_difficulty = -w[6] * (rating - 3)
            difficulty_prime = D + delta_difficulty * (10 - D) / 9
            new_difficulty = w[7] * D04 + (1 - w[7]) * difficulty_prime

            if t_review < 1:
                new_stability = (
                    S * math.exp(w[17] * (rating - 3 + w[18])) * S ** (-w[19])
                )
            else:
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
