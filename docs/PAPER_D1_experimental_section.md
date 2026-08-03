# Direction 1 — Paper-Ready Experimental Section

**Rate-Constrained Decentralized Detection: empirical validation of Theorems D1★ (converse) and D1★★ (achievability).**

> Companion to `D1_Research_Bible_v3.md`. Full per-experiment logs in `resultsD1.md`; raw data in
> `results/d1/data/`; figures in `results/d1/figures/` (PNG/PDF/SVG). All quantities in nats.

---

## 1. Setup

We validate the closed-loop result $E_k(\theta)=\min\{E^{\mathrm{cen}},\ \theta_{\mathrm{IB}}(\Gamma_k)\}$
for testing against independence on the Gaussian instantiation of §1.6-AI. We use the **self-consistent
form** of the model — $N$ agents each observing an *independent* relevance pair $(X_i,Y_i)$ with
$X_i=\rho_i Y_i+\sqrt{1-\rho_i^2}\,Z_i$ — under which the bible's identities
$E^{\mathrm{cen}}=\sum_i I(X_i;Y_i)$, $\theta_{\mathrm{IB}}(\Gamma)=\max_{\sum_iR_i=\Gamma}\sum_i\theta_{\mathrm{IB},i}(R_i)$,
and the water-filling allocation all hold exactly (a shared-$Y$ reading would instead give
$E^{\mathrm{cen}}=I(X_{1:N};Y)$; we state this explicitly as a clarification of the bible).

**Exponent measurement.** The naive Monte-Carlo protocol of §1.8 cannot reach $\beta_n\sim e^{-2n}$. We instead
compute the **exact finite-$n$ error of the optimal (Neyman–Pearson) detector** by a saddlepoint
(Lugannani–Rice) evaluation of the per-sample log-likelihood-ratio CGF — a Gaussian quadratic form with
closed-form CGF $K(s)=-\tfrac12\ln\det(I-2s\,\Sigma M)+sc$ — computed in log-space for numerical stability.
We cross-checked it against plain Monte-Carlo wherever $\beta_n$ is directly measurable ($\gtrsim10^{-5}$):
agreement ratios were $0.99$–$1.02$. The asymptotic exponent is extracted by a dispersion-corrected fit
$-\ln\beta_n=an+b\sqrt n+c$ that removes the $O(\sqrt n)$ Strassen term.

Base parameters: $\rho=\sqrt{1-e^{-1}}\approx0.795$ ($I(X_i;Y)=0.5$ nat, $E^{\mathrm{cen}}(N{=}4)=2$ nats),
Type-I level $\varepsilon=0.05$ unless swept.

## 2. Results

| Exp. | Claim tested | Key metric | Result |
|---|---|---|---|
| **D1-E1** | $E_k=\theta_{\mathrm{IB}}(\Gamma)$ (achiev.), $\le E^{\mathrm{cen}}$ (converse) | MAE, max over-shoot | **0.0011 nats**, $-0.0011$ (never exceeds) |
| **D1-E2** | $\theta_{\mathrm{IB}}$ is a genuine upper envelope | max $I(U;Y)-\theta_{\mathrm{IB}}(I(U;X))$ | $-3.3\times10^{-3}$ (no scheme crosses it) |
| **D1-E3** | $\Gamma_k$ is a sufficient statistic (10 topologies) | exponent spread at fixed $\Gamma_k$ | **0.0000 nats** |
| **D1-E4** | water-filling optimal allocation | max gain over equal split; fit MAE | 0.3045 nats; 0.0010 |
| **D1-E5** | agent scaling (fixed $R$ vs fixed $\Gamma$) | MAE both regimes | 0.0011 / 0.0012 |
| **D1-E6** | time-varying: ergodic-mean cut | $|E_{\rm meas}-\theta_{\mathrm{IB}}(\bar\Gamma_k)|$ | 0.001 ($\bar\Gamma_k=2.895$) |
| **D1-E7** | 2nd-order dispersion (§1.5.1) | $V$ recovered; coeff MAE | 0.16 %; 0.0013 |

**Headline.** Across a 0.2–12 nat rate sweep the measured exponent lies on $\theta_{\mathrm{IB}}(\Gamma)$ to
$\le0.002$ nats and never exceeds the $E^{\mathrm{cen}}$ ceiling — a simultaneous confirmation of the
achievability D1★★ and the converse D1★. Holding the min-cut $\Gamma_k$ fixed while sweeping the topology
across complete / ring / path / star / grid / tree / Erdős–Rényi / Barabási–Albert / Watts–Strogatz / directed
graphs collapses all ten exponents to a single value (spread $0.0000$ nats): $\Gamma_k$ — and nothing else
about the graph — determines the achievable exponent.

## 3. Paper-ready figure captions

- **Fig. D1-E1** (`D1-E1_rate_sweep`). *Measured error exponent (black, saddlepoint with 95 % CIs) versus cut
  budget $\Gamma_k$ for $N{=}4$ Gaussian agents ($\rho=0.795$, $E^{\mathrm{cen}}=2$ nats). The measurement
  tracks the closed-form $\theta_{\mathrm{IB}}(\Gamma)$ (blue, achievability D1★★) to $<0.002$ nats and never
  exceeds the centralized ceiling $E^{\mathrm{cen}}$ (orange dashed, converse D1★). The knee $C_{\mathrm{DIB}}$
  (green dotted) marks the practical saturation.*
- **Fig. D1-E2** (`D1-E2_converse_schemes`). *Every rate-$R$ scheme respects the converse. Uniform (squares) and
  Lloyd–Max (triangles) scalar quantizers, plotted at their operating point $(I(U;X),I(U;Y))$, lie on or below
  the IB relevance–rate envelope $\theta_{\mathrm{IB}}(R)$ (blue). No scheme crosses the envelope
  (max violation $-3.3\times10^{-3}$); only the soft IB test channel attains it.*
