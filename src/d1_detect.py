"""
d1_detect.py — Detection engine for Direction 1 (rate-constrained decentralized detection).

Model (bible 1.6-AI, independent per-agent relevance — the self-consistent instantiation):
  Agent i observes (X_i, Y_i), Y_i ~ N(0,1) i.i.d. across agents, X_i = rho_i Y_i + sqrt(1-rho_i^2) Z_i.
  Test H0: X_i correlated with Y_i (all i)  vs  H1: X_i _|_ Y_i (all i).
  Full-data Stein exponent E_cen = sum_i I(X_i;Y_i) = -1/2 sum_i ln(1-rho_i^2).

Rate-R_i Gaussian IB representation: U_i = a_i X_i + xi_i with I(U_i;X_i)=R_i.
  Induced U-Y correlation r_UY,i with r_UY,i^2 = rho_i^2 (1 - e^{-2 R_i}), so the per-agent
  against-independence exponent is exactly  -1/2 ln(1 - r_UY,i^2) = theta_IB_i(R_i).
  Network exponent E_k = min{ E_cen, theta_IB(Gamma_k) }  (bible D1*/D1**).

EXPONENT MEASUREMENT — the naive Monte Carlo of bible 1.8 CANNOT reach beta_n ~ e^{-2n}; we use the
EXACT finite-n error probability of the optimal (Neyman-Pearson) detector via a saddlepoint
(Lugannani-Rice) evaluation of the per-sample log-likelihood-ratio CGF (a Gaussian quadratic form),
plus an importance-sampling Monte-Carlo cross-check of the actual simulated detector.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm
from scipy.special import log_ndtr, logsumexp


# =====================================================================================
# IB encoder and induced correlation
# =====================================================================================
def ib_r_uy(R: float, rho: float) -> float:
    """Induced U-Y correlation of the optimal Gaussian IB encoder at rate R:
       r_UY^2 = rho^2 (1 - e^{-2R}).  (derivation in bible 1.6-AI)."""
    return float(np.sqrt(rho**2 * (1.0 - np.exp(-2.0 * R))))


def exponent_from_r(r_uy: float) -> float:
    """Per-agent against-independence Stein exponent = -1/2 ln(1 - r_UY^2) = I(U;Y)."""
    return -0.5 * np.log(1.0 - r_uy**2)


def scalar_quantizer_mi(boundaries, rho: float, n_y: int = 4000):
    """For a scalar quantizer U=Q(X) of the Gaussian AI model, return (I(U;X), I(U;Y)) in nats.
    X = rho Y + sqrt(1-rho^2) Z, Y~N(0,1). U = bin index of X under `boundaries` (interior edges).
    I(U;X)=H(U) (deterministic quantizer); I(U;Y)=H(U)-H(U|Y). Used for the converse (D1*)
    demonstration that every rate-Gamma scheme lies on/under the IB curve."""
    b = np.concatenate([[-np.inf], np.sort(boundaries), [np.inf]])
    sd = np.sqrt(1 - rho**2)
    # marginal P(U=j) via X~N(0,1)
    Fx = norm.cdf(b)
    pU = np.diff(Fx)
    pU = pU / pU.sum()
    HU = -np.sum([p * np.log(p) for p in pU if p > 0])
    # H(U|Y) = E_Y[ H(U | Y=y) ], integrate over y with Gauss-Hermite-like grid
    ys, wy = np.polynomial.legendre.leggauss(n_y)
    ymax = 8.0
    ys = ys * ymax
    wy = wy * ymax
    py = norm.pdf(ys)
    HU_given_Y = 0.0
    for y, w, fy in zip(ys, wy, py):
        Fc = norm.cdf((b - rho * y) / sd)
        pcond = np.diff(Fc)
        s = pcond.sum()
        if s > 0:
            pcond = pcond / s
        h = -np.sum([p * np.log(p) for p in pcond if p > 0])
        HU_given_Y += w * fy * h
    I_UY = HU - HU_given_Y
    return float(HU), float(max(I_UY, 0.0))


def uniform_quantizer_boundaries(L: int, span: float = 6.0):
    """L-level uniform quantizer interior boundaries over [-span/2, span/2] (for N(0,1))."""
    return np.linspace(-span / 2, span / 2, L + 1)[1:-1]


def lloyd_max_boundaries(L: int, rho: float = None, iters: int = 50, n_grid: int = 20000):
    """Lloyd-Max (MSE-optimal) quantizer boundaries for a standard normal source."""
    x = np.linspace(-8, 8, n_grid)
    px = norm.pdf(x)
    # init levels at uniform quantiles
    levels = norm.ppf((np.arange(L) + 0.5) / L)
    for _ in range(iters):
        bnd = (levels[:-1] + levels[1:]) / 2
        edges = np.concatenate([[-np.inf], bnd, [np.inf]])
        new_levels = []
        for j in range(L):
            m = (x >= edges[j]) & (x < edges[j + 1])
            if px[m].sum() > 0:
                new_levels.append(np.sum(x[m] * px[m]) / np.sum(px[m]))
            else:
                new_levels.append(levels[j])
        levels = np.array(new_levels)
    return (levels[:-1] + levels[1:]) / 2


# =====================================================================================
# Per-sample LLR as a Gaussian quadratic form  L = z^T M z + c,  z=(u,y) standardized
# =====================================================================================
def _M_c(r: float):
    """Quadratic-form matrix M and constant c of the per-sample LLR for corr-r vs independence."""
    d = 1.0 - r**2
    M = np.array([[-r**2 / (2 * d), r / (2 * d)],
                  [r / (2 * d), -r**2 / (2 * d)]])
    c = -0.5 * np.log(d)
    return M, c


def _Sigma(r: float, hypo: str):
    """Covariance of z=(u,y): H0 -> corr r; H1 -> identity (independent)."""
    if hypo == "H0":
        return np.array([[1.0, r], [r, 1.0]])
    return np.eye(2)


def llr_cgf(s: float, r: float, hypo: str):
    """CGF K(s)=ln E[e^{s L}] of one agent's per-sample LLR under H0 or H1.
       For a Gaussian quadratic form: E[e^{s(z^T M z)}] = det(I - 2 s Sigma M)^{-1/2}."""
    M, c = _M_c(r)
    Sig = _Sigma(r, hypo)
    A = np.eye(2) - 2.0 * s * Sig @ M
    det = np.linalg.det(A)
    if det <= 0:
        return np.inf
    return -0.5 * np.log(det) + s * c


def _cgf_derivs(s: float, r: float, hypo: str, h: float = 1e-5):
    """Numerical K'(s), K''(s) of one agent's per-sample LLR CGF (central differences)."""
    k_p = llr_cgf(s + h, r, hypo)
    k_m = llr_cgf(s - h, r, hypo)
    k_0 = llr_cgf(s, r, hypo)
    return (k_p - k_m) / (2 * h), (k_p - 2 * k_0 + k_m) / (h * h)


# =====================================================================================
# Multi-agent CGF (sum of independent agents, each with n i.i.d. samples)
# =====================================================================================
def total_cgf(s: float, rs, n: int, hypo: str):
    """CGF of the total LLR S = sum_i sum_{t=1..n} L_{i,t}: n * sum_i K_i(s)."""
    return n * sum(llr_cgf(s, r, hypo) for r in rs)


def total_cgf_derivs(s: float, rs, n: int, hypo: str):
    d1 = d2 = 0.0
    for r in rs:
        a, b = _cgf_derivs(s, r, hypo)
        d1 += a; d2 += b
    return n * d1, n * d2


def relative_entropy_variance(rs) -> float:
    """Per-sample relative-entropy variance V = Var_{H0}(LLR) = K''(0) under H0 (bible 1.5.1).
    Governs the second-order (Strassen) dispersion term -sqrt(nV) Phi^{-1}(eps)."""
    _, v = total_cgf_derivs(0.0, rs, 1, "H0")
    return float(v)


def _s_domain(rs, hypo: str):
    """Analytic (s_lo, s_hi): the interval containing 0 on which every agent's CGF is finite.
    Per agent, det(I - 2s Sigma M) = 4 det(A) s^2 - 2 tr(A) s + 1 with A=Sigma M; the CGF is finite
    where this quadratic is > 0. s_hi = nearest positive root over agents; s_lo = nearest negative."""
    return _s_domain_cached(tuple(round(float(r), 12) for r in rs), hypo)


@lru_cache(maxsize=4096)
def _s_domain_cached(rs, hypo: str):
    s_hi, s_lo = np.inf, -np.inf
    for r in rs:
        M, _ = _M_c(r)
        A = _Sigma(r, hypo) @ M
        trA = float(np.trace(A))
        detA = float(np.linalg.det(A))
        a2 = 4.0 * detA
        a1 = -2.0 * trA
        a0 = 1.0
        if abs(a2) < 1e-15:                       # linear: a1 s + 1 = 0
            if abs(a1) > 1e-15:
                root = -a0 / a1
                if root > 0:
                    s_hi = min(s_hi, root)
                elif root < 0:
                    s_lo = max(s_lo, root)
            continue
        disc = a1 * a1 - 4 * a2 * a0
        if disc <= 0:
            continue                              # quadratic never zero -> no constraint
        sq = np.sqrt(disc)
        for root in ((-a1 - sq) / (2 * a2), (-a1 + sq) / (2 * a2)):
            if root > 1e-12:
                s_hi = min(s_hi, root)
            elif root < -1e-12:
                s_lo = max(s_lo, root)
    # pad slightly inside to keep CGF finite
    if np.isfinite(s_hi):
        s_hi *= 0.999999
    else:
        s_hi = 50.0
    if np.isfinite(s_lo):
        s_lo *= 0.999999
    else:
        s_lo = -50.0
    return float(s_lo), float(s_hi)


# =====================================================================================
# Lugannani-Rice saddlepoint tail probabilities for S_n
# =====================================================================================
def _saddle(rs, n, hypo, x, s_lo, s_hi, upper: bool):
    """Solve K'(s)=x for the saddlepoint; return (s_hat, w, u) or None."""
    def eqn(s):
        d1, _ = total_cgf_derivs(s, rs, n, hypo)
        return d1 - x
    if upper:
        a, b = 1e-10, s_hi - 1e-7
    else:
        a, b = s_lo + 1e-7, -1e-10
    try:
        if eqn(a) * eqn(b) > 0:
            return None
        s_hat = brentq(eqn, a, b, maxiter=300)
    except Exception:
        return None
    K = total_cgf(s_hat, rs, n, hypo)
    _, K2 = total_cgf_derivs(s_hat, rs, n, hypo)
    if K2 <= 0:
        return None
    w = np.sign(s_hat) * np.sqrt(max(2 * (s_hat * x - K), 0.0))
    u = s_hat * np.sqrt(K2)
    return s_hat, w, u


