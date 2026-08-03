"""
plotting.py — Publication-quality matplotlib style and helpers.
Saves every figure as PNG (300 dpi), PDF, and SVG with consistent styling.
"""
from __future__ import annotations

import os
import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402


# Consistent, colour-blind-friendly palette (Wong 2011)
PALETTE = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "yellow": "#F0E442",
    "skyblue": "#56B4E9",
    "black": "#000000",
    "grey": "#7F7F7F",
}
CYCLE = [PALETTE[c] for c in ("blue", "orange", "green", "red", "purple", "skyblue", "yellow")]


def set_style():
    """Apply a consistent publication style."""
    plt.rcParams.update({
        "figure.figsize": (7.0, 4.6),
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "font.size": 12,
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "axes.titlesize": 13,
        "axes.labelsize": 13,
        "axes.linewidth": 0.9,
        "axes.prop_cycle": plt.cycler(color=CYCLE),
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.6,
        "legend.fontsize": 10.5,
        "legend.frameon": True,
        "legend.framealpha": 0.9,
        "legend.edgecolor": "0.8",
        "lines.linewidth": 2.0,
        "lines.markersize": 6,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "pdf.fonttype": 42,   # editable text in PDF
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def savefig_all(fig, path_no_ext: str, formats=("png", "pdf", "svg")):
    """Save a figure to PNG/PDF/SVG. `path_no_ext` has no extension."""
    os.makedirs(os.path.dirname(path_no_ext), exist_ok=True)
    for fmt in formats:
        fig.savefig(f"{path_no_ext}.{fmt}", format=fmt)
    plt.close(fig)
    return [f"{path_no_ext}.{fmt}" for fmt in formats]