- **Fig. D1-E3** (`D1-E3_topology_suff`). *Min-cut sufficiency. With edge budgets scaled so $\Gamma_k=3$ across
  ten topologies (including random ER/BA/WS and a directed graph), the measured exponents collapse onto
  $\theta_{\mathrm{IB}}(\Gamma_k)$ (spread $0.0000$ nats): topology matters only through the cut.*
- **Fig. D1-E4** (`D1-E4_waterfilling`). *Heterogeneous informativeness $\{0.95,0.85,0.7,0.5\}$: optimal
  water-filling (blue) beats equal splitting (orange) by up to 0.30 nats; the measured exponent (black) matches
  the water-filling prediction to 0.001 nats.*
- **Fig. D1-E5** (`D1-E5_scaling`). *Agent scaling. (a) Fixed per-agent rate: exponent grows linearly in $N$.
  (b) Fixed total budget $\Gamma=2$: the shared-cut throttle bends the exponent as agents are starved of rate.*
- **Fig. D1-E6** (`D1-E6_dynamic_topology`). *Time-varying topology. (a) Per-round min-cut fluctuates; (b) only
  the ergodic mean $\bar\Gamma_k=2.90$ predicts the measured exponent (1.488 vs $\theta_{\mathrm{IB}}=1.489$);
  min- or max-round cuts mispredict.*
- **Fig. D1-E7** (`D1-E7_dispersion`). *Second-order dispersion. (a) $-\ln\beta_n$ for five Type-I levels obeys
  $n\theta_{\mathrm{IB}}-\sqrt{nV}\,\Phi^{-1}(\varepsilon)+O(\ln n)$; (b) the $\sqrt n$ coefficient is linear in
  $\Phi^{-1}(\varepsilon)$ with slope $\sqrt V$; the analytic relative-entropy variance $V=1.598$ is recovered
  to 0.16 %.*
- **Fig. D1-N5** (`D1-N5_rlnc_achievability`). *Achievability with an actual GF(q) random linear network code
  (fusion-free = multicast). (a) The code recovers all $h$ source descriptions exactly when $h\le F$ (the
  min-cut) and fails beyond — RLNC attains precisely $\Gamma_k$. (b) Recovery probability $\to1$ as the field
  size $q$ grows, above the $(1-h/q)^{|E|}$ Ho bound. (c) On the butterfly the code delivers the min-cut 2 to
  both sinks while edge-disjoint routing delivers only 1 — network coding is genuinely necessary for the
  fusion-free setting; cyclic/time-varying graphs are handled by the time-expanded DAG.*

*(The full adversarial-validation figure set — D1-N1 genuine routing, D1-N2 scale to $N=1000$, D1-N3 discrete
converse, D1-N4 edge cases, D1-N5 RLNC — is catalogued with confidences in `VALIDATION_AUDIT.md`.)*

## 4. Discoveries, improvements, and reviewer pre-emption

1. **Model disambiguation (improvement).** §1.6-AI must use *independent per-agent relevance* $Y_i$ for the
   stated identities; with a shared $Y$, $E^{\mathrm{cen}}=\tfrac12\ln(1+N\rho^2/(1-\rho^2))\ne\sum_iI(X_i;Y)$.
   Recommend the bible state the parallel-channel instantiation explicitly.
2. **Measurement methodology (improvement).** The §1.8 naive-MC exponent protocol is infeasible ($\beta_n\sim
   e^{-2n}$). The exact saddlepoint detector-error + dispersion-corrected fit is the correct instrument and
   should replace it; we validate it against MC in the measurable regime.
3. **Converse is an envelope, not a value (clarification).** D1-E2 shows $\theta_{\mathrm{IB}}$ upper-bounds
   *all* quantizers, separating the converse (envelope) from achievability (only the soft IB channel is tight).
4. **Sufficient-statistic strength (new evidence).** The exact $0.0000$-nat topology collapse (E3) is stronger
   than the bible's ring/path check and directly answers "does structure matter beyond the cut?" — no.

## 5. Limitations & threats to validity

- Validated target is **testing against independence** with conditionally-independent Gaussian observations
  (the domain where D1★★ is tight). The **general-pair** ($\theta_{\mathrm{SHA}}$) exponent is a structurally
  different problem and is *not* claimed (consistent with the bible's scope).
- Exponents are the **exact optimal-detector** error (Neyman–Pearson); we do not simulate a specific
  finite-complexity distributed protocol (TPNC network coding) — the achievability is verified at the
  information-theoretic optimum, not for a particular code.
- The **distributed** dispersion $V_{\mathrm{dist}}$ (§1.5.1) is open; E7 validates the centralized-along-the-cut
  variance $V$ that forms its baseline component.
- Correlated observations, Byzantine edges, and non-ergodic topologies are covered qualitatively by the bible's
  §1.10; only the ergodic i.i.d.-topology case is measured here (E6).

## 6. Future work

- Genuine finite-blocklength **distributed dispersion** $V_{\mathrm{dist}}(\Gamma_k)$ (cut-variance +
  quantization-dispersion).
- A concrete **TPNC network-coding decoder** simulation on a cyclic time-varying graph (approach the exponent
  with an explicit code, not just the optimal detector).
- **General-pair** SHA converse validation and the Markov-topology (non-i.i.d. but stationary-ergodic) cut.
- A binary/bounded-relevance instantiation exhibiting a **hard finite-rate kink** at $C_{\mathrm{DIB}}$.