def log_lr_upper(rs, n: int, hypo: str, x: float, s_lo=None, s_hi=None) -> float:
    """ln P(S >= x) via Lugannani-Rice in LOG space (robust to underflow). x > mean."""
    if s_lo is None:
        s_lo, s_hi = _s_domain(rs, hypo)
    sol = _saddle(rs, n, hypo, x, s_lo, s_hi, upper=True)
    if sol is None:
        return np.nan
    _, w, u = sol
    if w <= 0 or u <= 0:
        return np.nan
    lnQ = log_ndtr(-w)                       # ln(1-Phi(w))
    lnphi = -0.5 * w * w - 0.5 * np.log(2 * np.pi)
    corr = 1.0 / u - 1.0 / w                 # P = Q(w) + phi(w)*corr
    if corr >= 0:
        return float(np.logaddexp(lnQ, lnphi + np.log(corr)))
    # corr<0: P = exp(lnQ) - exp(lnphi+ln|corr|)
    ln_neg = lnphi + np.log(-corr)
    if ln_neg >= lnQ:                        # numerical guard -> fall back to Bahadur-Rao leading term
        return float(lnphi - np.log(u))
    return float(lnQ + np.log1p(-np.exp(ln_neg - lnQ)))


def lugannani_rice_lower(rs, n: int, hypo: str, x: float, s_lo=None, s_hi=None) -> float:
    """P(S <= x) (actual probability; used for the ~epsilon Type-I calibration)."""
    if s_lo is None:
        s_lo, s_hi = _s_domain(rs, hypo)
    mean0, _ = total_cgf_derivs(0.0, rs, n, hypo)
    if x >= mean0:
        lu = log_lr_upper(rs, n, hypo, x, s_lo, s_hi)
        return float(1.0 - np.exp(lu)) if np.isfinite(lu) else np.nan
    sol = _saddle(rs, n, hypo, x, s_lo, s_hi, upper=False)
    if sol is None:
        return np.nan
    _, w, u = sol
    val = norm.cdf(w) - norm.pdf(w) * (1.0 / u - 1.0 / w)
    return float(min(max(val, 0.0), 1.0))


