import functools
import math
from typing import Optional

try:
    from ..fsrs_utils.fsrs6 import fsrs_simulate
    from ..fsrs_utils.types import State
except ImportError:
    from fsrs_utils.fsrs6 import fsrs_simulate
    from fsrs_utils.types import State

from . import GAMMA
from .future_estimator import exp_knowledge_gain_future_greedy
from .utils import log_upper_gamma

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

EPS = 1e-5


def _knowledge_integral(
    stability: float,
    decay: float,
    factor: Optional[float] = None,
    t_begin: Optional[float] = None,
    t_end: Optional[float] = None,
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
            + log_upper_gamma(decay + 1, x0, tol=EPS)
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
    elif t_end is not None:
        if t_begin is None:
            t_begin = 0.0
        return _knowledge_integral(
            stability, decay=decay, factor=factor, t_begin=t_begin
        ) - math.pow(gamma, (t_end - t_begin)) * _knowledge_integral(
            stability, decay=decay, factor=factor, t_begin=t_end
        )
    else:
        raise NotImplementedError


@functools.cache
def _calc_knowledge_cached(
    stability: float, decay: float, elapsed_days: float
) -> float:
    return _knowledge_integral(stability, decay=decay, t_begin=elapsed_days)


def calc_knowledge(state: State, decay: float, elapsed_days: float) -> float:
    return _calc_knowledge_cached(
        state.stability, decay=decay, elapsed_days=elapsed_days
    )


def _calc_reviewed_knowledge(state: State, fsrs_params: tuple, elapsed_days: float):
    decay = -fsrs_params[20]

    next_states = fsrs_simulate(state, fsrs_params, elapsed_days)

    knowledge = sum(
        prob * calc_knowledge(next_state, decay=decay, elapsed_days=0)
        for prob, next_state in next_states
    )

    return knowledge


@functools.cache
def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    current_knowledge = calc_knowledge(
        state, decay=-fsrs_params[20], elapsed_days=elapsed_days
    )
    reviewed_knowledge = _calc_reviewed_knowledge(
        state, fsrs_params=fsrs_params, elapsed_days=elapsed_days
    )

    return reviewed_knowledge - current_knowledge


# @functools.cache
def exp_knowledge_gain_future(
    state: State, fsrs_params: tuple, elapsed_days: float
) -> float:
    return exp_knowledge_gain_future_greedy(
        state, fsrs_params, elapsed_days, fsrs_simulate, exp_knowledge_gain
    )


if __name__ == "__main__":
    state = State(10.0, 0.03)
    fsrs_params = (
        0.0212,
        0.2849,
        3.1533,
        24.4448,
        6.4748,
        0.7424,
        3.1032,
        0.0010,
        1.8021,
        0.1157,
        0.7286,
        1.3906,
        0.1507,
        0.1679,
        1.5564,
        0.5314,
        1.8290,
        0.5890,
        0.1003,
        0.0765,
        0.1895,
    )
    elapsed_days = 10

    import time

    tic = time.time()

    for i in range(100000):
        knowledge_gain_future = exp_knowledge_gain_future(
            state, fsrs_params, elapsed_days
        )
    print(f"Expected knowledge gain future: {knowledge_gain_future}")

    toc = time.time()
    print(f"Time taken: {toc - tic:.4f} seconds")

    tic = time.time()

    for i in range(100000):
        knowledge_gain = exp_knowledge_gain(state, fsrs_params, elapsed_days)
    print(f"Expected knowledge gain: {knowledge_gain}")

    toc = time.time()
    print(f"Time taken: {toc - tic:.4f} seconds")
