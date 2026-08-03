"""
theory.py — Closed-form theoretical predictions for D1 and D2 research bibles (v3).

All logarithms are natural (nats) to match the bibles' convention.

D1 — Rate-Constrained Decentralized Detection
    Main theorem D1*/D1**:  E_k(theta) = min{ E_cen, theta_IB(Gamma_k) }
    Gaussian against-independence model (bible D1 v3, section 1.6-AI).

D2 — Restoration-Anytime Limit over Lossy Channels
    Exact m-th moment threshold:  gamma = (1-p) e^{m(h_R-R)/d+} + p e^{m r*_top} < 1
    Marginals:  (R) R(1-p) >= h_R ;  (A) p e^{m r*_top} < 1  <=>  p_c(m) = e^{-m r*}

References inline cite the bible sections.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq


# =====================================================================================
# D1 — Gaussian against-independence information bottleneck (bible D1 v3, 1.6-AI)
# =====================================================================================

def mutual_information_XY(rho: float) -> float:
    """I(X_i; Y) = -1/2 ln(1 - rho^2)  [nats].  (bible 1.6-AI)

    X_i = rho Y + sqrt(1-rho^2) Z_i, Y ~ N(0,1), Z_i ~ N(0,1).
    """
    rho = np.asarray(rho, dtype=float)
    return -0.5 * np.log1p(-rho**2)


def E_cen_symmetric(N: int, rho: float) -> float:
    """Centralized Stein exponent, symmetric case: E_cen = N * I(X_i;Y).  (bible 1.6-AI)"""
    return N * mutual_information_XY(rho)


def E_cen_asymmetric(rhos) -> float:
    """E_cen = sum_i I(X_i; Y) = -1/2 sum_i ln(1 - rho_i^2).  (bible 1.6-AI)"""
    rhos = np.asarray(rhos, dtype=float)
    return float(np.sum(mutual_information_XY(rhos)))


def theta_IB_single(R: float, rho: float) -> float:
    """Single-agent Gaussian IB relevance curve (bible 1.6-AI):

        theta_IB_i(R) = -1/2 ln( 1 - rho^2 (1 - e^{-2R}) )   [nats]

    Properties: theta_IB_i(0)=0; slope rho^2 at R=0; saturates at I(X_i;Y) as R->inf.
    """
    R = np.asarray(R, dtype=float)
    val = 1.0 - rho**2 * (1.0 - np.exp(-2.0 * R))
    return -0.5 * np.log(val)


def theta_IB_symmetric(Gamma: float, N: int, rho: float) -> float:
    """Symmetric-network IB curve with equal split R = Gamma/N (bible 1.6-AI):

        theta_IB(Gamma) = -(N/2) ln( 1 - rho^2 (1 - e^{-2 Gamma/N}) )
    """
    Gamma = np.asarray(Gamma, dtype=float)
    R = Gamma / N
    return N * theta_IB_single(R, rho)


def _dtheta_dR_single(R: float, rho: float) -> float:
    """d theta_IB_i / dR = rho^2 e^{-2R} / (1 - rho^2 (1 - e^{-2R})).  (bible 1.6-AI)"""
    e = np.exp(-2.0 * R)
    return (rho**2 * e) / (1.0 - rho**2 * (1.0 - e))


def water_filling_allocation(Gamma: float, rhos, tol: float = 1e-12):
    """Optimal asymmetric rate allocation maximizing sum_i theta_IB_i(R_i) s.t. sum R_i = Gamma.

    Closed form (bible 1.6-AI, D1-C5):
        R_i*(nu) = 1/2 ln( rho_i^2 (1-nu) / (nu (1 - rho_i^2)) )   when > 0, else 0.
    nu in (0,1) found by 1-D root finding on sum_i max(0, R_i*(nu)) = Gamma.

    Returns (allocation array R_i, theta_IB(Gamma)).
    """
    rhos = np.asarray(rhos, dtype=float)
    r2 = rhos**2

    def Ri_of_nu(nu):
        # R_i*(nu) = 0.5 ln( r2 (1-nu) / (nu (1-r2)) )
        val = 0.5 * np.log((r2 * (1.0 - nu)) / (nu * (1.0 - r2)))
        return np.maximum(0.0, val)

    def total_rate(nu):
        return np.sum(Ri_of_nu(nu)) - Gamma

    if Gamma <= 0:
        return np.zeros_like(rhos), 0.0

    # As nu -> 0+, R_i -> +inf (total -> +inf). As nu -> 1-, R_i -> 0 (total -> 0 - Gamma < 0).
    # total_rate is decreasing in nu; bracket a root.
    lo, hi = 1e-15, 1.0 - 1e-15
    flo, fhi = total_rate(lo), total_rate(hi)
    if flo <= 0:  # Gamma so large that even nu->0 cannot use it (numerical); saturate all
        R = Ri_of_nu(lo)
        return R, float(np.sum(theta_IB_single(R, rhos)))
    nu_star = brentq(total_rate, lo, hi, xtol=tol, rtol=1e-14, maxiter=500)
    R = Ri_of_nu(nu_star)
    theta = float(np.sum(theta_IB_single(R, rhos)))
    return R, theta


def theta_IB_asymmetric(Gamma: float, rhos) -> float:
    """theta_IB(Gamma) for heterogeneous {rho_i} via water-filling (bible 1.6-AI)."""
    _, theta = water_filling_allocation(Gamma, rhos)
    return theta


def E_k_prediction_symmetric(Gamma: float, N: int, rho: float) -> float:
    """Full D1 prediction E_k = min{ E_cen, theta_IB(Gamma) }, symmetric case (bible 1.3/1.4)."""
    return float(np.minimum(E_cen_symmetric(N, rho), theta_IB_symmetric(Gamma, N, rho)))


def C_DIB_symmetric(N: int, rho: float, delta: float = 1e-6) -> float:
    """Saturation rate C_DIB: smallest Gamma with theta_IB(Gamma) = (1-delta) E_cen (bible 1.6-AI).

    theta_IB(Gamma) approaches E_cen only as Gamma->inf (exponentially), so we use the
    delta-saturation knee. Solve -(N/2) ln(1 - rho^2 (1-e^{-2R})) = (1-delta) E_cen for R,
    Gamma = N R.
    """
    Ecen = E_cen_symmetric(N, rho)
    target = (1.0 - delta) * Ecen
    # per-agent: -1/2 ln(1 - rho^2 (1-e^{-2R})) = target/N
    # 1 - rho^2 (1 - e^{-2R}) = exp(-2 target/N)
    rhs = np.exp(-2.0 * target / N)
    # rho^2 (1 - e^{-2R}) = 1 - rhs  ->  e^{-2R} = 1 - (1-rhs)/rho^2
    e2R = 1.0 - (1.0 - rhs) / rho**2
    if e2R <= 0:
        return np.inf
    R = -0.5 * np.log(e2R)
    return N * R


def rho_for_target_MI(I_target: float) -> float:
    """Invert I(X;Y) = -1/2 ln(1-rho^2) to get rho for a target per-agent MI (nats)."""
    return float(np.sqrt(1.0 - np.exp(-2.0 * I_target)))


# =====================================================================================
# D2 — Restoration-Anytime threshold (bible D2 v3, 2.3 / 2.4)
# =====================================================================================

# Analytic expansion rates of the primary surrogates (bible 2.6)
def r_star_circle(k: int) -> float:
    """Expanding circle map f(x)=k x mod 1: r*_top = r*_vol = h_R = ln k.  (bible 2.6.1)"""
    return float(np.log(k))


CAT_LAMBDA_U = (3.0 + np.sqrt(5.0)) / 2.0  # ~2.618, unstable eigenvalue of [[1,1],[1,2]]
CAT_LAMBDA_S = (3.0 - np.sqrt(5.0)) / 2.0  # ~0.382, stable eigenvalue


def r_star_cat() -> float:
    """Cat map A=[[1,1],[1,2]]: r*_top = r*_vol = h_R = ln lambda_u.  (bible 2.6.2)"""
    return float(np.log(CAT_LAMBDA_U))


def gamma_threshold(p: float, R: float, m: float, r_star: float,
                    h_R: float | None = None, d_plus: int = 1) -> float:
    """Exact m-th-moment drift coefficient (bible 2.4.1):

        gamma = (1-p) e^{m (h_R - R)/d+} + p e^{m r*_top}

    Stability iff gamma < 1. For the primary surrogates h_R = r*_top = r_star, d+ = 1.
    """
    if h_R is None:
        h_R = r_star
    p = np.asarray(p, dtype=float)
    R = np.asarray(R, dtype=float)
    alpha = np.exp(m * (h_R - R) / d_plus)   # delivered-step contraction factor^? (per-step, ^m applied)
    Lam = np.exp(m * r_star)                  # erased-step expansion factor^m
    return (1.0 - p) * alpha + p * Lam


def p_c_marginal(m: float, r_star: float) -> float:
    """Marginal reliability threshold (condition A, R->inf limit):

        p_c(m) = e^{-m r*}     (bible 2.3.1 / 2.6.3)
    """
    return float(np.exp(-m * r_star))


def p_c_exact(R: float, m: float, r_star: float, h_R: float | None = None,
              d_plus: int = 1) -> float:
    """Exact critical erasure prob at finite rate R: solve gamma(p,R,m)=1 for p.

    gamma = (1-p) A + p L = 1, with A = e^{m(h_R-R)/d+}, L = e^{m r*}.
    => p (L - A) = 1 - A  => p = (1 - A)/(L - A).
    Valid (in (0,1)) when A < 1 (R > h_R) and L > 1 (r*>0).
    """
    if h_R is None:
        h_R = r_star
    A = np.exp(m * (h_R - R) / d_plus)
    L = np.exp(m * r_star)
    if L <= A:
        return np.nan
    p = (1.0 - A) / (L - A)
    return float(p)


def R_c_exact(p: float, m: float, r_star: float, h_R: float | None = None,
              d_plus: int = 1) -> float:
    """Exact critical rate at erasure prob p: solve gamma(p,R,m)=1 for R.

    (1-p) e^{m(h_R-R)/d+} = 1 - p e^{m r*}
    => e^{m(h_R-R)/d+} = (1 - p e^{m r*})/(1-p)
    => (h_R - R) m/d+ = ln[(1 - p e^{m r*})/(1-p)]
    => R = h_R - (d+/m) ln[(1 - p e^{m r*})/(1-p)]
    Requires p e^{m r*} < 1 (condition A) for a finite solution.
    """
    if h_R is None:
        h_R = r_star
    L = np.exp(m * r_star)
    inner = (1.0 - p * L) / (1.0 - p)
    if inner <= 0:
        return np.inf  # condition (A) violated: no finite rate stabilizes
    return float(h_R - (d_plus / m) * np.log(inner))


if __name__ == "__main__":
    # Quick self-consistency checks against the bible's stated numbers.
    print("=== D1 checks ===")
    rho = rho_for_target_MI(0.5)
    print(f"rho for I=0.5 nats: {rho:.6f} (bible ~0.795)")
    print(f"I(X;Y)={mutual_information_XY(rho):.6f} (target 0.5)")
    print(f"E_cen(N=4)={E_cen_symmetric(4, rho):.6f} (bible 2.0)")
    print(f"theta_IB_single(0.5, rho)={theta_IB_single(0.5, rho):.6f}")
    print(f"theta_IB_single(inf)->{mutual_information_XY(rho):.6f} (saturation)")
    # water-filling symmetric should match equal split
    R, th = water_filling_allocation(2.0, [rho]*4)
    print(f"water-fill sym alloc={R} theta={th:.6f} vs symmetric={theta_IB_symmetric(2.0,4,rho):.6f}")

    print("\n=== D2 checks ===")
    print(f"r*_circle(k=2)={r_star_circle(2):.6f} (ln2={np.log(2):.6f})")
    print(f"r*_cat={r_star_cat():.6f} (ln lambda_u, lambda_u={CAT_LAMBDA_U:.6f})")
    for m in (1, 2, 4):
        print(f"circle k=2 p_c(m={m})={p_c_marginal(m, r_star_circle(2)):.6f} "
              f"(bible {2**-m:.6f})")
    for m in (1, 2, 4):
        print(f"cat p_c(m={m})={p_c_marginal(m, r_star_cat()):.6f}")
    print(f"exact p_c at R=ln2+0.1, m=2: {p_c_exact(np.log(2)+0.1, 2, np.log(2)):.6f} "
          f"(NOT 0.25 - marginal needs R->inf)")
    print(f"exact p_c at R=ln2+3, m=2:   {p_c_exact(np.log(2)+3, 2, np.log(2)):.6f} "
          f"(approaching 0.25)")