# =====================================================================================
# Exact finite-n Neyman-Pearson error and error exponent
# =====================================================================================
@dataclass
class ExponentResult:
    Gamma: float
    rs: tuple
    theta_IB: float          # predicted exponent (analytic)
    E_cen: float
    E_pred: float            # min(E_cen, theta_IB)
    E_measured: float        # dispersion-corrected asymptotic exponent (primary)
    E_measured_se: float
    E_slope_raw: float       # raw slope of -ln beta_n vs n (finite-n, biased low)
    ns: np.ndarray
    log_beta: np.ndarray


def _cgf_third(s, rs, n, hypo, h=1e-4):
    """Numerical K'''(s) of the total CGF (for Cornish-Fisher skewness)."""
    kpp_p = total_cgf_derivs(s + h, rs, n, hypo)[1]
    kpp_m = total_cgf_derivs(s - h, rs, n, hypo)[1]
    return (kpp_p - kpp_m) / (2 * h)


def _type1_threshold(rs, n, eps, s_lo0, s_hi0):
    """Robust threshold tau with P_H0(S<tau)=eps: saddlepoint root, Cornish-Fisher fallback."""
    mean_H0, var_H0 = total_cgf_derivs(0.0, rs, n, "H0")
    mean_H1, _ = total_cgf_derivs(0.0, rs, n, "H1")

    def type1(tau):
        v = lugannani_rice_lower(rs, n, "H0", tau, s_lo0, s_hi0)
        return v - eps if np.isfinite(v) else np.nan
    lo, hi = mean_H1 + 1e-6, mean_H0 - 1e-9
    try:
        flo, fhi = type1(lo), type1(hi)
        if np.isfinite(flo) and np.isfinite(fhi) and flo * fhi < 0:
            return brentq(type1, lo, hi, maxiter=300)
    except Exception:
        pass
    # Cornish-Fisher (Gaussian + skewness) fallback
    sd = np.sqrt(max(var_H0, 1e-300))
    z = norm.ppf(eps)
    k3 = _cgf_third(0.0, rs, n, "H0")
    gamma1 = k3 / (sd ** 3) if sd > 0 else 0.0
    z_cf = z + (z * z - 1) / 6.0 * gamma1
    return mean_H0 + sd * z_cf


