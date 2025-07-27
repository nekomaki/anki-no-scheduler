import math
from math import log, pi, sqrt
from typing import Optional

from fsrs.fsrs4 import DECAY, FACTOR
from longterm_knowledge.ema import GAMMA
from longterm_knowledge.ema.fsrs6 import (
    _knowledge_integral as _knowledge_integral_v6,
)


def erfcx(x):
    """M. M. Shepherd and J. G. Laframboise,
    MATHEMATICS OF COMPUTATION 36, 249 (1981)
    Note that it is reasonable to compute it in long double
    (or whatever python has)
    """
    ch_coef = [
        1.177578934567401754080e00,
        -4.590054580646477331e-03,
        -8.4249133366517915584e-02,
        5.9209939998191890498e-02,
        -2.6658668435305752277e-02,
        9.074997670705265094e-03,
        -2.413163540417608191e-03,
        4.90775836525808632e-04,
        -6.9169733025012064e-05,
        4.139027986073010e-06,
        7.74038306619849e-07,
        -2.18864010492344e-07,
        1.0764999465671e-08,
        4.521959811218e-09,
        -7.75440020883e-10,
        -6.3180883409e-11,
        2.8687950109e-11,
        1.94558685e-13,
        -9.65469675e-13,
        3.2525481e-14,
        3.3478119e-14,
        -1.864563e-15,
        -1.250795e-15,
        7.4182e-17,
        5.0681e-17,
        -2.237e-18,
        -2.187e-18,
        2.7e-20,
        9.7e-20,
        3e-21,
        -4e-21,
    ]

    K = 3.75
    y = (x - K) / (x + K)
    y2 = 2.0 * y
    d, dd = ch_coef[-1], 0.0

    for cj in ch_coef[-2:0:-1]:
        d, dd = y2 * d - dd + cj, d

    d = y * d - dd + ch_coef[0]
    return d / (1.0 + 2.0 * x)


def _knowledge_integral_v4(stability, t_begin=None, t_end=None, gamma=GAMMA):
    # g\left(x\right)=\left(1+\frac{Fx}{s}\right)^{D}r^{x}
    # -\left(\ln r\right)\int_{0}^{\infty}g\left(x\right)dx
    A = -stability / FACTOR * log(gamma)
    if t_begin is None and t_end is None:
        return sqrt(pi * A) * erfcx(sqrt(A))
    elif t_end is None and t_begin is not None:
        return sqrt(pi * A) * erfcx(sqrt(A - t_begin * log(gamma)))
    elif t_end is not None:
        if t_begin is None:
            t_begin = 0.0
        return _knowledge_integral_v4(stability, t_begin=t_begin) - GAMMA ** (
            t_end - t_begin
        ) * _knowledge_integral_v4(stability, t_begin=t_end)
    else:
        raise NotImplementedError


def _knowledge_integral_scipy(
    stability: float,
    decay: float,
    factor: Optional[float] = None,
    t_begin: Optional[float] = None,
    t_end: Optional[float] = None,
    gamma: float = GAMMA,
) -> float:
    from scipy.integrate import quad

    if stability == 0:
        return 0.0

    if factor is None:
        factor = math.pow(0.9, 1 / decay) - 1

    lgamma = -math.log(gamma)

    # default integration bounds
    if t_begin is None:
        t_begin = 0.0
    if t_end is None:
        t_end = math.inf

    def integrand(t: float) -> float:
        base = 1 + (factor * t / stability)
        return lgamma * (base**decay) * (gamma ** (t - t_begin))

    result, _ = quad(integrand, t_begin, t_end)
    return result


def test_knowledge_integral_fsrs4():
    for stability in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 36500.0]:
        knowledge_fsrs4 = _knowledge_integral_v4(
            stability=stability, t_begin=30, t_end=365, gamma=GAMMA
        )
        knowledge_fsrs6 = _knowledge_integral_v6(
            stability=stability, decay=DECAY, factor=FACTOR, t_begin=30, t_end=365, gamma=GAMMA, tol=1e-14
        )

        assert math.isclose(
            knowledge_fsrs6, knowledge_fsrs4, rel_tol=1e-9
        ), f"Knowledge EMA mismatch for stability {stability}: {knowledge_fsrs6} != {knowledge_fsrs4}"


def test_knowledge_integral_scipy():
    for decay in [-0.1, -0.5]:
        factor = 0.9 ** (1 / decay) - 1
        for stability in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 36500.0]:
            knowledge_fsrs6 = _knowledge_integral_v6(
                stability=stability, decay=decay, factor=factor, t_begin=30, t_end=365, gamma=GAMMA, tol=1e-14
            )
            knowledge_scipy = _knowledge_integral_scipy(
                stability=stability, decay=decay, factor=factor, t_begin=30, t_end=365, gamma=GAMMA
            )

            assert math.isclose(
                knowledge_fsrs6, knowledge_scipy, rel_tol=1e-9
            ), f"Knowledge EMA mismatch for stability {stability}: {knowledge_fsrs6} != {knowledge_scipy}"
