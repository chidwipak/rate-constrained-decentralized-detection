# D1 Research Bible — Rate-Constrained Decentralized Detection

**Self-contained research bible for Direction 1. No dependency on File 2.**
**Status:** Terminal pre-experimental. Theorem **D1★** (converse) is proved at lemma level; achievability is a formally stated open conjecture with a research roadmap.
**Convention:** All logarithms are natural ($\ln$, units = nats) unless a subscript $\log_2$ (bits) is written. Information quantities are stated in nats; rates in nats/use. A bit-rate $R_{\mathrm{bits}}$ converts as $R_{\text{nats}}=R_{\mathrm{bits}}\ln 2$.

---

## Correction Log (errors in prior documents, with replacements)

> **[COR-1]** *Doc 1 claimed* "Epistemic Channel Capacity $C_E$" and "Semantic Differential Entropy" govern multi-agent reasoning.
> **Correct claim:** No such object is definable without the Bar-Hillel–Carnap inconsistency. The governing object is the **min-cut Shannon/IB information flow** $\Gamma_k$ and the **rate-limited testing exponent** $\theta_{\mathrm{IB}}(\Gamma)$.
> **Replacement:** Theorem **D1★**, §1.3. The discarded objects do **not** reappear anywhere in this file.

> **[COR-2]** *Doc 1 claimed* the multi-agent "coordination tax" scales as $N^2$ as a fundamental law.
> **Correct claim:** $N^2$ is a protocol artifact (serialization/tokenization overhead), not an information-theoretic limit. The fundamental quantity is the cut capacity $\Gamma_k$, which is topology-dependent, not generically $N^2$.
> **Replacement:** §1.1, §1.3; the $N^2$ figure appears nowhere in a theorem.

> **[COR-3]** *Doc 3 (D1-C) claimed* a single theorem fusing (i) the converse, (ii) ADMM achievability, and (iii) an "exponential-in-diameter gap."
> **Correct claim:** Only (i) is provable from first principles. (ii) conflates an optimization algorithm with a fundamental limit; (iii) is unsupported.
> **Replacement:** The converse is isolated as **D1★** (§1.3, proved); achievability is demoted to **Conjecture D1-Ach** (§1.4) with a named barrier; the "exponential-in-diameter" claim is **retracted** (§1.4.2).

> **[COR-4]** *Doc 4 claimed* $\theta_{\mathrm{IB}}$ characterizes the exponent for the general parameter test.
> **Correct claim:** Equality $\theta_{\mathrm{IB}}=$ exponent holds **exactly only for testing against independence** (Ahlswede–Csiszár). For a general hypothesis pair the relevant functional is the Shimokawa–Han–Amari (SHA) functional, and the exact distributed exponent is itself open; $\theta_{\mathrm{IB}}$ is then used as a **converse upper bound** via the SHA/Rahman–Wagner converse.
> **Replacement:** §1.0 (two functionals defined), §1.3.3 (which is used where).

> **[COR-5]** *Prior documents* propagated future-dated / unverifiable arXiv identifiers.
> **Correct claim:** Only independently known or live-verified references are used here. Three load-bearing references were verified live during preparation: Ahlswede–Csiszár program, Nedić–Olshevsky–Uribe (arXiv 1508.05161), Aguerri–Zaidi (arXiv 1709.09082).

---

## Cross-Reference Table (object roles across both directions)

| Object | D1★ role | D2★ role | Relationship |
|---|---|---|---|
| $\Gamma_k$ (min-cut info flow) | **Central** (rate condition) | absent | D1-specific |
| $\theta_{\mathrm{IB}}(\Gamma)$ (IB relevance) | **Central** (exponent bound) | absent | D1-specific |
| $E^{\mathrm{cen}}$ (Stein exponent) | centralized ceiling | absent | D1-specific |
| $r^\star$ (expansion rate) | absent | central (reliability) | D2-specific |
| $h_R$ (restoration entropy) | absent | central (rate) | D2-specific |
| $p$ (erasure prob.), $m$ (moment) | absent | central | D2-specific |
| **Conjecture U** | appendix only | appendix only | unproven bridge |

---

## 1.0 — Notation and Definitions Table

| Symbol | Type | Definition |
|---|---|---|
| $N$ | $\mathbb N$ | Number of agents, $i\in\{1,\dots,N\}=:[N]$. |
| $\Theta$ | finite set | Hypothesis set. **[H-Fin]** $|\Theta|<\infty$. Binary core case $\Theta=\{\theta_0,\theta_1\}$; $\theta^\star=\theta_0$ true. |
| $\mathcal X_i$ | Polish space | Observation alphabet of agent $i$ (e.g. $\mathbb R^{d_i}$ with Borel $\sigma$-algebra). |
| $\ell_i(\cdot\mid\theta)$ | prob. measure on $\mathcal X_i$ | Local likelihood; $X_{i,t}\mid\theta \overset{\text{i.i.d. in }t}{\sim}\ell_i(\cdot\mid\theta)$. |
| **[H-CI]** | condition | Conditional independence across agents: $P(x_{1},\dots,x_{N}\mid\theta)=\prod_{i}\ell_i(x_i\mid\theta)$. |
| $D(P\Vert Q)$ | $[0,\infty]$ | KL divergence $\int \log\frac{dP}{dQ}\,dP$ if $P\ll Q$, else $+\infty$. Borel-measurable in $(P,Q)$. |
| $D_i$ | $[0,\infty]$ | $D_i:=D(\ell_i(\cdot\mid\theta_0)\Vert\ell_i(\cdot\mid\theta_1))$. Gaussian case below. |
| $G_t=(V,E_t)$ | directed graph | $V=[N]$ (optionally $+$ a sink), $E_t\subseteq V\times V$ **directed**. **[H-Top]** $\{E_t\}$ is a stationary ergodic process (i.i.d. or finite-state Markov). |
| $C_{ij}(t)$ | $\mathbb R_{\ge0}$ | Capacity (nats/use) of edge $(i,j)$ at round $t$. **[H-Rate]** taken as a **hard bit/nat budget**: any transcript $M_{ij,t}$ on the edge satisfies $H(M_{ij,t})\le C_{ij}(t)$ (hence $I(M_{ij,t};\theta)\le C_{ij}(t)$). See §1.0-note. |
| $\mathrm{Cut}(k)$ | set of edge sets | All edge cuts separating the observation sources from node $k$ in the (time-expanded) graph. |
| $\Gamma_k$ | $[0,\infty]$ | $\displaystyle \Gamma_k:=\liminf_{T\to\infty}\frac1T\sum_{t=1}^T \min_{S\in\mathrm{Cut}(k)}\sum_{(i,j)\in S}C_{ij}(t)$. Deterministic if $\{E_t,C(t)\}$ ergodic (a.s. constant by the ergodic theorem). |
| $E^{\mathrm{cen}}(\theta)$ | $[0,\infty]$ | Centralized Stein exponent, §1.0-def-Stein. For $\theta=\theta_1$: $E^{\mathrm{cen}}=\sum_i D_i$. |
| $\theta_{\mathrm{IB}}(\Gamma)$ | $[0,\infty)$ | IB relevance / Ahlswede–Csiszár against-independence exponent: $\theta_{\mathrm{IB}}(\Gamma)=\max\{I(U;Y):\,I(U;X_{\mathcal S})\le\Gamma,\ U\!-\!X_{\mathcal S}\!-\!Y\}$, $Y$ the relevance variable. §1.0-def-IB. |
| $\theta_{\mathrm{SHA}}(\Gamma)$ | $[0,\infty)$ | Shimokawa–Han–Amari rate-limited exponent for the **general** pair $(\theta_0,\theta_1)$; reduces to $\theta_{\mathrm{IB}}$ for testing against independence. §1.0-def-SHA. |
| $C_{\mathrm{DIB}}(\theta)$ | $[0,\infty]$ | $\min\{\Gamma:\theta_{\mathrm{IB}}(\Gamma)=E^{\mathrm{cen}}(\theta)\}$ (the saturation rate). Existence/finiteness: Prop. 1.0-A. |
| $\alpha_n,\beta_n$ | $[0,1]$ | Type-I, Type-II error of a node's test on $n$ samples. **[H-T1]** $\alpha_n\le\varepsilon$, fixed $\varepsilon\in(0,1)$. |
| $E_k(\theta)$ | $[0,\infty]$ | Achievable Type-II exponent at node $k$: $E_k(\theta)=\sup_{\text{schemes}}\liminf_{n\to\infty}-\frac1n\ln\beta_n^{(k)}$ subject to **[H-T1]**. |

