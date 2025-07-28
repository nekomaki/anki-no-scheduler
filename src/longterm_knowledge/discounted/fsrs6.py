import math
from functools import cache
from typing import Optional

try:
    from ...fsrs.fsrs6 import FSRS6
    from ...fsrs.types import State
except ImportError:
    from fsrs.fsrs6 import FSRS6
    from fsrs.types import State

from . import GAMMA, TOL
from .interfaces import KnowledgeDiscountedMixin
from .utils import log_upper_gamma


def _knowledge_integral(
    stability: float,
    decay: float,
    factor: float,
    t_begin: Optional[float] = None,
    t_end: Optional[float] = None,
    gamma: float = GAMMA,
    tol: float = TOL,
):
    if stability == 0:
        return 0.0

    alpha = stability / factor
    lgamma = -math.log(gamma)

    def compute(x0, exponent):
        return math.exp(
            exponent * lgamma
            + log_upper_gamma(decay + 1, x0, tol=tol)
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
        x0 = (alpha + t_begin) * lgamma
        return compute(x0, alpha + t_begin) - gamma ** (t_end - t_begin) * compute(
            (alpha + t_end) * lgamma, alpha + t_end
        )
    else:
        raise NotImplementedError


@cache
def _calc_knowledge_cached(
    stability: float, decay: float, factor: float, elapsed_days: float
) -> float:
    return _knowledge_integral(
        stability, decay=decay, factor=factor, t_begin=elapsed_days
    )


class FSRS6KnowledgeDiscounted(KnowledgeDiscountedMixin, FSRS6):
    def calc_knowledge(self, state: State, elapsed_days: float) -> float:
        return _calc_knowledge_cached(
            state.stability,
            decay=self.decay,
            factor=self.factor,
            elapsed_days=elapsed_days,
        )


if __name__ == "__main__":
    state = State(difficulty=10.0, stability=0.01)
    elapsed_days = 30

    import time

    tic = time.time()

    for i in range(1000):
        fsrs = FSRS6KnowledgeDiscounted.from_list(
            [
                0.8457,
                8.1627,
                17.1531,
                100.0000,
                6.2004,
                0.8907,
                3.0530,
                0.0282,
                2.3039,
                0.0302,
                1.2036,
                1.3832,
                0.0883,
                0.1358,
                1.5999,
                0.5648,
                2.2040,
                0.7055,
                0.1141,
                0.0916,
                0.1000,
            ]
        )
        retrivibility = fsrs.power_forgetting_curve(elapsed_days, state.stability)
        knowledge_gain = fsrs.exp_knowledge_gain_future(state, i)
    print(f"Expected knowledge gain: {knowledge_gain}")
    print(f"Retrievability: {retrivibility}")

    toc = time.time()
    print(f"Time taken: {toc - tic:.4f} seconds")
