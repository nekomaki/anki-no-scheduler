import functools
import math
from typing import Optional

from .types import State

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

NEW_WORKLOAD = 1
FORGET_WORKLOAD = 1

DECAY = -0.5
FACTOR = 0.9 ** (1 / DECAY) - 1


def power_forgetting_curve(t: float, s: float) -> float:
    return (1 + FACTOR * t / s) ** DECAY


@functools.cache
def _fsrs_simulate_wrapper(fsrs_params: tuple):
    w = fsrs_params

    @functools.cache
    def fsrs_simulate_cached(
        state: State, t_review: float, retention: Optional[float] = None
    ):
        (D, S), R = (state.difficulty, state.stability), retention

        if R is None:
            R = power_forgetting_curve(t_review, S)

        # We only consider two outcomes
        ratings = [1, 3]
        probs = [1 - R, R]
        D03 = w[4]

        res = []
        for prob, rating in zip(probs, ratings):
            # Compute new difficulty
            new_difficulty = w[7] * D03 + (1 - w[7]) * (D - w[6] * (rating - 3))

            workload = 1
            if rating == 1:
                # Forget
                new_stability = (
                    w[11]
                    * (D ** -w[12])
                    * ((S + 1) ** w[13] - 1)
                    * math.exp(w[14] * (1 - R))
                )
                workload = FORGET_WORKLOAD
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

            res.append((prob, State(new_difficulty, new_stability), workload))

        return res

    return fsrs_simulate_cached


def fsrs_simulate(
    state: State, fsrs_params: tuple, t_review: float, retention: Optional[float] = None
):
    return _fsrs_simulate_wrapper(fsrs_params)(state, t_review, retention)
