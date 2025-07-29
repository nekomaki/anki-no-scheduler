import math
from typing import Optional


def lower_gamma_series(a: float, x: float, max_iter=200, tol=1e-14) -> float:
    """
    Compute lower incomplete gamma γ(a, x) via series:
    γ(a, x) = x^a e^{-x} * sum_{k=0}∞ x^k / [a(a+1)...(a+k)]
    """
    if not (a > 0 and x >= 0):
        raise ValueError("Requires a > 0 and x >= 0")

    term = 1.0 / a
    total = term
    for k in range(1, max_iter):
        term *= x / (a + k)
        total += term
        if abs(term) < tol * abs(total):
            break

    return total * math.exp(-x + a * math.log(x))


def log_upper_gamma_cf(a: float, x: float, max_iter=200, tol=1e-14) -> float:
    """
    Computes log(Γ(a, x)) using continued fraction (Lentz's method).
    Only used when x >= a + 1.
    """
    tiny = 1e-300
    b0 = x + 1.0 - a
    C = b0 if b0 != 0 else tiny
    D = 0.0
    f = C

    for n in range(1, max_iter + 1):
        an = -n * (n - a)
        b = x + 2 * n + 1 - a

        D = b + an * D
        if abs(D) < tiny:
            D = tiny
        C = b + an / C
        if abs(C) < tiny:
            C = tiny

        D = 1.0 / D
        delta = C * D
        f *= delta

        if abs(delta - 1.0) < tol:
            break

    log_Q = -x + a * math.log(x) - math.lgamma(a) - math.log(f)
    return log_Q + math.lgamma(a)


def log_upper_gamma(a: float, x: float, max_iter=200, tol=1e-14) -> float:
    """
    Computes log(Γ(a, x)) for a > 0 and x > 0.
    Automatically chooses between series and continued fraction based on x.
    Reference: https://www.foo.be/docs-free/Numerical_Recipe_In_C/c6-2.pdf
    """
    if not (a > 0 and x > 0):
        raise ValueError("Requires a > 0 and x > 0")

    if x < a + 1:
        P = lower_gamma_series(a, x, max_iter, tol)
        Q = 1.0 - P / math.exp(math.lgamma(a))
        if Q <= 0.0:
            # avoid log(0) or log(negative)
            return float('-inf')
        return math.log(Q) + math.lgamma(a)
    else:
        return log_upper_gamma_cf(a, x, max_iter, tol)


def knowledge_discounted_integral(
    stability: float,
    decay: float,
    factor: float,
    t_begin: Optional[float] = None,
    t_end: Optional[float] = None,
    gamma: float = 0.99,
    tol: float = 1e-14,
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
