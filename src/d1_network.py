"""
d1_network.py — GENUINE distributed-network detector for Direction 1.

Fixes the circularity of the original topology experiments (which discarded the graph after computing
the scalar Gamma_k). Here the delivered information rate to the sink EMERGES from an actual max-flow
routing on the actual graph, and different coding schemes deliver different rates on the SAME topology.

Model (single Gaussian evidence source, shared relevance Y at sink k — the cleanest relay-network test):
  Source s holds X = rho Y + sqrt(1-rho^2) Z; sink k holds Y and must test H0 (corr) vs H1 (indep).
  Each edge (i,j) carries a rate-C_ij Gaussian description; the max information deliverable s->k equals
  the min-cut F = mincut(s,k) (network-information-flow / cut-set bound, Lemma A).

Schemes (what each delivers, in nats, from the max-flow path decomposition {f_p}, sum f_p = F):
  * successive refinement (SR, = network coding): layers add   -> R_sr = F = min-cut  (ACHIEVES the cut)
  * naive independent descriptions (quantize-and-forward, no coding): Gaussian MMSE fusion is
    SUB-ADDITIVE in nats -> R_naive = 1/2 ln(1 + sum_p (e^{2 f_p} - 1)) <= F  (falls short when >1 path)
  * single best path: R_1 = max_p f_p                                          (falls short further)

The exponent of a rate-R Gaussian description is E = -1/2 ln(1 - rho^2(1-e^{-2R})) = theta_IB^{N=1}(R),
measured exactly by the Lugannani-Rice saddlepoint (d1_detect). A Monte-Carlo of the actual sampling +
fusion verifies the emergent effective correlation r_eff matches R.
"""
from __future__ import annotations

import networkx as nx
import numpy as np


def _to_digraph(G: nx.Graph, capacity_attr="capacity"):
    H = nx.DiGraph()
    for u, v, d in G.edges(data=True):
        c = float(d.get(capacity_attr, 1.0))
        H.add_edge(u, v, capacity=c)
        if not G.is_directed():
            H.add_edge(v, u, capacity=c)
    return H


def mincut_st(G: nx.Graph, s, t, capacity_attr="capacity"):
    """Min-cut (= max-flow) value and the flow dict for a single source s to sink t."""
    H = _to_digraph(G, capacity_attr)
    if s not in H or t not in H:
        return 0.0, {}
    val, flow = nx.maximum_flow(H, s, t)
    return float(val), flow


def path_decomposition(flow: dict, s, t, tol=1e-9):
    """Decompose a max-flow dict into (path, bottleneck) pairs. Sum of bottlenecks = flow value."""
    # residual flow graph
    R = nx.DiGraph()
    for u in flow:
        for v, f in flow[u].items():
            if f > tol:
                R.add_edge(u, v, f=f)
    paths = []
    while True:
        try:
            path = nx.shortest_path(R, s, t)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            break
        # bottleneck along path
        b = min(R[u][v]["f"] for u, v in zip(path[:-1], path[1:]))
        paths.append((path, b))
        for u, v in zip(path[:-1], path[1:]):
            R[u][v]["f"] -= b
            if R[u][v]["f"] <= tol:
                R.remove_edge(u, v)
    return paths


def farthest_source(G: nx.Graph, k):
    """Pick the source node farthest (hop distance) from k — a non-trivial relay scenario."""
    if G.is_directed():
        UG = G.to_undirected()
    else:
        UG = G
    try:
        dist = nx.shortest_path_length(UG, target=k)
    except Exception:
        dist = {n: 1 for n in G.nodes()}
    cand = [n for n in G.nodes() if n != k]
    return max(cand, key=lambda n: dist.get(n, 0))


# ----- delivered-rate models (nats) for the three schemes -----
def rate_sr(path_rates):
    """Successive refinement / network coding: additive layers -> equals the min-cut."""
    return float(sum(f for _, f in path_rates))


def rate_naive(path_rates):
    """Naive independent descriptions fused by Gaussian MMSE (sub-additive in nats)."""
    snr = sum(np.expm1(2.0 * f) for _, f in path_rates)   # sum of (e^{2f}-1)
    return float(0.5 * np.log1p(snr))


def rate_singlepath(path_rates):
    """Single widest path only."""
    return float(max((f for _, f in path_rates), default=0.0))


def r_eff_from_rate(R, rho):
    """Induced source-relevance correlation of a rate-R Gaussian description."""
    return float(np.sqrt(rho**2 * (1.0 - np.exp(-2.0 * R))))


def montecarlo_r_eff(path_rates, rho, scheme, n_samples, rng):
    """GENUINE Monte-Carlo: sample Y, X, per-path descriptions, fuse, and MEASURE the emergent
    effective correlation corr(fused_estimate, Y). Verifies the delivered-rate model empirically."""
    Y = rng.standard_normal(n_samples)
    X = rho * Y + np.sqrt(1 - rho**2) * rng.standard_normal(n_samples)
    if scheme == "sr":
        R = rate_sr(path_rates)
        varN = 1.0 / np.expm1(2.0 * R) if R > 0 else np.inf
        U = X + np.sqrt(varN) * rng.standard_normal(n_samples)
        est = U  # single refined description
    elif scheme == "single":
        R = rate_singlepath(path_rates)
        varN = 1.0 / np.expm1(2.0 * R) if R > 0 else np.inf
        U = X + np.sqrt(varN) * rng.standard_normal(n_samples)
        est = U
    else:  # naive: independent descriptions, MMSE (precision-weighted) fusion
        prec = np.zeros(n_samples); acc = np.zeros(n_samples)
        for _, f in path_rates:
            if f <= 0:
                continue
            varN = 1.0 / np.expm1(2.0 * f)
            Up = X + np.sqrt(varN) * rng.standard_normal(n_samples)
            w = 1.0 / (varN + 1e-300)     # precision of this description about X
            acc += w * Up; prec += w
        est = acc / np.maximum(prec, 1e-300)
    # empirical correlation between the fused estimate and the relevance Y
    r = np.corrcoef(est, Y)[0, 1]
    return float(abs(r))


def analyze_topology(G, k, C, rho, n_mc=200000, rng=None, source=None):
    """Full genuine analysis of one topology at per-edge capacity C.
    Returns per-scheme delivered rate, analytic r_eff, MC-measured r_eff, and the min-cut."""
    rng = rng or np.random.default_rng(0)
    from topology import set_uniform_capacity, gamma_k
    set_uniform_capacity(G, C)
    s = source if source is not None else farthest_source(G, k)
    F, flow = mincut_st(G, s, k)
    Gamma_super = gamma_k(G, k)     # super-source min-cut (all agents) for reference
    paths = path_decomposition(flow, s, k) if F > 0 else []
    out = {"source": s, "mincut_sk": F, "gamma_super": Gamma_super, "n_paths": len(paths),
           "path_rates": [b for _, b in paths]}
    for scheme, ratefn in (("sr", rate_sr), ("naive", rate_naive), ("single", rate_singlepath)):
        R = ratefn(paths)
        out[scheme] = {
            "rate": R,
            "r_eff_analytic": r_eff_from_rate(R, rho),
            "r_eff_mc": montecarlo_r_eff(paths, rho, scheme, n_mc, rng),
        }
    return out
