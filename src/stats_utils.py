"""
stats_utils.py — Statistical utilities: bootstrap CIs, exponent fitting, logistic
phase-transition fitting, effect sizes. Used by all experiments for rigorous reporting.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize, stats


def bootstrap_ci(data, statistic=np.mean, n_boot: int = 10000, ci: float = 0.95,
                 rng: np.random.Generator | None = None):
    """Nonparametric bootstrap CI for a statistic of a 1-D sample.

    Returns (point_estimate, lo, hi).
    """
    rng = rng or np.random.default_rng(0)
    data = np.asarray(data, dtype=float)
    n = len(data)
    point = float(statistic(data))
    if n < 2:
        return point, point, point
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = np.array([statistic(data[i]) for i in idx])
    alpha = (1.0 - ci) / 2.0
    lo, hi = np.quantile(boot, [alpha, 1.0 - alpha])
    return point, float(lo), float(hi)


def fit_exponent(n_values, beta_values, weights=None):
    """Fit an error exponent E from beta_n ~ exp(-n E) via OLS of ln(beta) on n.

    Returns dict with slope (=E), intercept, se_slope (HC-robust), r2, n_used.
    Only uses strictly positive beta values.
    """
    n_values = np.asarray(n_values, dtype=float)
    beta_values = np.asarray(beta_values, dtype=float)
    mask = (beta_values > 0) & np.isfinite(beta_values)
    n = n_values[mask]
    y = np.log(beta_values[mask])
    if len(n) < 2:
        return dict(E=np.nan, intercept=np.nan, se=np.nan, r2=np.nan, n_used=len(n))
    X = np.column_stack([np.ones_like(n), n])
    # OLS
    beta_hat, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta_hat
    # Heteroscedasticity-robust (HC0) covariance
    XtX_inv = np.linalg.inv(X.T @ X)
    S = (X * resid[:, None]).T @ (X * resid[:, None])
    cov = XtX_inv @ S @ XtX_inv
    se_slope = float(np.sqrt(cov[1, 1]))
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - y.mean())**2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return dict(E=float(-beta_hat[1]), intercept=float(beta_hat[0]),
                se=se_slope, r2=r2, n_used=int(len(n)))


def logistic_fit(p_values, escape_rate, p0=None):
    """Fit escape_rate ~ 1/(1+exp(-slope (p - p_c))) to locate the critical point p_c.

    Returns dict with p_c, slope, and standard errors (from covariance).
    """
    p_values = np.asarray(p_values, dtype=float)
    escape_rate = np.asarray(escape_rate, dtype=float)

    def logistic(p, pc, slope):
        z = np.clip(slope * (p - pc), -500, 500)
        return 1.0 / (1.0 + np.exp(-z))

    if p0 is None:
        # initial guess: p_c where escape crosses 0.5
        cross = np.interp(0.5, escape_rate, p_values) if escape_rate.max() > 0.5 > escape_rate.min() \
            else p_values[np.argmin(np.abs(escape_rate - 0.5))]
        p0 = [cross, 50.0]
    if escape_rate.max() < 0.5 or escape_rate.min() > 0.5:
        # transition not bracketed by the sweep; report NaN rather than a spurious fit
        return dict(p_c=np.nan, slope=np.nan, p_c_se=np.nan, slope_se=np.nan,
                    note="transition not bracketed by p-grid")
    try:
        popt, pcov = optimize.curve_fit(logistic, p_values, escape_rate, p0=p0, maxfev=20000)
        perr = np.sqrt(np.diag(pcov))
        return dict(p_c=float(popt[0]), slope=float(popt[1]),
                    p_c_se=float(perr[0]), slope_se=float(perr[1]))
    except Exception as e:  # noqa
        return dict(p_c=np.nan, slope=np.nan, p_c_se=np.nan, slope_se=np.nan, error=str(e))


def cohens_d(a, b):
    """Cohen's d effect size between two samples (pooled SD)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    if sp == 0:
        return np.nan
    return float((a.mean() - b.mean()) / sp)


def holm_bonferroni(pvals, alpha: float = 0.05):
    """Holm-Bonferroni step-down. Returns (reject_bool_array, adjusted_alpha_thresholds)."""
    pvals = np.asarray(pvals, dtype=float)
    m = len(pvals)
    order = np.argsort(pvals)
    reject = np.zeros(m, dtype=bool)
    for rank, idx in enumerate(order):
        thresh = alpha / (m - rank)
        if pvals[idx] <= thresh:
            reject[idx] = True
        else:
            break
    return reject


def wilson_ci(k: int, n: int, z: float = 1.96):
    """Wilson score interval for a binomial proportion k/n (for escape rates)."""
    if n == 0:
        return 0.0, 0.0, 1.0
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2)) / denom
    return float(phat), float(max(0.0, center - half)), float(min(1.0, center + half))
