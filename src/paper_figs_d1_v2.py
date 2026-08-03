"""
paper_figs_d1_v2.py — Redesigned D1 paper figures for the reconstructed manuscript.

Design goals (IEEE TIT submission quality):
  * one scientific message per figure;
  * readable in grayscale (every series has a distinct colour AND line style AND
    marker; every bar series has a distinct grey level AND hatch);
  * uniform fonts and line widths across all figures;
  * vector output in PDF and SVG (PNG also written for on-screen preview).

All numbers are read from the frozen experiment data in results/d1/data/.
Nothing is recomputed or invented.
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

# Colour-blind-safe palette (Wong 2011); grayscale separation is carried by
# line style, marker, and hatch so the figures survive black-and-white printing.
C = {
    "blue": "#0072B2", "orange": "#D55E00", "green": "#009E73",
    "grey": "#555555", "lgrey": "#9A9A9A", "black": "#000000",
}


def set_style():
    plt.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 600, "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02, "font.size": 9, "font.family": "serif",
        "mathtext.fontset": "cm", "axes.titlesize": 9, "axes.labelsize": 9,
        "axes.linewidth": 0.8, "axes.grid": True, "grid.alpha": 0.25,
        "grid.linewidth": 0.5, "legend.fontsize": 7.7, "legend.frameon": True,
        "legend.framealpha": 0.95, "legend.edgecolor": "0.7", "legend.handlelength": 2.6,
        "lines.linewidth": 1.7, "lines.markersize": 4.6, "xtick.labelsize": 8,
        "ytick.labelsize": 8, "xtick.direction": "out", "ytick.direction": "out",
        "hatch.linewidth": 0.6, "pdf.fonttype": 42, "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def save(fig, name):
    for fmt in ("pdf", "svg", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{fmt}"), format=fmt)
    plt.close(fig)
    print("wrote", name)


def npz(e):
    return np.load(os.path.join(DATA, f"{e}.npz"), allow_pickle=True)


def js(e):
    with open(os.path.join(DATA, f"{e}.json")) as f:
        return json.load(f)


# --------------------------------------------------------------- Fig: rate sweep
def fig_ratesweep():
    d, j = npz("D1-E1"), js("D1-E1")
    G, th, Em, Ese = d["Gammas"], d["theta"], d["E_meas"], d["E_se"]
    Ecen, Cdib = 2.0, j["C_DIB"]
    fig, ax = plt.subplots(figsize=(3.45, 2.7))
    ax.plot(G, th, color=C["blue"], ls="-", lw=1.9, zorder=2,
            label=r"achievable exponent $\theta_{\mathrm{IB}}(\Gamma_k)$")
    ax.axhline(Ecen, color=C["orange"], ls="--", lw=1.6, zorder=1,
               label=r"centralized ceiling $E^{\mathrm{cen}}=2.00$")
    ax.axvline(Cdib, color=C["grey"], ls=":", lw=1.5, zorder=1,
               label=r"saturation $C_{\mathrm{DIB}}\approx 8.89$")
    ax.errorbar(G, Em, yerr=1.96 * Ese, fmt="o", mfc="white", mec="black",
                ecolor="black", ms=4.0, mew=0.9, elinewidth=0.9, capsize=1.7,
                zorder=3, label=r"measured $E_k$ (optimal detector)")
    ax.set_xlabel(r"cut budget $\Gamma_k$ (nats per channel use)")
    ax.set_ylabel(r"error exponent $E_k$ (nats)")
    ax.set_xlim(0, 12.3)
    ax.set_ylim(0, 2.16)
    ax.legend(loc="lower right", handletextpad=0.5)
    fig.tight_layout()
    save(fig, "fig_ratesweep")


# ------------------------------------------------------------ Fig: genuine network
def fig_network():
    d, j = npz("D1-N1"), js("D1-N1")
    names = j["names"]
    Esr, Ena, th = d["E_sr"], d["E_naive"], float(d["theta_star"])
    G, ssr, sna, ssg = d["sweep_G"], d["sw_sr"], d["sw_naive"], d["sw_single"]
    short = {"complete": "K", "ring": "ring", "path": "path", "star": "star",
             "grid 3x3": "grid", "tree": "tree", "Erdos-Renyi": "ER",
             "Barabasi-Albert": "BA", "Watts-Strogatz": "WS", "grid 2x4": "grid'"}
    lab = [short.get(n, n) for n in names]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.75))
    x = np.arange(len(names))
    w = 0.4
    a1.bar(x - w / 2, Esr, w, facecolor=C["grey"], edgecolor="black", lw=0.6,
           label="network coding")
    a1.bar(x + w / 2, Ena, w, facecolor="white", edgecolor="black", lw=0.6,
           hatch="////", label="naive forwarding")
    a1.axhline(th, color=C["blue"], ls="--", lw=1.5,
               label=rf"$\theta_{{\mathrm{{IB}}}}(\Gamma_k)={th:.3f}$")
    a1.set_xticks(x)
    a1.set_xticklabels(lab, rotation=45, ha="right", fontsize=6.9)
    a1.set_ylabel(r"exponent $E_k$ (nats)")
    a1.set_ylim(0, 0.96)
    a1.legend(loc="lower center", fontsize=6.9, ncol=1)
    a1.set_title(r"(a) ten topologies at matched $\Gamma_k=2.5$", fontsize=8.2)
    a2.plot(G, ssr, color=C["blue"], ls="-", marker="o", markevery=3, ms=3.8,
            label="network coding (attains cut)")
    a2.plot(G, sna, color=C["orange"], ls="--", marker="s", markevery=3, ms=3.6,
            label="naive forwarding")
    a2.plot(G, ssg, color=C["grey"], ls=":", marker="^", markevery=3, ms=3.8,
            label="single path")
    a2.set_xlabel(r"cut budget $\Gamma_k$ (nats)")
    a2.set_ylabel(r"exponent $E_k$ (nats)")
    a2.legend(loc="lower right")
    a2.set_title(r"(b) exponent vs budget on $K_6$", fontsize=8.2)
    fig.tight_layout()
    save(fig, "fig_network")


# ------------------------------------------------------------------- Fig: RLNC code
def fig_rlnc():
    d, j = npz("D1-N5"), js("D1-N5")
    hs, ra = d["hs"], d["rec_a"]
    qs, rb, ho = d["qs"], d["rec_b"], d["ho_b"]
    F = j["F"]
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(7.16, 2.4))
    a1.plot(hs, ra, color=C["blue"], ls="-", marker="o", ms=4.6,
            label="recover-all prob.")
    a1.axvline(F, color=C["orange"], ls="--", lw=1.6, label=rf"min-cut $F={F}$")
    a1.set_xlabel(r"number of descriptions $h$")
    a1.set_ylabel("recovery probability")
    a1.set_ylim(-0.05, 1.09)
    a1.legend(loc="lower left")
    a1.set_title("(a) sharp cut threshold", fontsize=8.2)
    a2.semilogx(qs, rb, color=C["blue"], ls="-", marker="o", ms=4.4,
                label="RLNC recovery")
    a2.semilogx(qs, ho, color=C["grey"], ls="--", marker="s", ms=3.8,
                label=r"$(1-h/q)^{|E|}$ bound")
    a2.set_xlabel(r"field size $q$")
    a2.set_ylabel(r"recovery at $h=F$")
    a2.set_ylim(-0.05, 1.09)
    a2.legend(loc="lower right")
    a2.set_title("(b) field-size reliability", fontsize=8.2)
    bx = np.arange(3)
    a3.bar(bx[:2], [2, 2], facecolor=C["grey"], edgecolor="black", lw=0.6,
           width=0.62, label="network coding")
    a3.bar(bx[2], [1], facecolor="white", edgecolor="black", lw=0.6, width=0.62,
           hatch="////", label="routing")
    a3.axhline(2, color=C["blue"], ls=":", lw=1.4, label="min-cut $=2$")
    a3.set_xticks(bx)
    a3.set_xticklabels([r"sink $T_1$", r"sink $T_2$", "routing"], fontsize=7.4)
    a3.set_ylabel("delivered rate (nats)")
    a3.set_ylim(0, 2.5)
    a3.legend(loc="upper right", fontsize=6.8)
    a3.set_title("(c) butterfly: coding vs routing", fontsize=8.2)
    fig.tight_layout()
    save(fig, "fig_rlnc")


# ------------------------------------------------------------- Fig: water-filling
def fig_waterfill():
    d, j = npz("D1-E4"), js("D1-E4")
    G, twf, teq, Ewf = d["Gammas"], d["theta_wf"], d["theta_eq"], d["E_wf"]
    fig, ax = plt.subplots(figsize=(3.45, 2.7))
    ax.plot(G, twf, color=C["blue"], ls="-", lw=1.9,
            label=r"water-filling $\theta_{\mathrm{IB}}(\Gamma)$")
    ax.plot(G, teq, color=C["orange"], ls="--", lw=1.7, label="equal split")
    ax.plot(G, Ewf, ls="none", marker="o", mfc="white", mec="black", mew=0.9,
            ms=3.8, label=r"measured $E_k$")
    ax.annotate("", xy=(2.4, np.interp(2.4, G, twf)), xytext=(2.4, np.interp(2.4, G, teq)),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color=C["grey"]))
    ax.text(2.65, 0.5 * (np.interp(2.4, G, twf) + np.interp(2.4, G, teq)),
            rf"gain $\leq {j['max_gain']:.3f}$", fontsize=7.4, va="center")
    ax.set_xlabel(r"total budget $\Gamma$ (nats)")
    ax.set_ylabel(r"error exponent (nats)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    save(fig, "fig_waterfill")


# ---------------------------------------------------------- Fig: dynamic topology
def fig_dynamic():
    d = npz("D1-E6")
    pr, gerg = d["per_round"], float(d["gamma_erg"])
    labels = ["min-round\ncut", "ergodic\nmean", "max-round\ncut", "measured"]
    vals = [0.5924, 1.4893, 2.1568, 1.4883]
    faces = ["white", C["grey"], "white", "white"]
    hatches = ["....", "", "xxxx", "////"]
    # single-column, panels stacked vertically for compact placement near the text
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(3.45, 3.75))
    r = np.arange(90)
    a1.step(r, pr[:90], where="mid", color=C["grey"], lw=0.9,
            label="per-round min-cut")
    a1.axhline(gerg, color=C["blue"], ls="--", lw=1.8,
               label=rf"ergodic mean $\bar\Gamma_k={gerg:.2f}$")
    a1.set_xlabel("round $t$")
    a1.set_ylabel("min-cut (nats)")
    a1.set_ylim(0, 5.6)
    a1.legend(loc="upper right", fontsize=7.0)
    a1.set_title("(a) the cut fluctuates every round", fontsize=8.2)
    x = np.arange(len(vals))
    bars = a2.bar(x, vals, width=0.62, edgecolor="black", lw=0.7)
    for b, fc, ht in zip(bars, faces, hatches):
        b.set_facecolor(fc)
        b.set_hatch(ht)
    a2.axhline(1.4883, color=C["blue"], ls=":", lw=1.3)
    for xi, v in zip(x, vals):
        a2.text(xi, v + 0.05, f"{v:.3f}", ha="center", va="bottom", fontsize=7.0)
    a2.set_xticks(x)
    a2.set_xticklabels(labels, fontsize=7.4)
    a2.set_ylabel("predicted exponent (nats)")
    a2.set_ylim(0, 2.6)
    a2.set_title(r"(b) only the ergodic mean predicts $E_k$", fontsize=8.2)
    fig.tight_layout()
    save(fig, "fig_dynamic")


if __name__ == "__main__":
    set_style()
    fig_ratesweep()
    fig_network()
    fig_rlnc()
    fig_waterfill()
    fig_dynamic()
    print("D1 figures (v2) written to", OUT)
