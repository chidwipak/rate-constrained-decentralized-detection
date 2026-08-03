"""
topology.py — Graph construction and min-cut information-flow Gamma_k for Direction 1.

Gamma_k (bible 1.0) = min-cut capacity from all observation sources to node k. We model each
agent i!=k as a source whose local observation is available at i (super-source -> i, capacity inf);
each network edge (i,j) carries capacity C_ij; Gamma_k = min-cut(super-source -> k). For time-varying
topologies, Gamma_k = ergodic average of per-round min-cuts (bible Lemma A / Lemma C-D1).
"""
from __future__ import annotations

import networkx as nx
import numpy as np

INF = 1e12


def gamma_k(G: nx.Graph, k, capacity_attr: str = "capacity") -> float:
    """Min-cut information flow to node k: max-flow from a super-source (attached to every other
    node with infinite capacity) to sink k. Works for directed and undirected graphs."""
    H = nx.DiGraph()
    for u, v, d in G.edges(data=True):
        c = d.get(capacity_attr, 1.0)
        H.add_edge(u, v, capacity=c)
        if not G.is_directed():
            H.add_edge(v, u, capacity=c)
    src = "__super_source__"
    for node in G.nodes():
        if node != k:
            H.add_edge(src, node, capacity=INF)   # node's own observation available at node
    if src not in H or k not in H:
        return 0.0
    try:
        cut_value, _ = nx.minimum_cut(H, src, k)
    except Exception:
        return 0.0
    return float(min(cut_value, INF / 2))


def set_uniform_capacity(G: nx.Graph, C: float, attr: str = "capacity"):
    for _, _, d in G.edges(data=True):
        d[attr] = C
    return G


def scale_to_gamma(G: nx.Graph, k, target_gamma: float, attr: str = "capacity"):
    """Uniformly scale all edge capacities so that Gamma_k == target_gamma (holds Gamma_k constant
    across topologies for the min-cut-sufficiency experiment)."""
    set_uniform_capacity(G, 1.0, attr)
    g1 = gamma_k(G, k, attr)
    if g1 <= 0:
        return G, 0.0
    scale = target_gamma / g1
    set_uniform_capacity(G, scale, attr)
    return G, gamma_k(G, k, attr)


# ---- topology builders (undirected unless noted) ----
def make_ring(N):
    return nx.cycle_graph(N)


def make_path(N):
    return nx.path_graph(N)


def make_complete(N):
    return nx.complete_graph(N)


def make_star(N):
    return nx.star_graph(N - 1)  # node 0 center, N-1 leaves


def make_tree(N, branching=2):
    return nx.balanced_tree(branching, int(np.ceil(np.log(N * (branching - 1) + 1) / np.log(branching))) - 1) \
        if branching > 1 else nx.path_graph(N)


def make_grid(rows, cols):
    G = nx.grid_2d_graph(rows, cols)
    return nx.convert_node_labels_to_integers(G)


def make_erdos_renyi(N, p, seed=0):
    G = nx.erdos_renyi_graph(N, p, seed=seed)
    # ensure connected
    if not nx.is_connected(G):
        comps = list(nx.connected_components(G))
        for i in range(len(comps) - 1):
            u = next(iter(comps[i])); v = next(iter(comps[i + 1]))
            G.add_edge(u, v)
    return G


def make_barabasi_albert(N, m, seed=0):
    return nx.barabasi_albert_graph(N, m, seed=seed)


def make_watts_strogatz(N, k, p, seed=0):
    return nx.watts_strogatz_graph(N, k, p, seed=seed)


def make_directed_ring(N):
    G = nx.DiGraph()
    for i in range(N):
        G.add_edge(i, (i + 1) % N)
        G.add_edge((i + 1) % N, i)  # bidirectional directed (still respects orientation in cut)
    return G


def time_varying_gamma_k(graph_sequence, k, capacity_attr="capacity"):
    """Ergodic-average min-cut over a sequence of graphs (bible Lemma C-D1):
    Gamma_k = (1/T) sum_t min-cut_t. Returns (mean_gamma, per_round array)."""
    per_round = np.array([gamma_k(G, k, capacity_attr) for G in graph_sequence])
    return float(per_round.mean()), per_round
