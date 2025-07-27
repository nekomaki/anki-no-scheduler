import math
from functools import cache
from typing import TYPE_CHECKING, Optional

try:
    from ...fsrs.fsrs6 import FSRS6
    from ...fsrs.types import State
    from ..knowledge import KnowledgeMixin
except ImportError:
    from fsrs.fsrs6 import FSRS6
    from fsrs.types import State
    from longterm_knowledge.knowledge import  KnowledgeMixin

from . import GAMMA

if TYPE_CHECKING:

    class _FSRS6(FSRS6):
        pass

else:
    _FSRS6 = FSRS6

# from . import GAMMA
from .utils import log_upper_gamma

D_MIN, D_MAX = 1, 10
S_MIN, S_MAX = 0.01, 36500

TOL = 1e-5


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


class FSRS6Knowledge(KnowledgeMixin, _FSRS6):
    def calc_knowledge(self, state: State, elapsed_days: float) -> float:
        return _calc_knowledge_cached(
            state.stability,
            decay=self.decay,
            factor=self.factor,
            elapsed_days=elapsed_days,
        )


if __name__ == "__main__":
    state = State(difficulty=10.0, stability=3.0)
    elapsed_days = 1

    import time

    tic = time.time()

    for i in range(100000):
        fsrs = FSRS6Knowledge.from_list(
            [
                0.0287,
                0.2781,
                4.5604,
                49.4121,
                6.4429,
                0.7331,
                3.0339,
                0.0010,
                1.8213,
                0.1312,
                0.7468,
                1.3651,
                0.1602,
                0.1411,
                1.5397,
                0.5035,
                1.9940,
                0.5862,
                0.1305,
                0.1015,
                0.2263,
            ]
        )
        knowledge_gain = fsrs.exp_knowledge_gain_future(state, elapsed_days)
    print(f"Expected knowledge gain: {knowledge_gain}")

    toc = time.time()
    print(f"Time taken: {toc - tic:.4f} seconds")