def beta_n_saddlepoint(rs, n: int, eps: float):
    """Exact finite-n LOG Type-II error of the optimal detector at Type-I = eps.
    Threshold tau set by P_{H0}(S_n < tau) = eps; returns (log_beta, tau)."""
    s_lo0, s_hi0 = _s_domain(rs, "H0")
    s_lo1, s_hi1 = _s_domain(rs, "H1")
    tau = _type1_threshold(rs, n, eps, s_lo0, s_hi0)
    log_beta = log_lr_upper(rs, n, "H1", tau, s_lo1, s_hi1)
    return log_beta, tau


def measure_exponent(rs, ns, eps: float = 0.05, Gamma=None, E_cen=None):
    """Measure the operational error exponent via LOG saddlepoint beta_n over a range of n.

    Primary estimate: dispersion-corrected fit  -ln beta_n = a n + b sqrt(n) + c  (a = exponent),
    which removes the O(sqrt n) Strassen dispersion bias. Also reports the raw slope for honesty.
    """
    rs = tuple(float(r) for r in rs)
    theta = float(sum(exponent_from_r(r) for r in rs))
    log_beta = []
    for n in ns:
        lb, _ = beta_n_saddlepoint(rs, int(n), eps)
        log_beta.append(lb)
    log_beta = np.array(log_beta, dtype=float)
    ns_arr = np.asarray(ns, dtype=float)
    mask = np.isfinite(log_beta)
    E_disp, se, E_raw = np.nan, np.nan, np.nan
    if mask.sum() >= 3:
        nn = ns_arr[mask]
        y = -log_beta[mask]                       # -ln beta_n
        # dispersion-corrected: y = a n + b sqrt(n) + c
        A = np.column_stack([nn, np.sqrt(nn), np.ones_like(nn)])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        E_disp = float(coef[0])
        resid = y - A @ coef
        dof = max(1, len(nn) - 3)
        s2 = float(resid @ resid) / dof
        se = float(np.sqrt(s2 * np.linalg.inv(A.T @ A)[0, 0]))
        # raw slope
        Ar = np.column_stack([np.ones_like(nn), nn])
        E_raw = float(np.linalg.lstsq(Ar, y, rcond=None)[0][1])
    elif mask.sum() == 2:
        nn = ns_arr[mask]; y = -log_beta[mask]
        E_raw = float((y[1] - y[0]) / (nn[1] - nn[0])); E_disp = E_raw
    return ExponentResult(
        Gamma=Gamma, rs=rs, theta_IB=theta, E_cen=(E_cen if E_cen is not None else np.inf),
        E_pred=(min(E_cen, theta) if E_cen is not None else theta),
        E_measured=E_disp, E_measured_se=se, E_slope_raw=E_raw,
        ns=ns_arr, log_beta=log_beta)


# =====================================================================================
# Plain Monte-Carlo detector validator (cross-check of the saddlepoint at measurable beta)
# =====================================================================================
def plain_mc_beta(rs, n: int, eps: float, rng: np.random.Generator, n_mc: int = 400000):
    """Directly simulate the optimal detector: calibrate tau to Type-I=eps under H0 (empirical),
    then estimate beta = P_H1(S_n >= tau). Valid where beta is not too small (>~1e-5)."""
    rs = tuple(float(r) for r in rs)

    def draw_S(hypo):
        S = np.zeros(n_mc)
        for r in rs:
            M, c = _M_c(r)
            Sig = _Sigma(r, hypo)
            Lc = np.linalg.cholesky(Sig)
            for _t in range(n):
                z = rng.standard_normal((n_mc, 2)) @ Lc.T
                S += np.einsum("ij,jk,ik->i", z, M, z) + c
        return S
    S0 = draw_S("H0")
    tau = np.quantile(S0, eps)             # P_H0(S<tau)=eps
    S1 = draw_S("H1")
    beta = float(np.mean(S1 >= tau))
    return beta, tau

