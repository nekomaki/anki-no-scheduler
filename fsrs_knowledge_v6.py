import functools
import math

from .fsrs_utils import log_gamma

GAMMA = 0.99

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

NEW_WORKLOAD = 1
FORGET_WORKLOAD = 1


def power_forgetting_curve(t, s, decay):
    if s <= 0:
        return 0.0
    factor = 0.9 ** (1 / decay) - 1
    return (1 + factor * t / s) ** decay


def knowledge_ema(
    stability, factor=None, decay=None, t_begin=None, t_end=None, gamma=GAMMA
):
    if stability == 0:
        return 0.0
    if factor is None and decay is None:
        raise ValueError("Either factor or decay must be provided")
    elif factor is None and decay is not None:
        factor = 0.9 ** (1 / decay) - 1
    elif decay is None and factor is not None:
        decay = math.log(0.9) / math.log(factor + 1)

    alpha = stability / factor
    lgamma = -math.log(gamma)

    def compute(x0, exponent):
        return math.exp(
            exponent * lgamma
            + log_gamma(decay + 1, x0)
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
        return knowledge_ema(stability, factor) - gamma**t_end * knowledge_ema(
            stability, factor, t_begin=t_end
        )
    else:
        raise NotImplementedError


@functools.cache
def _fsrs_simulate_wrapper(fsrs_params):
    w = fsrs_params

    @functools.lru_cache(maxsize=20000)
    def fsrs_simulate_cached(state, t_review, retention=None):
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
            new_difficulty = w[7] * D04 + (1 - w[7]) * (D - w[6] * (rating - 3))

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

            # new_difficulty = min(D_MAX, max(D_MIN, new_difficulty))
            new_difficulty = D
            new_stability = min(S_MAX, max(S_MIN, new_stability))

            res.append((prob, (new_difficulty, new_stability), workload))

        return res

    return fsrs_simulate_cached


def _fsrs_simulate(state, fsrs_params, t_review, retention=None):
    if isinstance(fsrs_params, list):
        fsrs_params = tuple(fsrs_params)

    return _fsrs_simulate_wrapper(fsrs_params)(state, t_review, retention)


@functools.cache
def _fsrs_simulate_with_probs_wrapper(fsrs_params, probs):
    w = fsrs_params

    @functools.lru_cache(maxsize=5000)
    def fsrs_simulate_with_probs_cached(state, t_review, retention=None):
        (D, S), R = state, retention

        if R is None:
            R = power_forgetting_curve(t_review, S, -fsrs_params[20])

        ratings = [1, 2, 3, 4]

        D04 = w[4] - math.exp(w[5] * (4 - 1)) + 1

        res = []
        for prob, rating in zip(probs, ratings):
            # Compute new difficulty
            new_difficulty = w[7] * D04 + (1 - w[7]) * (D - w[6] * (rating - 3))

            workload = 1
            if S == 0:
                # New card
                new_stability = w[rating - 1]
                workload = NEW_WORKLOAD
            elif t_review < 1:
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

            # new_difficulty = min(D_MAX, max(D_MIN, new_difficulty))
            new_difficulty = D
            new_stability = min(S_MAX, max(S_MIN, new_stability))

            res.append((prob, (new_difficulty, new_stability), workload))

        return res

    return fsrs_simulate_with_probs_cached


def _fsrs_simulate_with_probs(state, fsrs_params, t_review, probs, retention=None):
    if isinstance(fsrs_params, list):
        fsrs_params = tuple(fsrs_params)
    if isinstance(probs, list):
        probs = tuple(probs)

    return _fsrs_simulate_with_probs_wrapper(fsrs_params, probs)(
        state, t_review, retention
    )


def _compute_new_knowledge(state, fsrs_params, elapsed_days, new_rating_probs):
    decay = -fsrs_params[20]
    factor = 0.9 ** (1 / decay) - 1

    next_states = _fsrs_simulate_with_probs(
        state, fsrs_params, elapsed_days, new_rating_probs
    )

    knowledge = sum(
        prob * knowledge_ema(new_state[1], factor=factor, decay=decay)
        for prob, new_state, _ in next_states
    )

    return knowledge


def _compute_reviewed_knowledge(state, fsrs_params, elapsed_days):
    decay = -fsrs_params[20]
    factor = 0.9 ** (1 / decay) - 1

    next_states = _fsrs_simulate(state, fsrs_params, elapsed_days)

    knowledge = sum(
        prob * knowledge_ema(new_state[1], factor=factor, decay=decay)
        for prob, new_state, _ in next_states
    )

    return knowledge


def compute_current_knowledge(state, decay, elapsed_days):
    if state[1] == 0:
        return 0.0

    return knowledge_ema(state[1], decay=decay, t_begin=elapsed_days)


def exp_knowledge_gain(state, fsrs_params, elapsed_days, new_rating_probs):
    if state[1] == 0:
        return _compute_new_knowledge(
            state, fsrs_params, elapsed_days, new_rating_probs
        )

    current_knowledge = compute_current_knowledge(
        state, decay=-fsrs_params[20], elapsed_days=elapsed_days
    )
    reviewed_knowledge = _compute_reviewed_knowledge(
        state, fsrs_params=fsrs_params, elapsed_days=elapsed_days
    )

    return reviewed_knowledge - current_knowledge
