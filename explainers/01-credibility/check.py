"""Every number the credibility explainer shows, recomputed from main.py's parameters.

Run: scripts/render.sh final runs this first; on its own,
    PYTHONPATH=. xvfb-run -a ~/.venvs/manim-gl/bin/python explainers/01-credibility/check.py
"""
import math

from main import ALPHA, BETA, DRIVER_CLAIMS, credibility_factor, gamma_pdf


def check(label, shown, value, tol=1e-9):
    ok = abs(shown - value) < tol
    print(f"{'ok ' if ok else 'BAD'} {label:52s} shown {shown!s:>8}   computed {value:.6g}")
    assert ok, label


n = len(DRIVER_CLAIMS)
total = sum(DRIVER_CLAIMS)
xbar = total / n
mu = ALPHA / BETA

# WhoseNumber and PortfolioPrior
check("xbar = (1 + 0 + 2 + 0) / 4", 0.75, xbar)
check("mu = alpha / beta", 0.5, mu)
check("prior Gamma(2, 4): alpha", 2, ALPHA)
check("prior Gamma(2, 4): beta", 4, BETA)

# YearByYear: Gamma(alpha + sum x, beta + n) after each year
check("posterior after year 1: Gamma(3, 5), alpha", 3, ALPHA + DRIVER_CLAIMS[0])
check("posterior after year 1: Gamma(3, 5), beta", 5, BETA + 1)
check("alpha + sum x = 2 + 3", 5, ALPHA + total)
check("beta + n = 4 + 4", 8, BETA + n)

# WhereIsTheMean: the posterior mean is the credibility weighted average
posterior_mean = (ALPHA + total) / (BETA + n)
Z = credibility_factor(n)
check("Z = 4 / (4 + 4)", 0.5, Z)
check("0.5 x 0.75 + 0.5 x 0.5", 0.625, Z * xbar + (1 - Z) * mu)
check("posterior mean (alpha + sum x) / (beta + n)", 0.625, posterior_mean)
check("the posterior's pdf integrates to 1", 1.0,
      sum(gamma_pdf((i + 0.5) / 1000, ALPHA + total, BETA + n) for i in range(20000)) / 1000, tol=1e-4)

# BalanceBeam: Z and the balance point as n grows (readouts to 2 and 3 decimals)
for years in [0, 1, 4, 12, 36, 100]:
    z = credibility_factor(years)
    print(f"    n = {years:3d}: Z = {z:.2f}, estimate = {z * xbar + (1 - z) * mu:.3f}")

# WithinVsBetween: law of total variance; k = E[V(X|lambda)] / V[E(X|lambda)] = beta
within = ALPHA / BETA        # E[V(X | lambda)] = E(lambda) for Poisson claims
between = ALPHA / BETA**2    # V[E(X | lambda)] = V(lambda)
check("E[V(X | lambda)] = alpha / beta", 0.5, within)
check("V[E(X | lambda)] = alpha / beta^2", 0.125, between)
check("k = 0.5 / 0.125 = 4 = beta", 4, within / between)
check("V(X) = 0.5 + 0.125", 0.625, ALPHA / BETA + ALPHA / BETA**2)
print(f"    shaded band: mean +/- sd of lambda = {mu:.3f} +/- {math.sqrt(ALPHA) / BETA:.3f}")

# CredibilitySummary: recall question
check("n / (n + 4) = 0.8 gives n = 16", 0.8, credibility_factor(16))
print("All numbers check out.")
