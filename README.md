# Rate-Constrained Decentralized Detection (D1)

Reproducible codebase and theoretical research repository for **Direction 1 (D1): Rate-Constrained Decentralized Detection over Network Topologies**.

## Abstract & Key Theoretical Results

This repository provides the theoretical proofs, numerical simulations, and paper publication assets for rate-constrained hypothesis testing against independence in sensor networks.

### Core Theorems

- **Theorem D1★ (Rate-Connectivity Converse)**:
  Under rate constraints $\mathbf{R} = (R_1, \dots, R_N)$ and topology graph $G=(V,E)$, the optimal decentralized error exponent $E_k$ at decision node $k$ testing against independence is bounded by:
  $$E_k = \min\left\{ E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k) \right\}$$
  where $\theta_{\mathrm{IB}}(\cdot)$ is the Information-Bottleneck curve and $\Gamma_k$ is the min-cut information flow capacity to node $k$.

- **Theorem D1★★ (Type-Preserving Network Coding Achievability)**:
  Demonstrates that Type-Preserving Random Linear Network Coding (RLNC) achieves the optimal error exponent $E_k$ over arbitrary directed acyclic network graphs, outperforming sub-additive naive quantize-and-forward architectures.

---

## Directory Structure

```
.
├── README.md                              # Main documentation & usage guide
├── requirements.txt                       # Python dependencies
├── .gitignore                             # Git ignore rules
├── docs/                                  # Theoretical research bibles & audits
│   ├── D1_Research_Bible_v3.md            # Primary D1 research bible
│   ├── MASTER_D1_HANDBOOK.md              # Master handbook with complete proofs
│   ├── D1_Research_Bible_Rate_..._v1.md   # Initial formulation
│   ├── D1_Research_Bible_Rate_..._v2.md   # Refined formulation
│   ├── PAPER_D1_experimental_section.md   # Manuscript experimental section draft
│   ├── resultsD1.md                       # Comprehensive experiment execution logs
│   └── VALIDATION_AUDIT.md                # Adversarial review gap analysis
├── src/                                   # Core Python simulation engine
│   ├── d1_detect.py                       # Gaussian detector & Lugannani-Rice saddlepoint
│   ├── d1_network.py                      # Multi-hop graph routing & min-cut detector
│   ├── d1_rlnc.py                         # Type-preserving RLNC implementation
│   ├── theory.py                          # IB bounds & water-filling solver
│   ├── topology.py                        # Graph topology generators (NetworkX)
│   ├── stats_utils.py                     # Bootstrap CIs & dispersion fits
│   ├── plotting.py                        # Publication-quality plotting utilities
│   ├── runlog.py                          # Experiment logging engine
│   ├── paper_figs_d1.py                   # Paper figure generator
│   └── paper_figs_d1_v2.py                # Updated paper figure generator
├── experiments/                           # Experiment runners
│   ├── d1_experiments.py                  # Full experiment suite (D1-E1 .. D1-E7)
│   ├── d1_stress.py                       # Stress testing suite (D1-N1 .. D1-N4)
│   └── reproducibility.py                 # Reproducibility validator
├── publication/                           # Publication manuscript assets
│   ├── Latex/                             # main.tex LaTeX source
│   ├── Figures/                           # Vector & raster publication graphics
│   ├── Build/                             # Compilation outputs (PDF, log)
│   ├── Outline/                           # Paper structure outline
│   ├── References/                        # BibTeX citations & literature survey
│   └── Review/                            # Peer review responses
├── configs/                               # JSON experiment snapshots
└── results/                               # Generated experimental data & plots
    ├── data/                              # Array data (.npz) & metadata (.json)
    └── figures/                           # Publication figure outputs (PNG, PDF, SVG)
```

---

## Environment Setup & Reproduction

### Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Experiments

```bash
# Run full D1 experiment suite (parallel execution across cores)
NJOBS=8 python experiments/d1_experiments.py

# Run quick verification smoke test
python experiments/d1_experiments.py --quick

# Run specific experiment subset
python experiments/d1_experiments.py --only E1,E4

# Run reviewer stress testing suite
python experiments/d1_stress.py
```

---

## License & Citation

Private research repository. All rights reserved.
