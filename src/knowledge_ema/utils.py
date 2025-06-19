import math


def log_upper_incomplete_gamma(a, x, max_iter=200, tol=1e-14):
    """
    Compute log(Γ(a, x)) for a > 0 and x > 0 using continued fraction (Lentz's method).
    This is the logarithm of the upper incomplete gamma function.
    """
    if not (a > 0 and x > 0):
        raise ValueError("Requires a > 0 and x > 0")

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
    return log_Q + math.lgamma(a)  # log Γ(a, x) = log Q + log Γ(a)