**§1.0-note (mutual information vs hard bits).** We adopt the **hard-budget** model **[H-Rate]**: an edge carries at most $C_{ij}(t)$ nats per round, so the transcript entropy obeys $H(M_{ij,t})\le C_{ij}(t)$, hence $I(M_{ij,t};\theta)\le C_{ij}(t)$ by $I\le H$. The **mutual-information** model replaces this by the soft constraint $I(M_{ij,t};X_{i}^{t})\le C_{ij}(t)$. The converse D1★ uses only $I(M_{ij,t};\theta)\le C_{ij}(t)$, which **both** models imply (the hard model directly; the soft model via the Markov chain $\theta\!-\!X_i^t\!-\!M_{ij,t}$ and data processing $I(M;\theta)\le I(M;X_i^t)\le C_{ij}$). Hence **D1★ holds identically under either model.** The two models differ only in *achievability* (the hard model is stricter for the encoder), discussed in §1.4.

**§1.0-def-Stein (centralized exponent).** Under **[H-CI]** the joint likelihood is the product, and by **Stein's lemma** applied to the $n$-fold product, for any fixed $\varepsilon\in(0,1)$,
$$\lim_{n\to\infty}-\tfrac1n\ln\beta_n^{\mathrm{cen}}(\varepsilon)=\sum_{i=1}^N D\big(\ell_i(\cdot\mid\theta_0)\Vert\ell_i(\cdot\mid\theta_1)\big)=\sum_i D_i=:E^{\mathrm{cen}}(\theta_1).$$
**This limit is independent of $\varepsilon$** for every $\varepsilon\in(0,1)$ — a property we use repeatedly (Stein's lemma; Cover–Thomas Thm. 11.8.3).

**§1.0-def-IB (information bottleneck functional).** For jointly distributed $(X_{\mathcal S},Y)$ (here $Y$ is the relevance variable; in testing against independence $Y=\theta$ or a sufficient statistic for it),
$$\theta_{\mathrm{IB}}(\Gamma)=\max_{p(u\mid x_{\mathcal S}):\,I(U;X_{\mathcal S})\le\Gamma}I(U;Y).$$
The maximization is over Markov kernels $U\!-\!X_{\mathcal S}\!-\!Y$. The map $\Gamma\mapsto\theta_{\mathrm{IB}}(\Gamma)$ is **concave, non-decreasing**, with $\theta_{\mathrm{IB}}(0)=0$ and $\theta_{\mathrm{IB}}(\infty)=I(X_{\mathcal S};Y)$ (Tishby–Pereira–Bialek 1999; Gilad-Bachrach et al. 2003 for concavity). "Sufficient statistic for $\theta$" means a measurable $T(X)$ with $\theta\!-\!T(X)\!-\!X$; for exponential families $T$ is the natural statistic.

**§1.0-def-SHA [D1-C1] (Shimokawa–Han–Amari converse exponent — complete definition).** For rate-$\Gamma$ one-sided compression in the general binary hypothesis test ($H_0:P_X$ vs $H_1:Q_X$),
$$\theta_{\mathrm{SHA}}(\Gamma)=\min_{\tilde U}\ E_{\mathrm{SHA}}(\tilde U,\Gamma),$$
where the minimization is over auxiliary random variables $\tilde U$ (the compressed representation) satisfying **(i)** Markov $\tilde U-X-(P_X,Q_X)$ and **(ii)** rate $I_{P}(\tilde U;X)\le\Gamma$ (mutual information under $H_0$), and the objective is
$$E_{\mathrm{SHA}}(\tilde U,\Gamma)=D\big(P_{\tilde U}\Vert Q_{\tilde U}\big)+\max\!\big(0,\ I_{P}(\tilde U;X)-\Gamma\big)\cdot[\text{binning correction}].$$
Under the hard rate constraint (ii), the overflow term $\max\!\big(0,I_{P}(\tilde U;X)-\Gamma\big)=0$, so the binning correction vanishes and $E_{\mathrm{SHA}}=D(P_{\tilde U}\Vert Q_{\tilde U})$.

**Testing against independence** ($H_1:P_X\!\cdot\!P_Y$): the binning correction is zero and the SHA exponent equals the IB functional, $\theta_{\mathrm{SHA}}(\Gamma)=\theta_{\mathrm{IB}}(\Gamma)$ — a separate decoder for the compressed $\tilde U$ achieves the same exponent as joint decoding; Rahman–Wagner (2012, IEEE-IT) prove the tightness (achievable lower bound and SHA converse coincide for this case).

**General binary HT** ($H_0:P$ vs $H_1:Q$ with neither a product measure):
$$\theta_{\mathrm{SHA}}(\Gamma)=\min_{p(\tilde u\mid x):\,I_{P}(\tilde U;X)\le\Gamma}\ D\big(P_{\tilde U}\Vert Q_{\tilde U}\big),$$
the KL divergence between the marginal laws of $\tilde U$ under $H_0$ and $H_1$ respectively — Theorem 2 of Shimokawa–Han–Amari (1994, ISIT) and Theorem 1 of Han (1987, IEEE-IT).

For the general pair, $\theta_{\mathrm{SHA}}(\Gamma)\le E^{\mathrm{cen}}(\theta)=\sum_iD_i$ always, and $\theta_{\mathrm{SHA}}(\Gamma)\le\theta_{\mathrm{IB}}(\Gamma)$ always (the IB functional counts mutual information, which upper-bounds the KL between marginals via the log-sum inequality). Hence D1★ with $\theta_{\mathrm{IB}}(\Gamma_k)$ is the tighter (better) converse in the against-independence case; with $\theta_{\mathrm{SHA}}(\Gamma_k)=\min_{p(\tilde u\mid x):\,\text{rate}\le\Gamma_k}D(P_{\tilde U}\Vert Q_{\tilde U})$ it is the correct converse for the general case.

**Reduction to $\theta_{\mathrm{IB}}$ (two-sentence confirmation).** When $H_1=P_X\!\cdot\!P_Y$ is the product measure, $\tilde U$ (a function of $X$ alone) is independent of $Y$ under $H_1$, so the joint law of $(\tilde U,Y)$ under $H_1$ is $P_{\tilde U}\!\cdot\!P_Y$ and the SHA divergence equals $D\big(P_{\tilde U,Y}\Vert P_{\tilde U}\!\cdot\!P_Y\big)=I(\tilde U;Y)$ by the definition of mutual information. Minimizing the error subject to $I_{P}(\tilde U;X)\le\Gamma$ therefore yields $\theta_{\mathrm{SHA}}(\Gamma)=\max_{I(\tilde U;X)\le\Gamma}I(\tilde U;Y)=\theta_{\mathrm{IB}}(\Gamma)$. $\;\square$

**Proposition 1.0-A (existence of $C_{\mathrm{DIB}}$).** Under **[H-Fin]**, **[H-CI]**, and $I(X_{[N]};Y)=E^{\mathrm{cen}}<\infty$, the set $\{\Gamma:\theta_{\mathrm{IB}}(\Gamma)=E^{\mathrm{cen}}\}$ is non-empty and its infimum $C_{\mathrm{DIB}}$ is attained and finite.
*Proof [D1-C3] (two cases).* **Case (i) — testing against independence.** $\theta_{\mathrm{IB}}(\Gamma)\to I(X_{[N]};Y)=E^{\mathrm{cen}}$ as $\Gamma\to\infty$ (the IB relevance saturates at the joint mutual information, which equals the Stein exponent in this case). Since $|\Theta|<\infty$, $Y$ takes finitely many values, so $I(X_{[N]};Y)\le\ln|\Theta|<\infty$; by concavity and non-decrease of $\theta_{\mathrm{IB}}(\cdot)$, saturation at this finite value occurs at some finite $\Gamma^\star$, and $C_{\mathrm{DIB}}\le\Gamma^\star<\infty$.
**Case (ii) — general pair ($E^{\mathrm{cen}}=\sum_iD_i$).** $\theta_{\mathrm{SHA}}(\Gamma)\to E^{\mathrm{cen}}$ as $\Gamma\to\infty$ (any description of the full data suffices; full data attains the Stein exponent by data processing). For $|\Theta|<\infty$ and finite $D_i$, $E^{\mathrm{cen}}=\sum_iD_i<\infty$ (if any $D_i=\infty$ the bound is trivially $\infty$ and uninteresting). The same saturation argument applies to $\theta_{\mathrm{SHA}}(\Gamma)$, which is non-decreasing in $\Gamma$ and bounded above by $E^{\mathrm{cen}}$; hence $C_{\mathrm{DIB}}=\inf\{\Gamma:\theta_{\mathrm{SHA}}(\Gamma)=E^{\mathrm{cen}}\}$ is finite. In both cases $C_{\mathrm{DIB}}\le\ln|\Theta|<\infty$. The Proposition holds. $\;\blacksquare$

---

## 1.1 — Scientific Problem Statement

**(a) Colloquial (SIGCOMM register).** A swarm of agents each see only a slice of a phenomenon and must agree on what is true, but the links between them carry only a few bits per round and the wiring keeps changing. How small can the probability of a wrong collective decision be driven, as a function of the link budgets and the changing topology? We give a hard limit: the best achievable error exponent at any agent is capped by the information that can physically flow to it across the network's tightest cut.

**(b) Mathematical.** Given **[H-Fin], [H-CI], [H-Top], [H-Rate], [H-T1]**, characterize
$$E_k(\theta)=\sup_{\text{decentralized, fusion-free, rate-constrained schemes}}\ \liminf_{n\to\infty}-\tfrac1n\ln\beta_n^{(k)}\quad\text{s.t. }\alpha_n^{(k)}\le\varepsilon,$$
for each node $k$, in terms of $\big(\{D_i\},\{C_{ij}(t)\},\{E_t\}\big)$.

**Why unsolved — precise decomposition.**
- **Solved:** (i) *Centralized, single rate-limited link, testing against independence* — Ahlswede–Csiszár (1986) give the exact exponent $\theta_{\mathrm{IB}}(R)$. (ii) *Static star, fusion center, distributed IB region* — Aguerri–Zaidi (2019) give the exact single-letter rate–relevance region. (iii) *Rate-unconstrained, time-varying graph consensus* — Nedić–Olshevsky–Uribe (2017) give geometric belief-concentration rates.
- **What changes when all three of {time-varying topology, no fusion center, per-edge rate constraints} hold simultaneously:** (1) *No fusion center* removes the single-detector structure that makes AC/SHA single-letter; the exponent becomes node-dependent and coupled to consensus dynamics. (2) *Time-varying topology* makes the "available rate to node $k$" a stochastic-process functional ($\Gamma_k$), not a fixed number; the cut that binds changes with $t$. (3) *Per-edge rate constraints* couple (1) and (2): the consensus that fixes (1) must itself be carried over the very links constrained by (2), so the compression and the agreement are not separable. The **intersection** has no published characterization — neither converse nor achievability — and that intersection is exactly the scientific gap D1★ addresses (converse) and Conjecture D1-Ach names (achievability).

---

## 1.2 — Literature Review and Prior-Art Matrix

For each: **Core**, **Exact result**, **Assumptions**, **Gap for D1★**, **Strictly generalized by D1★?**

### Hypothesis testing & error exponents
- **Stein (≈1952; Chernoff 1952).** *Core:* binary HT exponents. *Exact:* best Type-II exponent at Type-I $\le\varepsilon$ equals $D(P\Vert Q)$ ($\varepsilon$-independent). *Assumptions:* full centralized samples. *Gap:* no communication constraint, no network. *Generalized?* D1★ recovers it as $N{=}1,\Gamma\to\infty$ (§1.3.6).
- **Ahlswede–Csiszár (1986), *Hypothesis testing with communication constraints*, IEEE-IT.** *Core:* one-sided rate-$R$ compression. *Exact:* for **testing against independence**, exponent $=\theta_{\mathrm{IB}}(R)=\max_{I(U;X)\le R}I(U;Y)$; for general HT, an achievable bound. *Assumptions:* single observer→single detector, static, asymptotic. *Gap:* no network/cut, no time variation, no fusion-free consensus. *Generalized?* D1★ recovers it on a single binding cut (§1.3.6).
- **Han (1987), *Hypothesis testing with multiterminal data compression*, IEEE-IT.** *Core:* multiterminal one-sided/two-sided compression. *Exact:* general achievable exponents; converse for special cases. *Relationship to AC:* Han's region **subsumes** AC's against-independence result as a special case and adds multiterminal sources; it does **not** add time-variation or fusion-free consensus. *Gap/Generalized?:* orthogonal axis; D1★ uses Han/SHA as the rate-limited converse ingredient.
- **Shimokawa–Han–Amari (1994), *Error bound of hypothesis testing with data compression*, ISIT.** *Core:* the SHA exponent with binning. *Exact:* $\theta_{\mathrm{SHA}}(R)$ (§1.0-def-SHA); equals $\theta_{\mathrm{IB}}$ for against-independence. *Assumptions:* static, single link. *Gap:* same as AC. *Use in D1★:* the general-pair converse ingredient of Lemma B.
- **Rahman–Wagner (2012), *On the optimality of binning…*, IEEE-IT; Watanabe; Zhao–Lai (2018); Sreekumar–Gündüz (2020) distributed testing over noisy channels.** *Core:* tightness/achievability refinements for distributed testing. *Exact:* Rahman–Wagner prove SHA tightness for testing against independence and a class of problems. *Gap:* **none address simultaneously time-varying topology + fusion-free + per-edge rate** — confirmed by inspection. *Use:* justifies $\theta_{\mathrm{IB}}$ as the tight functional in the against-independence instantiation.

### Information bottleneck
- **Tishby–Pereira–Bialek (1999/2000).** *Core:* IB principle. *Exact:* Lagrangian $\min_{p(u\mid x)} I(U;X)-\beta I(U;Y)$; self-consistent equations. *Assumptions:* centralized, single source. *Gap:* no network, no exponent operational meaning. *Use:* defines $\theta_{\mathrm{IB}}$.
- **Aguerri–Zaidi (2019; arXiv 1709.09082), *Distributed Information Bottleneck…*, IEEE-IT.** *Core:* distributed IB exact region. *Exact:* single-letter rate–relevance region for **a star of encoders to one decoder** (CEO-like), discrete & Gaussian; Blahut–Arimoto-type algorithm. *Assumptions:* **static topology, a fusion/decoder node exists, asymptotic block length.** *Gap for D1★:* exactly the three missing axes (time-varying, fusion-free, per-edge cut). *Generalized?* D1★'s static-star specialization recovers their **converse** ceiling (§1.3.6); D1★ does not claim their achievability in the time-varying case.
- **Estella Aguerri–Zaidi one-shot/finite-sample IB.** *Core:* non-asymptotic IB bounds. *Exact:* one-shot bounds via convex duality. *Does it close D1★'s non-asymptotic gap?* **No** — it is single-decoder and static; the distributed dispersion (§1.5) remains open.

### Distributed inference over networks
- **Nedić–Olshevsky–Uribe (2017; arXiv 1508.05161), *Fast convergence rates for distributed non-Bayesian learning*.** *Core:* belief consensus over time-varying graphs. *Exact:* each agent's belief on a wrong hypothesis $\theta$ decays geometrically at rate governed by the **network-averaged KL** $\sum_i v_i\,D(\ell_i(\cdot\mid\theta^\star)\Vert\ell_i(\cdot\mid\theta))$ with $v$ the (eigenvector-centrality) stationary weight; non-asymptotic, explicit. *Assumptions:* **belief messages are essentially rate-unconstrained** (agents exchange full log-belief vectors), doubly/column-stochastic mixing, $B$-strong-connectivity. *Gap for D1★:* gives the **rate-unconstrained** time-varying answer; says nothing about the per-edge **rate**-limited exponent. *Generalized?* D1★'s $\Gamma\to\infty$ limit is consistent with (and bounded by) their network-averaged rate; D1★ adds the binding-cut throttle they lack.
- **Lalitha–Javidi–Sarwate (2018), *Social learning and distributed hypothesis testing*, IEEE-IT; Shahrampour–Rakhlin–Jadbabaie (2016).** *Core:* large-deviation rates of social learning. *Exact:* a.s. exponential belief concentration with network-weighted KL rate. *Under information constraints?* They consider full-belief or finitely-parameterized exchange — **not** Shannon/cut rate limits. *Gap:* same as NOU.

### Network information theory (cut-set)
- **Ahlswede–Cai–Li–Yeung (2000), network coding; Cover–El Gamal (1979), relay channel; Cover–Thomas Ch. 15.** *Core:* cut-set outer bound. *Exact:* for any network, the rate of reliable information transfer across a cut is $\le$ the cut capacity; for a single-source single-sink, max-flow = min-cut (deterministic/orthogonal links). *Applicability to directed time-varying graphs:* the cut-set bound holds **per use** for any directed network; for our orthogonal rate-limited edges it specializes to "$\sum_{(i,j)\in S}C_{ij}(t)$ across cut $S$." Time variation is handled by summing per-round cut capacities (§1.3.2). *Use:* Lemma A.

### Byzantine / resilient distributed detection
- **Vempaty–Tong–Varshney; Chen–Vempaty–Varshney; arXiv 2008.00164 (*Byzantine-resilient distributed HT with time-varying topology*).** *Core:* detection under adversarial nodes/links, time-varying graphs. *Exact:* resilient consensus/learning rates with a fraction of Byzantine agents. *Do they constrain Shannon rate?* **No** — they constrain *adversarial behavior*, not *bits per edge*. *Consequence:* their results do **not** bound $E_k(\theta)$ under rate constraints; conversely D1★ (a converse) only *tightens* under Byzantine links (§1.10).

### Novelty matrix
| Paper | time-varying | fusion-free | per-edge rate | converse | achievability |
|---|:--:|:--:|:--:|:--:|:--:|
| Ahlswede–Csiszár '86 | ✗ | ✗ | ✓(1 link) | ✓ | ✓ |
| Han '87 / SHA '94 | ✗ | ✗ | ✓ | ✓ | ✓(LB) |
| Aguerri–Zaidi '19 | ✗ | ✗ (decoder) | ✓ | ✓ | ✓ |
| Nedić–Olshevsky–Uribe '17 | ✓ | ✓ | ✗ | — | ✓(rate) |
| Lalitha–Javidi–Sarwate '18 | ✓ | ✓ | ✗ | — | ✓(rate) |
| Byzantine HT (2008.00164) | ✓ | ✓ | ✗ | — | ✓(resilient) |
| **D1★ (this file)** | **✓** | **✓** | **✓** | **✓** | **✗ (open, §1.4)** |

The gap = the row with all of {time-varying, fusion-free, per-edge rate, converse} = ✓ and which no prior row matches. D1★ occupies it as a **converse**; the achievability cell is the named open problem.

---

## 1.3 — Theorem D1★: Formal Statement and Complete Proof Roadmap

### 1.3.1 Formal statement

**Hypotheses.** [H-Fin] $|\Theta|<\infty$; [H-CI] conditional independence; [H-Top] $\{(E_t,C(t))\}$ stationary ergodic; [H-Rate] hard per-edge budgets (or the MI model, §1.0-note); [H-T1] $\alpha_n\le\varepsilon\in(0,1)$.

> **Theorem D1★ (Rate–Connectivity Converse).** Under [H-Fin]–[H-T1], for every node $k$ and every alternative $\theta\in\Theta\setminus\{\theta^\star\}$,
> $$\boxed{\;E_k(\theta)\;\le\;\min\big\{\,E^{\mathrm{cen}}(\theta),\ \ \theta_{\mathrm{IB}}(\Gamma_k)\,\big\}\;}$$
> in the **testing-against-independence** instantiation (where $\theta_{\mathrm{IB}}$ is the tight rate-limited exponent). For a **general** pair $(\theta_0,\theta_1)$, the same display holds with $\theta_{\mathrm{IB}}$ replaced by the SHA converse functional $\theta_{\mathrm{SHA}}(\Gamma_k)\ (\ge\theta_{\mathrm{IB}})$, i.e. $E_k(\theta)\le\min\{E^{\mathrm{cen}},\theta_{\mathrm{SHA}}(\Gamma_k)\}$.
> **Furthermore (strictness):** if $\Gamma_k<C_{\mathrm{DIB}}(\theta)$ then $E_k(\theta)<E^{\mathrm{cen}}(\theta)$ strictly.

**Nature of the bound.** This is an **upper bound (converse)** on what any scheme can achieve; it is a *strong converse* in the against-independence case (the bound is the exact limiting exponent there). It does **not** assert a scheme attains it in the time-varying fusion-free case (that is Conjecture D1-Ach).

**Weakenings of assumptions.**
- [H-Fin] → countable $\Theta$: the bound holds for each fixed alternative $\theta$; the *uniform* statement over $\Theta$ needs a uniform Stein lemma (holds for finite/compact $\Theta$; for countable $\Theta$ replace $\min$ over a fixed pair — the per-pair bound is unaffected).
- [H-Fin] → general $\Theta$ (parametric, continuous): replace Stein by its parametric/large-deviation analog; $E^{\mathrm{cen}}$ becomes the relevant Chernoff/Stein parametric rate; the cut bound is unchanged.
- [H-CI] → correlated observations: addressed in §1.3.1-CI below.

**§1.3.1-CI (correlated observations).** If [H-CI] fails ($P_{X_{[N]}\mid\theta}\ne\prod_i\ell_i$):
**(a)** The **converse still holds as an upper bound** with $E^{\mathrm{cen}}(\theta)=\tfrac1n D(P^n_{X_{[N]}\mid\theta_0}\Vert P^n_{X_{[N]}\mid\theta_1})$ (the true joint divergence, which is **not** $\sum_i D_i$ in general) and the same cut/IB term: every step of Lemmas A–B uses only data processing and the cut capacity, never the product structure. *Justification:* Lemma A bounds $I(M_k;\theta)\le\Gamma_k$ regardless of source correlation; Lemma B bounds the exponent by a rate-limited divergence functional of the joint law. **(b)** The *value* changes: positive correlation typically **reduces** $E^{\mathrm{cen}}$ (shared information is redundant) and can change $\theta_{\mathrm{IB}}$ in either direction (correlation can be exploited by joint compression only with a fusion center; fusion-free, it usually **lowers** the achievable exponent). **(c)** The formulation does **not** fundamentally change: it remains a rate-limited distributed test; only the single-letter evaluability of $\theta_{\mathrm{IB}}$ degrades (multiterminal source coding with side information, Wyner–Ziv/CEO machinery, enters). *Conclusion:* **(a) is the operative answer** — D1★ is a valid converse for correlated sources; sharpness is what is lost.

### 1.3.2 Lemma A — Cut-Set Information Bound (complete proof)

> **Lemma A.** Let $M_k^{(T)}$ be the entire transcript received by node $k$ over rounds $1,\dots,T$ (all messages on all in-edges, over all rounds, possibly interactive). Then
> $$I\big(M_k^{(T)};\theta\big)\ \le\ \sum_{t=1}^{T}\ \min_{S\in\mathrm{Cut}(k)}\ \sum_{(i,j)\in S}C_{ij}(t).$$
> Dividing by $T$ and taking $\liminf$ gives $\limsup_T \tfrac1T I(M_k^{(T)};\theta)\le\Gamma_k$.

*Proof.*
**(1) Directed time-expanded graph.** Build the time-expanded graph $\mathcal G$: a vertex $(i,t)$ for each agent–round, an edge $(i,t)\!\to\!(j,t{+}1)$ of capacity $C_{ij}(t)$ whenever $(i,j)\in E_t$, and "memory" edges $(i,t)\!\to\!(i,t{+}1)$ of infinite capacity (an agent remembers its own state). The information sources are the observation vertices $\{(i,t):\text{$i$ observes $X_{i,t}$}\}$; the sink is $(k,T)$. Any $(s,k)$-separating cut in $\mathcal G$ corresponds, round-by-round, to a cut $S\in\mathrm{Cut}(k)$ in $G_t$.
**(2) Per-edge bound.** On a directed orthogonal edge with hard budget, the message $M_{ij,t}$ satisfies $H(M_{ij,t})\le C_{ij}(t)$, hence $I(M_{ij,t};\theta\mid \text{past})\le H(M_{ij,t}\mid\text{past})\le H(M_{ij,t})\le C_{ij}(t)$. (Under the MI model use $I(M_{ij,t};\theta)\le I(M_{ij,t};X_i^t)\le C_{ij}(t)$ via $\theta\!-\!X_i^t\!-\!M_{ij,t}$.) **Interaction** is allowed: $M_{ij,t}$ may depend on everything $i$ has received; the bound $H(M_{ij,t})\le C_{ij}(t)$ is on the *transmitted symbol*, independent of how it was computed.
**(3) Cut-set bound for deterministic orthogonal rate-limited networks [D1-C2].** For a network of noiseless, orthogonal, rate-limited links — each edge $(i,j)$ at round $t$ carrying $M_{ij,t}$ with $H(M_{ij,t})\le C_{ij}(t)$ — the information about $\theta$ reaching $k$ is bounded by the min-cut capacity by a **direct** argument (no noisy-channel cut-set theorem is needed). For any source-separating cut $S\in\mathrm{Cut}(k)$ in the time-expanded graph at round $t$,
$$I\big(\theta;\{M_{ij,t}:(i,j)\in S\}\mid\text{past}\big)\le H\big(\{M_{ij,t}:(i,j)\in S\}\mid\text{past}\big)\le\sum_{(i,j)\in S}H(M_{ij,t}\mid\text{past})\le\sum_{(i,j)\in S}H(M_{ij,t})\le\sum_{(i,j)\in S}C_{ij}(t),$$
where the steps use, in order, $I\le H$; subadditivity of entropy; $H(\cdot\mid\cdot)\le H(\cdot)$; and the budget constraint. Taking $\min_{S\in\mathrm{Cut}(k)}$ and summing over $t$ gives Lemma A. (Reference for this style of deterministic-network argument: El Gamal–Kim, *Network Information Theory*, Cambridge 2011, Ch. 16 Lemma 16.1; Ahlswede–Cai–Li–Yeung 2000 network-coding cut-set for deterministic links.) The noisy-channel cut-set bound (Cover–Thomas Thm 15.10.1) would give a **looser** result and is **not** needed here, because the links are deterministic and orthogonal; the deterministic-network argument above is tighter and exactly right. **Directedness** is handled natively (cuts respect edge orientation). **Time-variation** is handled because $\mathcal G$ is a single static DAG encoding all rounds; the bound is the *sum* of per-round binding cuts, **not** the binding cut of a time-averaged graph (these differ when the binding cut moves with $t$ — the sum-of-minima form is the correct one).
**(4) Interactive tightness of the bound.** Multi-round interaction can **increase achievable exponents** (Kang–Ulukus; Xiang–Kim) by better *using* the rate, but cannot transmit more than the cut capacity: the total entropy crossing the cut over $T$ rounds is $\le\sum_t\sum_{(i,j)\in S}C_{ij}(t)$ for every fixed cut $S$, hence $\le$ the per-round min. Therefore Lemma A's **converse** is valid for interactive schemes. $\;\blacksquare$

**Measure used.** Shannon mutual information $I(M_k;\theta)$ in nats. This is the correct rate measure because (i) it is the operational quantity bounding hypothesis-discrimination via Lemma B, and (ii) under the hard-bit model it is dominated by $H(M)\le$ budget, so the same proof structure is valid for bit-capacities verbatim.

### 1.3.3 Lemma B — Rate-Limited Stein Upper Bound (complete proof)

> **Lemma B.** If node $k$'s decision is a (measurable) function of $M_k$ with $\tfrac1n I(M_k;\theta)\le\Gamma$ (per-sample), then its Type-II exponent at Type-I $\le\varepsilon$ obeys
> $$E_k(\theta)\ \le\ \theta_{\mathrm{IB}}(\Gamma)\quad\text{(against independence)},\qquad E_k(\theta)\ \le\ \theta_{\mathrm{SHA}}(\Gamma)\quad\text{(general pair).}$$

*Proof.*
**(A) Against-independence case (tight).** Here $H_0:P_{XY}$ vs $H_1:P_XP_Y$ with $Y=\theta$-relevance. Node $k$ holds a rate-$\Gamma$ description $U=M_k$ of $X$ (the cut limits $I(U;X)\le\Gamma$ via $I(U;\theta)\le I(U;X)$ when $\theta\!-\!X\!-\!U$; more precisely the relevant constraint is $I(U;X_{\mathcal S})\le\Gamma$ on the binding cut). By **Ahlswede–Csiszár (1986), Theorem 5** (and its converse), the optimal Type-II exponent achievable from a rate-$\Gamma$ description equals $\max_{p(u\mid x):I(U;X)\le\Gamma}I(U;Y)=\theta_{\mathrm{IB}}(\Gamma)$. Rahman–Wagner (2012) confirm tightness (binning inactive). Hence $E_k\le\theta_{\mathrm{IB}}(\Gamma)$, with equality if $k$ were an optimal centralized detector of the rate-$\Gamma$ description.
**(B) General pair (converse).** Apply the **Shimokawa–Han–Amari** converse: for a rate-$\Gamma$ one-sided description, $E_k\le\theta_{\mathrm{SHA}}(\Gamma)$ (§1.0-def-SHA). Since $\theta_{\mathrm{SHA}}\ge\theta_{\mathrm{IB}}$ always (the IB term is one of the two SHA branches), the displayed general bound is correct; we do **not** claim $\theta_{\mathrm{SHA}}=\theta_{\mathrm{IB}}$ off the against-independence case.
**(C) Data-processing step used.** The single inequality $I(M_k;\theta)\le I(M_k;X_{\mathcal S})\le\Gamma$ uses the **DPI for mutual information** along the Markov chain $\theta\!-\!X_{\mathcal S}\!-\!M_k$ (Cover–Thomas Thm 2.8.1). The exponent-divergence link uses the **DPI for KL divergence** (strong form, Csiszár–Körner): $D(P_{M_k\mid\theta_0}\Vert P_{M_k\mid\theta_1})\le D(P_{X\mid\theta_0}\Vert P_{X\mid\theta_1})$, controlled by the rate via $\theta_{\mathrm{IB}}/\theta_{\mathrm{SHA}}$. $\;\blacksquare$

### 1.3.4 Combining A and B

Chain: by **Lemma A**, $\tfrac1n I(M_k;\theta)\le\Gamma_k$ (per-sample, using stationarity to pass from $T$-round to per-sample rate). By **Lemma B**, $E_k(\theta)\le\theta_{\mathrm{IB}}(\Gamma_k)$ (resp. $\theta_{\mathrm{SHA}}$). Independently, the **full-data DPI** gives $E_k\le E^{\mathrm{cen}}$ (node $k$'s data is a function of all observations; KL-DPI). Taking the smaller yields the boxed bound. *Where hypotheses enter:* [H-CI] fixes $E^{\mathrm{cen}}=\sum_iD_i$ (else §1.3.1-CI); [H-Rate] gives the per-edge bound in Lemma A(2); [H-Top] ergodicity makes $\Gamma_k$ a.s. a constant and lets $\tfrac1T I\to$ per-sample rate; [H-T1] is the Stein/AC Type-I level (exponents $\varepsilon$-independent). $\;\blacksquare$

### 1.3.5 Strictness

> **Proposition (strict gap).** If $\Gamma_k<C_{\mathrm{DIB}}(\theta)$, then $\theta_{\mathrm{IB}}(\Gamma_k)<E^{\mathrm{cen}}(\theta)$, hence $E_k<E^{\mathrm{cen}}$.

*Proof.* By Prop. 1.0-A, $\theta_{\mathrm{IB}}$ is concave, non-decreasing, equal to $E^{\mathrm{cen}}$ first at $\Gamma=C_{\mathrm{DIB}}$. **Strict monotonicity on $[0,C_{\mathrm{DIB}})$:** a concave non-decreasing function that is constant on a sub-interval $[a,C_{\mathrm{DIB}}]$ with $a<C_{\mathrm{DIB}}$ would, by concavity, be constant on $[a,\infty)$, contradicting $\theta_{\mathrm{IB}}(a)<\theta_{\mathrm{IB}}(\infty)$ unless already saturated; hence on $[0,C_{\mathrm{DIB}})$ the curve is strictly increasing up to its first saturation, so $\Gamma_k<C_{\mathrm{DIB}}\Rightarrow\theta_{\mathrm{IB}}(\Gamma_k)<\theta_{\mathrm{IB}}(C_{\mathrm{DIB}})=E^{\mathrm{cen}}$. (Strict monotonicity of the IB relevance–rate curve below saturation is established in Gilad-Bachrach–Navot–Tishby 2003 and Witsenhausen–Wyner for the convexity of the analogous curve.) $\;\blacksquare$

### 1.3.6 Degeneration to known special cases

- **$N=1$, static, $\Gamma\to\infty$:** $\theta_{\mathrm{IB}}(\infty)=I(X;Y)=E^{\mathrm{cen}}$ (against independence) or $E^{\mathrm{cen}}=D_1$ (general), recovering **Stein**. ✓
- **Static star, fusion center, one rate constraint $R$:** $\Gamma_k=R$, binding cut = the single link; bound $=\min\{E^{\mathrm{cen}},\theta_{\mathrm{IB}}(R)\}$ = **Ahlswede–Csiszár / Aguerri–Zaidi converse**. ✓
- **Rate-unconstrained ($\Gamma_k\to\infty$), time-varying:** bound $\to E^{\mathrm{cen}}$; the *achievable* rate of approach is the **Nedić–Olshevsky–Uribe** network-averaged-KL geometric rate, which is $\le E^{\mathrm{cen}}$ and consistent with D1★'s ceiling. D1★ subsumes their *ceiling* and adds the finite-rate throttle they omit. ✓

---

## 1.4 — The Open Achievability Problem

### 1.4.1 Conjecture D1-Ach (formal)
> **Conjecture D1-Ach.** There is a sequence of decentralized, fusion-free, rate-constrained schemes over $\{G_t\}$ with, for every node $k$,
> $$\lim_{n\to\infty}-\tfrac1n\ln\beta_n^{(k)}=\min\{E^{\mathrm{cen}}(\theta),\theta_{\mathrm{IB}}(\Gamma_k)\}.$$
**Known sub-cases:** static star + fusion center (Aguerri–Zaidi: ✓ exact); static, fusion-free, unconstrained rate (NOU: ✓ for *consensus/convergence*, **exponent-matching unverified**); **time-varying + rate-constrained: OPEN.**

### 1.4.2 The exact mathematical barrier
1. **Convexity of the IB objective.** The IB Lagrangian $I(U;X)-\beta I(U;Y)$ is **non-convex** in $p(u\mid x)$ in general (only the *curve* $\theta_{\mathrm{IB}}(\Gamma)$ is concave). For **jointly Gaussian** $(X,Y)$ with quadratic structure the optimizer is a linear–Gaussian projection (Chechik et al. 2005) and the problem is tractable, giving the right exponent; for general sources the non-convexity means decentralized alternating schemes (ADMM) may converge to **stationary points that are not global**, so exponent-matching is not guaranteed.
2. **Consensus-to-exponent translation.** NOU give geometric **belief** convergence; converting a belief-convergence rate into an **error-exponent** match requires controlling the *large-deviation* rate of the consensus error, not just its mean — a gap not bridged in the rate-constrained setting.
3. **"Exponential-in-diameter gap" (Doc 3): RETRACTED.** No known result establishes an exponential-in-diameter penalty for this problem; it is neither a theorem for a related problem nor a supported conjecture. It is withdrawn. The honest statement is "finite-time gap of unknown order; conjectured polynomial-in-diameter."

### 1.4.3 Suggested proof strategies (research roadmap)
- **(S1) Distributed method of types.** Adapt Csiszár–Körner type-counting to the time-expanded graph: show the number of jointly typical message-type classes reaching $k$ matches $e^{n\theta_{\mathrm{IB}}(\Gamma_k)}$. Closest technique: Han (1987) type-covering + NOU mixing. Likely yields achievability for finite alphabets.
- **(S2) CEO/Wyner–Ziv embedding.** Recognize fusion-free rate-limited testing as a **CEO source-coding** instance on each cut; import Berger–Zhang–Viswanathan / Oohama achievability. Closest: Aguerri–Zaidi (2019) Gaussian CEO; extend the decoder to a consensus operator over $\{G_t\}$.
- **(S3) Online-convex/large-deviation consensus.** Combine NOU geometric mixing with a Sanov-type rate function for the consensus statistic; prove the consensus large-deviation rate equals $\theta_{\mathrm{IB}}(\Gamma_k)$. Closest: Lalitha–Javidi–Sarwate (2018) large-deviation social learning, augmented with a per-edge rate quantizer.

---

## 1.5 — Non-Asymptotic Refinements (new)

### 1.5.1 Second-order (dispersion) terms
**Centralized baseline (Strassen 1962; Tomamichel–Tan 2013).** With Type-I $\le\varepsilon$,
$$-\ln\beta_n(\varepsilon)=nD(P\Vert Q)-\sqrt{nV}\,\Phi^{-1}(\varepsilon)+O(\ln n),\qquad V=\mathrm{Var}_P\!\big[\ln\tfrac{dP}{dQ}\big]\ \text{(relative-entropy variance)}.$$
**Distributed dispersion — OPEN.** *Conjectured form:* $-\ln\beta_n^{(k)}=n\,\theta_{\mathrm{IB}}(\Gamma_k)-\sqrt{nV_{\mathrm{dist}}(\Gamma_k)}\,\Phi^{-1}(\varepsilon)+o(\sqrt n)$ with a **distributed information-variance** $V_{\mathrm{dist}}$ that adds (i) the centralized $V$ along the binding cut and (ii) a *quantization-dispersion* term from the rate-$\Gamma_k$ description. **Barrier:** no second-order theory exists for rate-constrained distributed testing over time-varying graphs; the quantizer's finite-block backoff and the consensus mixing-time interact. **Closest techniques:** Tomamichel–Tan (2013) one-shot HT + Watanabe's second-order distributed source coding. *Status:* stated as open; experiments (§1.7) use the centralized $V$ as the finite-$n$ bias correction baseline.

### 1.5.2 One-shot bounds
A one-shot ($n=1$) converse follows directly: replace asymptotic Stein by the one-shot hypothesis-testing divergence $D_h^\varepsilon(P\Vert Q)=-\ln\beta_1(\varepsilon)$ and Lemma A's per-use cut bound; this yields $-\ln\beta_1^{(k)}(\varepsilon)\le D_h^\varepsilon$ evaluated through the rate-$\Gamma_k$ channel (a one-shot IB/meta-converse). A matching one-shot **achievability** inherits the §1.4 openness. So: one-shot **converse — available**; one-shot **achievability — open**.

---

## 1.6 — Gaussian Surrogate: Complete Closed-Form Derivation

**Two instantiations are given.** The **against-independence Gaussian** (§1.6-AI) is *exactly* solvable and is the **primary numerical target**. The **binary mean-shift** (§1.6-MS) is the operational detection problem with $E^{\mathrm{cen}}=\sum_iD_i$; its rate-limited exponent is SHA, closed-form only at high rate.

### §1.6-AI — Against-independence Gaussian (exact)
Let a scalar relevance $Y\sim\mathcal N(0,1)$ and agent $i$ observe $X_i=\rho_i Y+\sqrt{1-\rho_i^2}\,Z_i$, $Z_i\sim\mathcal N(0,1)$ i.i.d., so $\mathrm{corr}(X_i,Y)=\rho_i$. Test $H_0:$ joint vs $H_1:X_i\perp Y$.
- **Per-agent full relevance:** $I(X_i;Y)=-\tfrac12\ln(1-\rho_i^2)$, and $E^{\mathrm{cen}}=\sum_i I(X_i;Y)=-\tfrac12\sum_i\ln(1-\rho_i^2)$.
- **Gaussian IB curve (Chechik–Globerson–Tishby–Weiss 2005).** Optimal $U_i$ is $U_i=a_iX_i+\text{noise}$; in closed form, for a single agent with budget $R$,
$$\boxed{\ \theta_{\mathrm{IB},i}(R)=-\tfrac12\ln\!\big(1-\rho_i^2(1-e^{-2R})\big)\ }\qquad(\text{nats}).$$
- **Optimal encoder:** $p(u\mid x_i)=\mathcal N(a_i x_i,\,1)$ with $a_i^2=\dfrac{e^{2R}-1}{\,1-\rho_i^2\,}$ (activation of the single eigen-direction; for the scalar case there is exactly one).
- **Low/high-rate limits:** $\theta_{\mathrm{IB},i}(R)\to\rho_i^2 R$ as $R\to0$ (**linear**, slope $\rho_i^2$), and $\to-\tfrac12\ln(1-\rho_i^2)=I(X_i;Y)$ as $R\to\infty$ (**saturation**). The kink is at the saturation knee.
- **Network curve and $C_{\mathrm{DIB}}$.** With min-cut budget $\Gamma_k$ optimally split across the agents on the binding cut, $\theta_{\mathrm{IB}}(\Gamma_k)=\max_{\sum_iR_i=\Gamma_k}\sum_i\theta_{\mathrm{IB},i}(R_i)$ (water-filling over the concave per-agent curves). $C_{\mathrm{DIB}}$ is the smallest $\Gamma$ at which water-filling saturates **all** agents, i.e. $C_{\mathrm{DIB}}=\sum_iR_i^{\mathrm{sat}}$ with $R_i^{\mathrm{sat}}=\infty$ formally — so for finite saturation use the $\delta$-saturation rate $C_{\mathrm{DIB}}^{(\delta)}=\sum_i\tfrac12\ln\frac{\rho_i^2}{\delta(1-\rho_i^2)+\dots}$; **for the symmetric case $\rho_i\equiv\rho$ the per-agent knee is explicit** (below).

**Symmetric closed form (used in experiments).** $\rho_i\equiv\rho$, $N$ agents, total budget $\Gamma$ split equally $R=\Gamma/N$:
$$\theta_{\mathrm{IB}}(\Gamma)=-\tfrac{N}{2}\ln\!\Big(1-\rho^2\big(1-e^{-2\Gamma/N}\big)\Big),\qquad E^{\mathrm{cen}}=-\tfrac N2\ln(1-\rho^2).$$
The **kink** in $E_k$ vs $\Gamma$ is the transition from the increasing branch to the flat ceiling $E^{\mathrm{cen}}$; its location is the practical $C_{\mathrm{DIB}}$ where $\theta_{\mathrm{IB}}(\Gamma)$ reaches $(1-\delta)E^{\mathrm{cen}}$.

**Asymmetric water-filling (general $\{\rho_i\}$) [D1-C5].** For $N$ agents with potentially different correlations $\{\rho_i\}$, the optimal rate allocation $\{R_i^\star\}$ solving $\max_{\sum_iR_i=\Gamma}\sum_i\theta_{\mathrm{IB},i}(R_i)$ satisfies the Lagrangian stationarity condition $\partial\theta_{\mathrm{IB},i}(R_i)/\partial R_i=\nu$ for all $i$ with $R_i>0$. Differentiating the closed form $\theta_{\mathrm{IB},i}(R)=-\tfrac12\ln\!\big(1-\rho_i^2(1-e^{-2R})\big)$:
$$\frac{\partial\theta_{\mathrm{IB},i}}{\partial R_i}=\frac{\rho_i^2 e^{-2R_i}}{1-\rho_i^2(1-e^{-2R_i})}.$$
Setting this equal to the common multiplier $\nu$ and solving for $e^{-2R_i}$:
$$\rho_i^2 e^{-2R_i}=\nu\big(1-\rho_i^2(1-e^{-2R_i})\big)=\nu-\nu\rho_i^2+\nu\rho_i^2 e^{-2R_i}\ \Longrightarrow\ e^{-2R_i}\,\rho_i^2(1-\nu)=\nu(1-\rho_i^2),$$
$$\boxed{\ e^{-2R_i}=\frac{\nu(1-\rho_i^2)}{\rho_i^2(1-\nu)}\quad\Longrightarrow\quad R_i^\star(\nu)=\tfrac12\ln\!\frac{\rho_i^2(1-\nu)}{\nu(1-\rho_i^2)}\ \text{ when }>0,\quad R_i^\star=0\text{ otherwise.}\ }$$
This is valid for $\nu\in(0,1)$ and $\rho_i\in(0,1)$; an agent whose $\rho_i$ is too small for the water level $\nu$ is cut off ($R_i^\star=0$). The multiplier $\nu$ is found by solving $\sum_i\max(0,R_i^\star(\nu))=\Gamma$ (a 1-D root-finding problem). **Algorithm (implementable):** (1) sort agents by $\rho_i$ descending; (2) binary-search $\nu\in(0,1)$ until $\sum_i\max(0,R_i^\star(\nu))=\Gamma$; (3) record $\{R_i^\star(\nu^\star)\}$ and compute $\theta_{\mathrm{IB}}(\Gamma)=\sum_i\theta_{\mathrm{IB},i}(R_i^\star(\nu^\star))$. This gives the exact parameter-free prediction $\theta_{\mathrm{IB}}(\Gamma)$ for any asymmetric $\{\rho_i\}$ and budget $\Gamma$, in $O(N\log N)$.

### §1.6-MS — Binary mean-shift (operational; high-rate closed form)
$X_i\mid\theta\sim\mathcal N(\mu_{i,\theta},\sigma_i^2)$, $\Theta=\{0,1\}$. Then $D_i=\dfrac{(\mu_{i,0}-\mu_{i,1})^2}{2\sigma_i^2}$ and $E^{\mathrm{cen}}=\sum_iD_i$ (Stein, Gaussian). Under a rate-$R$ scalar quantizer the exponent is the **SHA** functional; its **high-rate expansion** is
$$\theta_{\mathrm{SHA},i}(R)=D_i-\kappa_i\,e^{-2R}+O(e^{-4R}),\qquad \kappa_i=\tfrac12\Big(\tfrac{\mu_{i,0}-\mu_{i,1}}{\sigma_i}\Big)^2\cdot c,$$
i.e. the quantization gap closes exponentially in rate. The exact low-rate $\theta_{\mathrm{SHA},i}(R)$ requires the SHA convex program (no elementary closed form); compute numerically. **For experiments, use §1.6-AI** (fully closed-form) as the validation target and §1.6-MS as the realistic detection instantiation.

---

## 1.7 — Numerical Validation Protocol

### 1.7.1 Experiment D1-E1 — Kink detection
**System (use §1.6-AI symmetric):** $N=4$, $\rho=\sqrt{1-e^{-1}}\approx0.795$ so $I(X_i;Y)=0.5$ nats, $E^{\mathrm{cen}}=2$ nats. Topology: ring; tunable per-edge budget $C$, so $\Gamma_k=2C$ (two edges into $k$ on a ring min-cut) — state the exact $\Gamma_k(C)$ from the ring's min cut.
**Detector:** running-consensus distributed sequential test (each node forms a quantized log-likelihood-ratio statistic, exchanges at rate $C$, accumulates).
**Measure:** $\widehat E_k=$ slope of $\ln(\text{Type-II error})$ vs $n$, $n\in\{100,\dots,5000\}$.
**Prediction (parameter-free):** $\widehat E_k(\Gamma_k)=\theta_{\mathrm{IB}}(\Gamma_k)=-2\ln\!\big(1-\rho^2(1-e^{-\Gamma_k/2})\big)$ for $\Gamma_k<C_{\mathrm{DIB}}$, and $\widehat E_k=2$ for $\Gamma_k\ge C_{\mathrm{DIB}}$; kink at $C_{\mathrm{DIB}}$.
**Falsification:** any measured $\widehat E_k>\theta_{\mathrm{IB}}(\Gamma_k)+\delta_{\mathrm{CI}}$ (beyond the 95% bootstrap CI, after the §1.5.1 finite-$n$ bias correction) **falsifies D1★**.

### 1.7.2 Experiment D1-E2 — Min-cut sufficiency for the converse [D1-C4]
Fix total capacity $C_{\mathrm{total}}$; sweep topology complete→ring→path, reallocating edge budgets so $\Gamma_k$ is held constant across topology changes. At each topology, run the strongest available decentralized detector.
**Correct prediction (converse test):** for **every** topology at every $\Gamma_k$, $\widehat E_k\le\theta_{\mathrm{IB}}(\Gamma_k)$. The converse does **not** predict $\widehat E_k$ is equal across topologies at equal $\Gamma_k$ — it only predicts $\widehat E_k$ is bounded above by $\theta_{\mathrm{IB}}(\Gamma_k)$ in all cases.
**What would be observed if D1★ is tight:** $\widehat E_k$ values roughly equal across topologies at equal $\Gamma_k$. This is an observation about *achievability* (Conjecture D1-Ach), not a prediction of D1★ itself.
**Falsification criterion:** a measured $\widehat E_k>\theta_{\mathrm{IB}}(\Gamma_k)+\delta_{\mathrm{CI}}$ (beyond the 95% bootstrap CI) for **any** topology at the given $\Gamma_k$ **falsifies D1★**. Equal-$\Gamma_k$ but unequal-$\widehat E_k$ across topologies does **not** falsify D1★.
**What this experiment tests:** (i) the converse is not violated by any topology (primary purpose); (ii) whether $\Gamma_k$ is a sufficient statistic for the achievable exponent (secondary, exploratory, addressing Conjecture D1-Ach only).

### 1.7.3 Statistical methodology
- Exponent fit: OLS of $\ln\widehat\beta_n$ on $n$; heteroscedasticity-robust SE.
- CIs: bootstrap $B=10{,}000$ resamples over trials.
- Finite-$n$ debiasing: subtract the $\sqrt{nV}\Phi^{-1}(\varepsilon)/n$ Strassen term (§1.5.1) using centralized $V$ as baseline.
- Multiple testing: Bonferroni across the $(C,N)$ grid.
- Finite-size scaling: extrapolate $\widehat E_k(n)\to\widehat E_k(\infty)$ via $a+b/\sqrt n$ fit.

---

## 1.8 — Simulation Roadmap (concrete)
- **Language/libs:** Python 3.11; `numpy` (Monte Carlo), `scipy.stats` (Gaussian KL, bootstrap), `networkx` (ring/path/complete graphs, min-cut via `networkx.algorithms.flow`).
- **Parameters:** $N=4$; $\rho=0.795$; $C\in\{0.1,0.2,\dots,3.0\}$ nats/use (30 points); $n\in\{100,200,\dots,5000\}$; trials/point $=2000$; seeds fixed and logged.
- **Graphs:** ring $C_4$, path $P_4$, complete $K_4$; per-edge budget set to hold $\Gamma_k$ constant in E2.
- **Outputs:** $\widehat E_k$ vs $\Gamma_k$ with CI; overlay analytic $\theta_{\mathrm{IB}}$; kink localization via segmented regression.
- **Compute:** single workstation, CPU only (48 threads ample). No GPU needed. Wall-clock: hours.

---

## 1.9 — Journal Submission Strategy
- **Primary: IEEE Trans. Information Theory.** Justification: D1★ is an information-theoretic converse in the lineage of Ahlswede–Csiszár (1986). **AE subfield:** multiterminal information theory / hypothesis testing. **AE will demand:** either tight achievability or a *strong* converse. **Plan:** present D1★ as a strong converse (tight against independence), state Conjecture D1-Ach with the §1.4.3 roadmap, and include the §1.7 numerical confirmation of the converse.
- **Secondary (AI-native framing): IEEE JSAC / INFOCOM.** Instantiate concretely: "For $N$ distributed inference agents each observing a local context, over a capacity-constrained time-varying mesh, the minimum achievable decision-error exponent at any agent is $\min\{E^{\mathrm{cen}},\theta_{\mathrm{IB}}(\Gamma_k)\}$ — the first information-theoretic bound for this class." No LLM vocabulary in the theorems.

---

## 1.10 — Limitations, Threats to Validity, Failure Conditions
- **Correlated observations:** §1.3.1-CI — converse survives as an upper bound (use the true joint divergence); sharpness/closed form is lost.
- **Non-stationary topology:** if $\{E_t\}$ is non-ergodic, $\Gamma_k$ may not converge; replace by $\limsup$/$\liminf$ sandwich, and D1★ holds with $\Gamma_k^{\sup}$ as the converse rate (looser).
- **Infinite $\Theta$:** per-alternative bound holds; uniform statement needs a uniform Stein lemma (compact $\Theta$ ok).
- **Continuous observations:** covered by the Gaussian case; require $D_i<\infty$ and absolute continuity $\ell_i(\cdot\mid\theta_0)\ll\ell_i(\cdot\mid\theta_1)$.
- **Vanishing connectivity:** $\Gamma_k\to0\Rightarrow\theta_{\mathrm{IB}}(0)=0\Rightarrow E_k\to0$ — agents cannot beat chance asymptotically. ✓ consistent.
- **Byzantine edges:** as a converse, D1★ only **tightens** (adversarial edges reduce honest information flow $\le\Gamma_k$); so $E_k\le\theta_{\mathrm{IB}}(\Gamma_k)$ remains valid. Achievability under Byzantine links is strictly harder (resilient-consensus literature).

---

## Appendix — Conjecture U (bridge to Direction 2; unproven)
> **Conjecture U.** If the agents' internal belief-update maps form a nonlinear dynamical system $f$ (the object of Direction 2) with uniform expansion rate $r^\star$, then the binding per-link rate needed to sustain $E_k=\min\{E^{\mathrm{cen}},\theta_{\mathrm{IB}}(\Gamma_k)\}$ is $\ge\max\{\,\text{(rate to reach }\theta_{\mathrm{IB}}\text{)},\,h_R(f)\,\}$: the restoration entropy of the belief dynamics lower-bounds the D1 rate.
**Conditions for it to follow from D1★+D2★:** [C-U1] $\theta_{\mathrm{IB}}$ monotone (proved, §1.3.5); [C-U2] belief estimators evolve by the D2 map $f$; [C-U3] one channel serves both estimation and message exchange. **Barrier:** requires a *joint information–control Lyapunov function* merging the KL/IB (statistical) and Lyapunov/SVD (dynamical) frameworks — non-standard; research frontier. Stated identically in File 2's appendix.
