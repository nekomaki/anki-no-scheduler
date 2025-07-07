import functools
import math

from .fsrs6 import calc_knowledge as calc_knowledge_v6
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

    @functools.lru_cache(maxsize=20000)
    def fsrs_simulate_cached(
        state: State, t_review: float, retention: float | None = None
    ):
        (D, S), R = state, retention

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


def _fsrs_simulate(
    state: State, fsrs_params: tuple, t_review: float, retention: float | None = None
):
    if isinstance(fsrs_params, list):
        fsrs_params = tuple(fsrs_params)

    return _fsrs_simulate_wrapper(fsrs_params)(state, t_review, retention)


def calc_knowledge(state: State, elapsed_days: float) -> float:
    return calc_knowledge_v6(state, DECAY, elapsed_days)


def _calc_reviewed_knowledge(
    state: State, fsrs_params: tuple, elapsed_days: float
) -> float:
    next_states = _fsrs_simulate(state, fsrs_params, elapsed_days)

    knowledge = sum(
        prob * calc_knowledge(new_state, elapsed_days=0)
        for prob, new_state, _ in next_states
    )

    return knowledge


def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    current_knowledge = calc_knowledge(state, elapsed_days=elapsed_days)
    reviewed_knowledge = _calc_reviewed_knowledge(
        state, fsrs_params=fsrs_params, elapsed_days=elapsed_days
    )

    return reviewed_knowledge - current_knowledge


if __name__ == "__main__":
    state = State(1.0, 1.0)
    fsrs_params = (
        1.0191,
        8.2268,
        17.8704,
        100.0000,
        6.6634,
        0.7805,
        2.2023,
        0.0241,
        1.9304,
        0.0000,
        1.3965,
        1.7472,
        0.1247,
        0.1160,
        2.2431,
        0.4258,
        3.1303,
    )
    elapsed_days = 10

    knowledge_gain = exp_knowledge_gain(state, fsrs_params, elapsed_days)
    print(f"Expected knowledge gain: {knowledge_gain:.3f}")
