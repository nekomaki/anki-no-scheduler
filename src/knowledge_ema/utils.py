import math


def lower_gamma_series(a: float, x: float, tol=1e-14, max_iter=200) -> float:
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


def log_upper_gamma(a: float, x: float) -> float:
    """
    Computes log(Γ(a, x)) for a > 0 and x > 0.
    Automatically chooses between series and continued fraction based on x.
    Reference: https://www.foo.be/docs-free/Numerical_Recipe_In_C/c6-2.pdf
    """
    if not (a > 0 and x > 0):
        raise ValueError("Requires a > 0 and x > 0")

    if x < a + 1:
        P = lower_gamma_series(a, x)
        Q = 1.0 - P / math.exp(math.lgamma(a))
        if Q <= 0.0:
            # avoid log(0) or log(negative)
            return float('-inf')
        return math.log(Q) + math.lgamma(a)
    else:
        return log_upper_gamma_cf(a, x)
