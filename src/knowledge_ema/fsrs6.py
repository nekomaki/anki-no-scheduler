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
from .utils import log_upper_gamma

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

NEW_WORKLOAD = 1
FORGET_WORKLOAD = 1


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
            + log_upper_gamma(decay + 1, x0)
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
        prob * calc_knowledge(new_state, decay=decay, elapsed_days=0)
        for prob, new_state, _ in next_states
    )

    return knowledge


def exp_knowledge_gain(state: State, fsrs_params: tuple, elapsed_days: float) -> float:
    current_knowledge = calc_knowledge(
        state, decay=-fsrs_params[20], elapsed_days=elapsed_days
    )
    reviewed_knowledge = _calc_reviewed_knowledge(
        state, fsrs_params=fsrs_params, elapsed_days=elapsed_days
    )

    return reviewed_knowledge - current_knowledge


if __name__ == "__main__":
    state = State(10.0, 0.01)
    fsrs_params = (
        0.8065,
        8.1580,
        17.1604,
        100.0000,
        6.1813,
        0.8775,
        3.0892,
        0.0223,
        2.2848,
        0.0126,
        1.1841,
        1.3679,
        0.0827,
        0.1116,
        1.4900,
        0.5721,
        2.1657,
        0.7048,
        0.1296,
        0.1008,
        0.1000,
    )
    elapsed_days = 0

    knowledge_gain = exp_knowledge_gain(state, fsrs_params, elapsed_days)
    print(f"Expected knowledge gain: {knowledge_gain:.3f}")
