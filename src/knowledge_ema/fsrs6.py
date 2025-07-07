import functools
import math

from .types import State
from .utils import log_upper_incomplete_gamma

GAMMA = 0.99

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

NEW_WORKLOAD = 1
FORGET_WORKLOAD = 1


def power_forgetting_curve(t: float, s: float, decay: float) -> float:
    factor = math.pow(0.9, 1 / decay) - 1
    return (1 + factor * t / s) ** decay


def knowledge_ema(
    stability: float,
    decay: float,
    factor: float | None = None,
    t_begin: float | None = None,
    t_end: float | None = None,
    gamma: float = GAMMA,
):
    if stability == 0:
        return 0.0

    if factor is None:
        factor = math.pow(0.9, 1 / decay) - 1

    alpha = stability / factor
    lgamma = -math.log(gamma)

    def compute(x0, exponent):
        return math.exp(
            exponent * lgamma
            + log_upper_incomplete_gamma(decay + 1, x0)
            - decay * (math.log(alpha) + math.log(lgamma))
        )

    # Case 1: full integral from 0 to ∞
    if t_begin is None and t_end is None:
        x0 = alpha * lgamma
        return compute(x0, alpha)

    # Case 2: integral from t_begin to ∞
    elif t_end is None and t_begin is not None:
        x0 = (alpha + t_begin) * lgamma
        return compute(x0, alpha + t_begin)

    # Case 3: integral from 0 to t_end
    elif t_begin is None and t_end is not None:
        return knowledge_ema(
            stability, decay=decay, factor=factor
        ) - gamma**t_end * knowledge_ema(
            stability, decay=decay, factor=factor, t_begin=t_end
        )
    else:
        return knowledge_ema(
            stability, decay=decay, factor=factor, t_end=t_end
        ) - gamma**t_begin * knowledge_ema(
            stability, decay=decay, factor=factor, t_begin=t_begin
        )


@functools.cache
def _fsrs_simulate_wrapper(fsrs_params: tuple):
    w = fsrs_params

    @functools.lru_cache(maxsize=20000)
    def fsrs_simulate_cached(
        state: State, t_review: float, retention: float | None = None
    ):
        (D, S), R = state, retention

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

            workload = 1
            if t_review < 1:
                # Same day review
                new_stability = (
                    S * math.exp(w[17] * (rating - 3 + w[18])) * S ** (-w[19])
                )
                workload = FORGET_WORKLOAD
            else:
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
            # new_difficulty = D
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


# @functools.cache
# def _fsrs_simulate_with_probs_wrapper(fsrs_params, probs):
#     w = fsrs_params

#     @functools.lru_cache(maxsize=5000)
#     def fsrs_simulate_with_probs_cached(state, t_review, retention=None):
#         (D, S), R = state, retention

#         if R is None:
#             R = power_forgetting_curve(t_review, S, -fsrs_params[20])

#         ratings = [1, 2, 3, 4]

#         D04 = w[4] - math.exp(w[5] * (4 - 1)) + 1

#         res = []
#         for prob, rating in zip(probs, ratings):
#             # Compute new difficulty
#             new_difficulty = w[7] * D04 + (1 - w[7]) * (D - w[6] * (rating - 3))

#             workload = 1
#             if S == 0:
#                 # New card
#                 new_stability = w[rating - 1]
#                 workload = NEW_WORKLOAD
#             elif t_review < 1:
#                 # Same day review
#                 new_stability = (
#                     S * math.exp(w[17] * (rating - 3 + w[18])) * S ** (-w[19])
#                 )
#                 workload = FORGET_WORKLOAD
#             else:
#                 if rating == 1:
#                     # Forget
#                     new_stability = (
#                         w[11]
#                         * (D ** -w[12])
#                         * ((S + 1) ** w[13] - 1)
#                         * math.exp(w[14] * (1 - R))
#                     )
#                     workload = FORGET_WORKLOAD
#                 else:
#                     new_stability = S * (
#                         math.exp(w[8])
#                         * (11 - D)
#                         * S ** (-w[9])
#                         * (math.exp(w[10] * (1 - R)) - 1)
#                         * (w[15] if rating == 2 else 1)
#                         * (w[16] if rating == 4 else 1)
#                         + 1
#                     )

#             new_difficulty = min(D_MAX, max(D_MIN, new_difficulty))
#             # new_difficulty = D
#             new_stability = min(S_MAX, max(S_MIN, new_stability))

#             res.append((prob, (new_difficulty, new_stability), workload))

#         return res

#     return fsrs_simulate_with_probs_cached


# def _fsrs_simulate_with_probs(state, fsrs_params, t_review, probs, retention=None):
#     if isinstance(fsrs_params, list):
#         fsrs_params = tuple(fsrs_params)
#     if isinstance(probs, list):
#         probs = tuple(probs)

#     return _fsrs_simulate_with_probs_wrapper(fsrs_params, probs)(
#         state, t_review, retention
#     )


# def _calc_new_knowledge(state, fsrs_params, elapsed_days, new_rating_probs):
#     decay = -fsrs_params[20]
#     factor = 0.9 ** (1 / decay) - 1

#     next_states = _fsrs_simulate_with_probs(
#         state, fsrs_params, elapsed_days, new_rating_probs
#     )

#     knowledge = sum(
#         prob * knowledge_ema(new_state[1], factor=factor, decay=decay)
#         for prob, new_state, _ in next_states
#     )

#     return knowledge


def _calc_reviewed_knowledge(state: State, fsrs_params: tuple, elapsed_days: float):
    decay = -fsrs_params[20]

    next_states = _fsrs_simulate(state, fsrs_params, elapsed_days)

    knowledge = sum(
        prob * knowledge_ema(new_state.stability, decay=decay)
        for prob, new_state, _ in next_states
    )
    for prob, new_state, _ in next_states:
        print(prob, new_state, knowledge_ema(new_state.stability, decay=decay))

    return knowledge


def calc_current_knowledge(state: State, decay: float, elapsed_days: float) -> float:
    return knowledge_ema(
        state.stability, decay=decay, t_begin=elapsed_days
    )  # * GAMMA ** elapsed_days


def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    current_knowledge = calc_current_knowledge(
        state, decay=-fsrs_params[20], elapsed_days=elapsed_days
    )
    reviewed_knowledge = _calc_reviewed_knowledge(
        state, fsrs_params=fsrs_params, elapsed_days=elapsed_days
    )

    return reviewed_knowledge - current_knowledge


if __name__ == "__main__":
    state = State(10.0, 0.01)
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
        0.9678,
        0.2470,
        0.1150,
        0.1000,
    )
    elapsed_days = 10

    knowledge_gain = exp_knowledge_gain(state, fsrs_params, elapsed_days)
    print(f"Expected knowledge gain: {knowledge_gain:.3f}")
