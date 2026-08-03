"""
paper_figs_d1.py — Regenerate the D1 paper figures (title-less, print-tuned)
from the saved experiment data in results/d1/data/. Output: Publication/D1/Figures/.

Only the five experimental figures selected for the manuscript are produced here;
the system-model figure is drawn in TikZ inside the LaTeX source.
All quantities in nats. Numbers are read from the frozen .npz/.json data; nothing
is recomputed or invented.
"""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

DATA = "results/d1/data"
OUT = "Publication/D1/Figures"
os.makedirs(OUT, exist_ok=True)

W = {  # Wong (2011) colour-blind-safe palette, consistent with code/plotting.py
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "grey": "#7F7F7F",
}


def set_style():
    plt.rcParams.update({
        "figure.dpi": 140,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "font.size": 9,
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "axes.titlesize": 9,
        "axes.labelsize": 9,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.alpha": 0.30,
        "grid.linewidth": 0.5,
        "legend.fontsize": 7.6,
        "legend.frameon": True,
        "legend.framealpha": 0.92,
        "legend.edgecolor": "0.8",
        "legend.handlelength": 1.8,
        "lines.linewidth": 1.7,
        "lines.markersize": 4.5,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def save(fig, name):
    for fmt in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{fmt}"), format=fmt)
    plt.close(fig)
    print("wrote", name)


def load_npz(e):
    return np.load(os.path.join(DATA, f"{e}.npz"), allow_pickle=True)


def load_json(e):
    with open(os.path.join(DATA, f"{e}.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------- E1 rate sweep
def fig_e1():
    d = load_npz("D1-E1")
    j = load_json("D1-E1")
    G, th, Em, Ese = d["Gammas"], d["theta"], d["E_meas"], d["E_se"]
    Ecen = 2.0
    Cdib = j["C_DIB"]
    fig, ax = plt.subplots(figsize=(3.45, 2.65))
    ax.plot(G, th, color=W["blue"], zorder=2,
            label=r"$\theta_{\mathrm{IB}}(\Gamma_k)$ (achievability)")
    ax.axhline(Ecen, color=W["orange"], ls="--", zorder=1,
               label=r"$E^{\mathrm{cen}}=2.00$ (converse)")
    ax.axvline(Cdib, color=W["green"], ls=":", lw=1.4, zorder=1,
               label=r"$C_{\mathrm{DIB}}\approx 8.89$")
    ax.errorbar(G, Em, yerr=1.96 * Ese, fmt="o", color="black", ms=3.3,
                elinewidth=0.9, capsize=1.6, zorder=3,
                label=r"measured $E_k$ (saddlepoint)")
    ax.set_xlabel(r"cut budget $\Gamma_k$ (nats/use)")
    ax.set_ylabel(r"error exponent $E_k$ (nats)")
    ax.set_xlim(0, 12.3)
    ax.set_ylim(0, 2.15)
    ax.legend(loc="lower right")
    fig.tight_layout()
    save(fig, "fig_e1_rate_sweep")


# ------------------------------------------------------------- E4 water-filling
def fig_e4():
    d = load_npz("D1-E4")
    j = load_json("D1-E4")
    G, twf, teq, Ewf = d["Gammas"], d["theta_wf"], d["theta_eq"], d["E_wf"]
    fig, ax = plt.subplots(figsize=(3.45, 2.65))
    ax.plot(G, twf, color=W["blue"], label=r"water-filling $\theta_{\mathrm{IB}}(\Gamma)$")
    ax.plot(G, teq, color=W["orange"], ls="--", label=r"equal split")
    ax.plot(G, Ewf, "o", color="black", ms=3.0, label=r"measured $E_k$")
    ax.set_xlabel(r"total budget $\Gamma$ (nats/use)")
    ax.set_ylabel(r"error exponent (nats)")
    ax.annotate(rf"max gain $= {j['max_gain']:.3f}$ nats",
                xy=(0.97, 0.05), xycoords="axes fraction", ha="right", va="bottom",
                fontsize=7.6, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.8"))
    ax.legend(loc="upper left")
    fig.tight_layout()
    save(fig, "fig_e4_waterfilling")


# ---------------------------------------------------------- E6 dynamic topology
def fig_e6():
    d = load_npz("D1-E6")
    pr = d["per_round"]
    gerg = float(d["gamma_erg"])
    # grounded predictor exponents (resultsD1.md): min-round, ergodic, max-round, measured
    labels = ["min-round\ncut", "ergodic\nmean", "max-round\ncut", "measured"]
    vals = [0.5924, 1.4893, 2.1568, 1.4883]
    cols = [W["grey"], W["blue"], W["grey"], W["red"]]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.55))
    # (a) per-round min-cut trace, first 80 rounds
    r = np.arange(80)
    a1.step(r, pr[:80], where="mid", color=W["sky"], lw=1.0, label="per-round min-cut")
    a1.axhline(gerg, color=W["blue"], ls="--", lw=1.6,
               label=rf"ergodic mean $\bar\Gamma_k={gerg:.2f}$")
    a1.set_xlabel("round $t$")
    a1.set_ylabel(r"min-cut (nats/use)")
    a1.set_ylim(0, 5.5)
    a1.legend(loc="upper right")
    a1.text(-0.16, 1.02, "(a)", transform=a1.transAxes, fontweight="bold", fontsize=10)
    # (b) predictor comparison
    x = np.arange(len(vals))
    a2.bar(x, vals, color=cols, width=0.62, edgecolor="black", lw=0.6)
    a2.axhline(1.4883, color=W["red"], ls=":", lw=1.2)
    for xi, v in zip(x, vals):
        a2.text(xi, v + 0.04, f"{v:.3f}", ha="center", va="bottom", fontsize=7.4)
    a2.set_xticks(x)
    a2.set_xticklabels(labels, fontsize=7.6)
    a2.set_ylabel(r"predicted exponent (nats)")
    a2.set_ylim(0, 2.5)
    a2.text(-0.16, 1.02, "(b)", transform=a2.transAxes, fontweight="bold", fontsize=10)
    fig.tight_layout()
    save(fig, "fig_e6_dynamic")


# ----------------------------------------------------------- N1 genuine network
def fig_n1():
    d = load_npz("D1-N1")
    j = load_json("D1-N1")
    names = j["names"]
    Esr, Ena = d["E_sr"], d["E_naive"]
    th = float(d["theta_star"])
    G, ssr, sna, ssg = d["sweep_G"], d["sw_sr"], d["sw_naive"], d["sw_single"]
    short = {"complete": "K", "ring": "ring", "path": "path", "star": "star",
             "grid 3x3": "grid", "tree": "tree", "Erdos-Renyi": "ER",
             "Barabasi-Albert": "BA", "Watts-Strogatz": "WS", "grid 2x4": "grid2"}
    lab = [short.get(n, n) for n in names]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.7))
    # (a) per-topology exponents at matched Gamma_k = 2.5
    x = np.arange(len(names))
    w = 0.4
    a1.bar(x - w / 2, Esr, w, color=W["blue"], edgecolor="black", lw=0.5,
           label="network coding / SR")
    a1.bar(x + w / 2, Ena, w, color=W["orange"], edgecolor="black", lw=0.5,
           label="naive quantize-and-forward")
    a1.axhline(th, color=W["green"], ls="--", lw=1.4,
               label=rf"$\theta_{{\mathrm{{IB}}}}(\Gamma_k)={th:.3f}$")
    a1.set_xticks(x)
    a1.set_xticklabels(lab, rotation=45, ha="right", fontsize=6.8)
    a1.set_ylabel(r"exponent $E_k$ (nats)")
    a1.set_ylim(0, 0.95)
    a1.legend(loc="lower center", fontsize=6.8)
    a1.text(-0.17, 1.02, "(a)", transform=a1.transAxes, fontweight="bold", fontsize=10)
    # (b) exponent vs budget on the complete graph
    a2.plot(G, ssr, color=W["blue"], label="network coding / SR (attains cut)")
    a2.plot(G, sna, color=W["orange"], ls="--", label="naive forward")
    a2.plot(G, ssg, color=W["red"], ls=":", label="single path")
    a2.set_xlabel(r"cut budget $\Gamma_k$ (nats/use)")
    a2.set_ylabel(r"exponent $E_k$ (nats)")
    a2.legend(loc="lower right")
    a2.text(-0.17, 1.02, "(b)", transform=a2.transAxes, fontweight="bold", fontsize=10)
    fig.tight_layout()
    save(fig, "fig_n1_network")


# ---------------------------------------------------------------- N5 RLNC code
def fig_n5():
    d = load_npz("D1-N5")
    j = load_json("D1-N5")
    hs, ra = d["hs"], d["rec_a"]
    qs, rb, ho = d["qs"], d["rec_b"], d["ho_b"]
    F = j["F"]
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(7.15, 2.35))
    # (a) recovery vs number of descriptions h; sharp threshold at min-cut F
    a1.plot(hs, ra, "o-", color=W["blue"], ms=4.5)
    a1.axvline(F, color=W["red"], ls="--", lw=1.4, label=rf"min-cut $F={F}$")
    a1.set_xlabel(r"descriptions $h$")
    a1.set_ylabel("recover-all probability")
    a1.set_ylim(-0.05, 1.08)
    a1.legend(loc="lower left")
    a1.text(-0.28, 1.02, "(a)", transform=a1.transAxes, fontweight="bold", fontsize=10)
    # (b) recovery vs field size q at the boundary h = F
    a2.semilogx(qs, rb, "o-", color=W["blue"], label="RLNC recovery")
    a2.semilogx(qs, ho, "s--", color=W["orange"], ms=3.6,
                label=r"$(1-h/q)^{|E|}$ bound")
    a2.set_xlabel(r"field size $q$")
    a2.set_ylabel("recovery at $h=F$")
    a2.set_ylim(-0.05, 1.08)
    a2.legend(loc="lower right")
    a2.text(-0.28, 1.02, "(b)", transform=a2.transAxes, fontweight="bold", fontsize=10)
    # (c) butterfly: coding delivers the min-cut to both sinks, routing does not
    bx = np.arange(3)
    bvals = [2, 2, 1]
    bcol = [W["blue"], W["blue"], W["orange"]]
    a3.bar(bx, bvals, color=bcol, width=0.6, edgecolor="black", lw=0.6)
    a3.axhline(2, color=W["green"], ls=":", lw=1.3, label="min-cut $=2$")
    a3.set_xticks(bx)
    a3.set_xticklabels(["coding\n$T_1$", "coding\n$T_2$", "routing"], fontsize=7.4)
    a3.set_ylabel("delivered rate (nats)")
    a3.set_ylim(0, 2.5)
    a3.legend(loc="upper right", fontsize=7.0)
    a3.text(-0.30, 1.02, "(c)", transform=a3.transAxes, fontweight="bold", fontsize=10)
    fig.tight_layout()
    save(fig, "fig_n5_rlnc")


if __name__ == "__main__":
    set_style()
    fig_e1()
    fig_e4()
    fig_e6()
    fig_n1()
    fig_n5()
    print("D1 paper figures written to", OUT)
