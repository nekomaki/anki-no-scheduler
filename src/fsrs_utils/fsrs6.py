import functools
import math

from .types import State

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

FORGET_WORKLOAD = 1


def power_forgetting_curve(t: float, s: float, decay: float) -> float:
    factor = math.pow(0.9, 1 / decay) - 1
    return math.pow(1 + factor * t / s, decay)


def interval_from_retention(state: State, retention: float, decay: float) -> float:
    factor = math.pow(0.9, 1 / decay) - 1
    alpha = (retention ** (1 / decay) - 1) / factor
    interval = state.stability * alpha
    interval = state.stability * alpha

    return interval


@functools.cache
def _fsrs_simulate_wrapper(fsrs_params: tuple):
    w = fsrs_params

    @functools.cache
    def _fsrs_simulate_cached(
        state: State, t_review: float, retention: float | None = None
    ):
        (D, S), R = (state.difficulty, state.stability), retention

        if R is None:
            R = power_forgetting_curve(t_review, S, -fsrs_params[20])

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

            workload = 1 if rating > 1 else FORGET_WORKLOAD

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

            res.append((prob, State(new_difficulty, new_stability), workload))

        return res

    return _fsrs_simulate_cached


def fsrs_simulate(
    state: State, fsrs_params: tuple, t_review: float, retention: float | None = None
):
    return _fsrs_simulate_wrapper(fsrs_params)(state, t_review, retention)
