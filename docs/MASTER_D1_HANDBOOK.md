# MASTER HANDBOOK — DIRECTION 1
## Rate-Constrained Decentralized Detection

> **Purpose of this document.** This is an *internal master handbook*, written by the first author, whose
> single job is to teach a future reader — assumed to remember *nothing* beyond undergraduate mathematics —
> everything needed to **understand, derive, defend, and answer reviewer questions** about Direction 1 (D1).
> It is deliberately long and repetitive. It explains intuition *before* mathematics, every time.
>
> **Source of truth.** Everything here is grounded in the repository files:
> `D1_Research_Bible_v3.md` (the theory), `code/theory.py`, `code/d1_detect.py`, `code/topology.py`,
> `code/d1_network.py`, `code/d1_rlnc.py` (the implementations), `resultsD1.md` (the experiment logs),
> `VALIDATION_AUDIT.md` (the adversarial validation), and the figures in `results/d1/figures/`.
> Where a claim cannot be verified from those files, the text says so explicitly.
>
> **Convention (memorize this first).** *All logarithms are natural logarithms* ($\ln$). The unit of
> information is therefore the **nat**, not the bit. One nat $= 1/\ln 2 \approx 1.4427$ bits. A rate written
> "$R$ nats/use" means $R$ nats of information per channel use. This convention is inherited from the bible
> and is used by every formula and every line of code in the project.

---

# SECTION 1 — THE BIG PICTURE (plain English, almost no mathematics)

## 1.1 A story to fix the setting

Imagine a swarm of small drones spread over a wide area after an earthquake. Each drone can see only a small
patch of ground beneath it. Some patches look like rubble, some look like intact buildings, some look like
fires. No single drone can see enough to decide the one question the rescue team actually cares about, which
we will call the **hypothesis**: *"Is the situation state A (say, 'the dam upstream has failed and water is
coming') or state B ('the dam is fine')?"*

Each drone individually has only weak, noisy evidence. Drone 7 sees slightly more water than usual; drone 12
sees mud where there should be grass. Individually, none of these observations is conclusive. But *together*,
if the drones could pool everything they see, the combined evidence might be overwhelming — the collective
could be almost certain.

Here is the catch, and it is the whole point of Direction 1:

1. **The drones cannot pool everything.** The radio links between them are tiny. A drone can send only a
   handful of bits to its neighbors each second. It physically cannot transmit its full camera image.
2. **There is no control tower.** There is no central computer that collects all the data and decides. Each
   drone must reach its *own* decision using only what trickles across the network to it. (We call this
   **fusion-free**: no fusion center.)
3. **The network keeps changing.** Drones move, links drop and reappear, the wiring is different every second.

The scientific question of D1 is: **given these three constraints, how good can the collective decision
possibly be?** More precisely: *how quickly can the probability of a wrong decision be driven to zero as the
drones collect more samples over time, and what physical quantity sets the ultimate limit?*

## 1.2 Why "how quickly" and not just "how likely"

If you take more and more independent measurements of something, the probability of guessing wrong typically
shrinks *exponentially* in the number of measurements $n$. That is, the error probability behaves like
$e^{-nE}$ for some positive number $E$. The number $E$ is called the **error exponent**. A large $E$ means
error vanishes fast (good); a small $E$ means it vanishes slowly (bad); $E = 0$ means it does not vanish at all
(you can never become sure — you are stuck at coin-flip quality forever).

So the right way to grade a distributed detection scheme is **not** "what is its error probability" (that
depends on how long you run it) but "**what is its error exponent** $E$" — the *rate* at which error decays.
D1 is entirely about characterizing the best achievable error exponent $E_k$ at each node $k$.

**Why exponents and not raw probabilities?** Because exponents are the *intrinsic, sample-count-independent*
grade of a detector. Two schemes both reach error $10^{-6}$, but one needed 100 samples and the other needed
10,000 — the first has a $100\times$ larger exponent and is fundamentally better. The exponent is the clean
figure of merit that a *fundamental limit* can be stated about.

## 1.3 The one-sentence answer (the punchline of the whole direction)

The best error exponent any node $k$ can achieve is:

> **the smaller of two things: (a) the exponent it could get with unlimited communication, and (b) the
> exponent permitted by the amount of information that can physically flow to it across the network's tightest
> bottleneck.**

In symbols (do not worry about the symbols yet, they are defined later):

$$ E_k \;=\; \min\{\,E^{\mathrm{cen}},\ \theta_{\mathrm{IB}}(\Gamma_k)\,\}. $$

- $E^{\mathrm{cen}}$ = the "unlimited communication" ceiling. If every drone could share everything, this is the
  best exponent (the **cen**tralized exponent). It is a property of the *statistics* of the evidence, nothing
  to do with the network.
- $\Gamma_k$ = the **bottleneck**. It is the maximum *rate of information* (nats per round) that can reach node
  $k$ from everyone else, limited by the narrowest cut of the changing network. This is a property of the
  *network*, nothing to do with the statistics.
- $\theta_{\mathrm{IB}}(\Gamma_k)$ = a function that translates "information rate that reaches you" into "best
  possible exponent given that rate." It is the bridge between the two worlds. `IB` stands for **Information
  Bottleneck**; we will meet it properly later.

The word "$\min$" is the entire story: **you are limited by whichever is scarcer — your statistical evidence or
your communication pipe.** If the pipe is wide ($\Gamma_k$ large), you are limited by statistics and you get
$E^{\mathrm{cen}}$. If the pipe is narrow, you are limited by the pipe and you get the smaller
$\theta_{\mathrm{IB}}(\Gamma_k)$.

## 1.4 Why is this important / where does it appear in practice

- **Distributed sensing / sensor networks.** Exactly the drone story: many cheap sensors, thin radios, no
  central server, must reach a common conclusion (intruder present? pipeline leaking? seismic event?).
- **"AI-native" networks / multi-agent inference.** A modern re-reading (the bible's secondary framing, §1.9):
  many inference agents, each holding a slice of context, connected by a bandwidth-limited, ever-changing mesh,
  must agree on a decision. The theorem says the minimum achievable decision-error exponent at any agent is
  $\min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$ — a hard limit on how good coordinated multi-agent
  inference can be, set by the communication cut. (The bible is careful: *no LLM vocabulary appears in the
  theorems*; the framing is just an application.)
- **Datacenter / edge fleets.** Machines observing local telemetry, deciding a global condition (is the cluster
  under attack?) over congested links.

The practical value is a **design law**: it tells an engineer *exactly* how much link budget $\Gamma_k$ is
needed to reach a target decision quality, and tells them that beyond the saturation point $C_{\mathrm{DIB}}$
(defined later) *buying more bandwidth is wasted* because you have hit the statistical ceiling
$E^{\mathrm{cen}}$. Symmetrically, below that point, *more agents without more bandwidth does not help* — you
are throttled by the shared cut.

## 1.5 What motivated the research / what exactly is the gap

Three neighboring results already existed before this work (details in Section 5). Each solves *part* of the
problem:

1. **Ahlswede–Csiszár (1986):** *one* sensor, compressing to *one* detector over *one* rate-limited link, on a
   *fixed* setup — they found the exact exponent for "testing against independence," and it is exactly the
   function $\theta_{\mathrm{IB}}(R)$. But: one link, one detector, static.
2. **Aguerri–Zaidi (2019):** *many* sensors compressing to *one* fusion center (a star), static — exact
   rate-vs-relevance region. But: there *is* a fusion center, and the topology is fixed.
3. **Nedić–Olshevsky–Uribe (2017):** *many* agents, *no* fusion center, *changing* topology — but with
   essentially *unlimited* communication (agents swap full belief vectors). Exact geometric convergence rate.
   But: no rate limit.

**The gap** is the *intersection nobody had done*: **time-varying topology AND no fusion center AND a hard
per-edge rate limit, all at once.** Each existing result switches off exactly the ingredient that makes the
others hard. When all three are on simultaneously, the "available rate to node $k$" is no longer a fixed
number — it is a random, time-averaged, cut-of-a-changing-graph quantity ($\Gamma_k$); the exponent becomes
*node-dependent*; and the compression and the agreement can no longer be separated because the messages that
build agreement must themselves squeeze through the very links being rate-limited.

That intersection is the central scientific question of D1, and the contribution is to **close it**: prove a
matching upper bound (converse, Theorem **D1★**) and lower bound (achievability, Theorem **D1★★**) that meet
at $\min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$, for the "testing against independence" version of
the problem, over *general time-varying directed graphs that may contain cycles*.

## 1.6 What we are actually trying to prove (two halves)

A "fundamental limit" is always two theorems that sandwich the truth:

- **Converse (D1★): "you cannot do better than this."** No scheme, however clever, can achieve an exponent
  above $\min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$. This is an *impossibility* result. It is
  proven by a chain of inequalities that hold for *any* scheme.
- **Achievability (D1★★): "you can actually reach this."** There is an explicit scheme (Type-Preserving
  Network Coding — quantize into an information-bottleneck code, then carry the pieces across the graph with
  random linear network coding) whose exponent *equals* the bound. This is a *construction*.

When the converse and the achievability meet with **zero gap**, the problem is *solved* — the true answer is
known exactly, not just bounded. D1 achieves zero gap for testing against independence. The rest of this
handbook explains every piece of that sentence.

## 1.7 A crucial honesty note carried throughout

The bible (and this handbook) is scrupulous about *scope*. The clean, closed answer
$\min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$ is exact for the specific statistical problem called
**testing against independence** (defined in Section 4). For a *general* pair of hypotheses, the right-hand
functional is a different, harder object (called $\theta_{\mathrm{SHA}}$), the exact distributed exponent is
itself an open problem in the literature, and D1★ then provides only an *upper bound* (converse), not a
matching achievability. This is not a weakness hidden under the rug — it is stated up front, and the
experiments are careful to test only what is actually claimed. Keeping "against independence" vs "general pair"
straight is the single most important discipline for defending this work.

---

# SECTION 2 — REQUIRED BACKGROUND (taught from near zero)

This section teaches every prerequisite. Each concept is introduced with **intuition first**, then a
**minimal, self-contained mathematical statement**, then a **tiny numerical example**, and finally a note on
**where it is used in D1**. Read it linearly; later concepts build on earlier ones.

## 2.1 Probability, random variables, expectation (the floor)

**Intuition.** A *random variable* is a quantity whose value is uncertain; a *probability distribution*
describes how likely each value is. The *expectation* (mean) is the long-run average.

**Minimal math.** A discrete random variable $X$ takes values $x$ with probabilities $p(x) \ge 0$,
$\sum_x p(x) = 1$. Its expectation is $\mathbb E[X] = \sum_x x\, p(x)$. For a continuous $X$ with density
$f(x)$, replace sums by integrals: $\mathbb E[X] = \int x f(x)\,dx$. The *variance* is
$\mathrm{Var}(X) = \mathbb E[(X-\mathbb E X)^2]$, a measure of spread.

**The Gaussian (normal) distribution** is the workhorse of D1's concrete model. We write
$X \sim \mathcal N(\mu, \sigma^2)$ for a Gaussian with mean $\mu$ and variance $\sigma^2$; its density is
$f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\!\big(-\frac{(x-\mu)^2}{2\sigma^2}\big)$. The *standard* normal is
$\mathcal N(0,1)$.

**Two Gaussian facts we reuse constantly:**
- *Jointly Gaussian* variables are fully described by their means and their *covariance matrix* $\Sigma$
  (entries $\Sigma_{ij} = \mathrm{Cov}(X_i, X_j) = \mathbb E[(X_i - \mu_i)(X_j - \mu_j)]$). The *correlation*
  between $X$ and $Y$ is $\rho = \mathrm{Cov}(X,Y)/\sqrt{\mathrm{Var}(X)\mathrm{Var}(Y)} \in [-1,1]$.
- Linear combinations of jointly Gaussian variables are Gaussian; conditioning one jointly Gaussian variable
  on another gives a Gaussian whose variance shrinks by a factor depending on the correlation.

**Numerical example.** If $Y \sim \mathcal N(0,1)$ and $X = 0.8\,Y + 0.6\,Z$ with independent
$Z \sim \mathcal N(0,1)$, then $\mathrm{Var}(X) = 0.8^2 + 0.6^2 = 1$, $\mathrm{Cov}(X,Y) = 0.8$, so the
correlation is $\rho = 0.8$. Knowing $X$ tells you something about $Y$ precisely because $\rho \ne 0$.

**Where used in D1.** The concrete, fully-solvable instantiation of D1 (the "Gaussian against-independence
model," Section 4) is built exactly this way: each agent sees $X_i = \rho_i Y_i + \sqrt{1-\rho_i^2}\,Z_i$.

## 2.2 Independence and conditional independence

**Intuition.** Two variables are *independent* if knowing one tells you nothing about the other. They are
*conditionally independent given $Z$* if, *once you already know $Z$*, they tell you nothing further about each
other.

**Minimal math.** $X, Y$ independent $\iff p(x,y) = p(x)p(y)$. Conditionally independent given $Z$ $\iff$
$p(x,y\mid z) = p(x\mid z)\,p(y\mid z)$.

**Where used in D1.** The assumption **[H-CI]** ("conditional independence across agents given the
hypothesis") is what makes the centralized exponent a clean sum $E^{\mathrm{cen}} = \sum_i D_i$. Intuitively:
if, *once you fix the true state $\theta$*, the agents' observations are independent, then their evidence
simply *adds up*.

## 2.3 Entropy — the amount of surprise / the size of uncertainty

**Intuition.** Entropy measures how uncertain a random variable is, equivalently how many nats you would need,
on average, to describe its outcome. A fair coin has entropy $\ln 2$ nats ($=1$ bit). A biased coin that
almost always lands heads has *low* entropy — outcomes are predictable, cheap to describe. Maximum uncertainty
= maximum entropy.

**Minimal math.** For a discrete $X$, the **Shannon entropy** is
$$ H(X) = -\sum_x p(x) \ln p(x) \quad [\text{nats}]. $$
It satisfies $0 \le H(X) \le \ln|\mathcal X|$ (zero if $X$ is deterministic; maximal $\ln|\mathcal X|$ if $X$
is uniform over its $|\mathcal X|$ values). The **conditional entropy** $H(X\mid Z) = -\sum_{x,z}
p(x,z)\ln p(x\mid z)$ is the average leftover uncertainty in $X$ once $Z$ is known; always
$H(X\mid Z) \le H(X)$ ("conditioning reduces entropy").

**A key inequality we use in a proof:** $I \le H$, and **subadditivity**
$H(X_1,\dots,X_n) \le \sum_i H(X_i)$ (the whole is no more uncertain than the sum of its parts). These two
facts alone drive the cut-set bound (Lemma A, Section 8).

**Numerical example.** A coin with $p(\text{heads}) = 0.9$: $H = -0.9\ln 0.9 - 0.1\ln 0.1 \approx 0.325$ nats
$\approx 0.47$ bits — less than a fair coin's $1$ bit, because it is more predictable.

**Where used in D1.** The rate limit on an edge is a *hard entropy budget*: a message $M$ sent on an edge of
capacity $C$ obeys $H(M) \le C$. Since $I(M;\theta) \le H(M) \le C$, the message can carry at most $C$ nats
*about the hypothesis*. This single inequality is the seed of the converse.

## 2.4 KL divergence — the "distance" between two distributions (the engine of detection)

**Intuition.** The Kullback–Leibler (KL) divergence $D(P\Vert Q)$ measures how *distinguishable* a
distribution $P$ is from a distribution $Q$. If $P$ and $Q$ are very different, $D$ is large and you can tell
them apart quickly from samples; if they are nearly identical, $D \approx 0$ and telling them apart is slow.
It is the fundamental "signal strength" of a hypothesis test. (It is *not* a true distance — it is not
symmetric and violates the triangle inequality — but it behaves like a squared distance for nearby
distributions.)

**Minimal math.**
$$ D(P\Vert Q) = \sum_x p(x)\ln\frac{p(x)}{q(x)} \quad(\text{discrete}), \qquad
   D(P\Vert Q) = \int p(x)\ln\frac{p(x)}{q(x)}\,dx \quad(\text{continuous}). $$
Properties: $D(P\Vert Q) \ge 0$, with equality iff $P=Q$ (**Gibbs' inequality**); $D = +\infty$ if $P$ puts
mass where $Q$ puts none. It is *not* symmetric: $D(P\Vert Q) \ne D(Q\Vert P)$ in general.

**Gaussian formula (used everywhere in D1's concrete model).** For two 1-D Gaussians with the same variance
$\sigma^2$ and means $\mu_0, \mu_1$:
$$ D\big(\mathcal N(\mu_0,\sigma^2)\,\Vert\,\mathcal N(\mu_1,\sigma^2)\big) = \frac{(\mu_0-\mu_1)^2}{2\sigma^2}. $$
This is the "signal-to-noise ratio" of a mean-shift test. For general multivariate Gaussians there is a
closed form used in `code/d1_detect.py` (Section 9).

**Numerical example.** $P=\mathcal N(1,1)$ vs $Q=\mathcal N(0,1)$: $D = (1-0)^2/2 = 0.5$ nats. So the Type-II
error of the best test decays like $e^{-0.5 n}$ — halving the exponent per... (see Stein's lemma below).

**Where used in D1.** The centralized exponent is a KL divergence (Stein's lemma). The per-agent "evidence
strength" $D_i$ is a KL divergence. The whole detection story is KL divergence bookkeeping.

## 2.5 Mutual information — how much two variables tell you about each other

**Intuition.** Mutual information $I(X;Y)$ is the amount of uncertainty about $Y$ that is removed by learning
$X$ (and vice versa — it is symmetric). If $X$ and $Y$ are independent, $I=0$. If $X$ determines $Y$, $I$ is as
large as $Y$'s entropy.

**Minimal math.** $I(X;Y) = H(Y) - H(Y\mid X) = H(X) - H(X\mid Y) = D\big(P_{XY} \Vert P_X P_Y\big)$. That last
form is the punchline: **mutual information is the KL divergence between the true joint distribution and the
product of the marginals** — i.e., it measures exactly how far $(X,Y)$ is from being independent. This is *why*
mutual information is the natural object in "testing against independence."

**Gaussian formula (the single most reused number in D1).** For jointly Gaussian $(X,Y)$ with correlation
$\rho$:
$$ I(X;Y) = -\tfrac12 \ln(1-\rho^2). $$
As $\rho \to 0$, $I \to 0$ (independent, uninformative). As $|\rho| \to 1$, $I \to \infty$ (one determines the
other). This formula lives in `code/theory.py` as `mutual_information_XY(rho)`.

**Numerical example.** $\rho = 0.795 \Rightarrow I = -\tfrac12\ln(1-0.632) = -\tfrac12\ln(0.368) = 0.5$ nats.
This exact value ($\rho \approx 0.795$ giving $I = 0.5$ nat) is the default per-agent evidence strength used in
almost every D1 experiment.

**Where used in D1.** For testing against independence, the centralized exponent *equals* a mutual
information, and the rate-limited exponent $\theta_{\mathrm{IB}}$ is a *constrained maximization* of mutual
information. Mutual information is the currency of the whole direction.

## 2.6 Data-processing inequality (DPI) — you cannot create information by processing

**Intuition.** If data flows in a chain $A \to B \to C$ (meaning $C$ depends on $A$ only through $B$; formally
$A - B - C$ is a *Markov chain*), then $C$ cannot know more about $A$ than $B$ does. Post-processing can only
*lose* information, never create it. This is the single most-used inequality in the converse.

**Minimal math.** If $A - B - C$ is Markov, then $I(A;C) \le I(A;B)$ and $I(A;C) \le I(B;C)$. There is also a
*KL* version: processing two distributions through the same channel can only bring them *closer* (reduce KL),
$D(P_B \Vert Q_B) \le D(P_A \Vert Q_A)$ when $B$ is obtained from $A$ by a fixed channel.

**Where used in D1.** (i) A node's decision is a function of the messages it received, which are functions of
the raw data; so the node's information about $\theta$ cannot exceed what crossed its cut — this is how the cut
limit becomes an exponent limit. (ii) The centralized ceiling $E^{\mathrm{cen}}$ is itself a DPI statement: no
node beats the full-data detector.

## 2.7 Hypothesis testing, Type-I / Type-II errors, and Stein's lemma

**Intuition.** You must decide between two explanations of your data: $H_0$ (the "null") and $H_1$ (the
"alternative"). Two ways to be wrong: a **Type-I error** (raise a false alarm — reject $H_0$ when $H_0$ is
true), probability $\alpha$; and a **Type-II error** (miss — accept $H_0$ when $H_1$ is true), probability
$\beta$. There is a tradeoff: driving $\alpha$ down pushes $\beta$ up, and vice versa. The best possible
tradeoff is achieved by the **likelihood-ratio test** (Neyman–Pearson): compute $\ln\frac{p_0(\text{data})}
{p_1(\text{data})}$ and threshold it.

**Stein's lemma (the reason exponents equal KL divergences).** Fix the Type-I error at some small level
$\varepsilon$ (e.g., "no more than 5% false alarms"). Then, as the number of i.i.d. samples $n \to \infty$,
the smallest achievable Type-II error decays as
$$ \beta_n \doteq e^{-nD(P_0\Vert P_1)}, \qquad\text{i.e.}\qquad \lim_{n\to\infty} -\tfrac1n \ln\beta_n =
   D(P_0\Vert P_1). $$
Two things to notice, both used heavily in D1:
1. **The exponent is the KL divergence** $D(P_0\Vert P_1)$ — the "signal strength" of Section 2.4.
2. **The exponent does not depend on $\varepsilon$** (as long as $0<\varepsilon<1$). Whether you allow 5% or
   20% false alarms, the *rate* of Type-II decay is the same. This "$\varepsilon$-independence" is quietly
   crucial: it lets D1 state a single exponent without fussing over the false-alarm level.

**Numerical example.** $P_0 = \mathcal N(1,1)$, $P_1 = \mathcal N(0,1)$: $D = 0.5$, so with $n=20$ samples the
miss probability is roughly $e^{-10} \approx 4.5\times 10^{-5}$, regardless of whether $\varepsilon$ is 0.05
or 0.2.

**Where used in D1.** The quantity D1 characterizes, $E_k$, is exactly a Type-II error exponent (best decay
rate of the miss probability at a fixed false-alarm level). Stein's lemma is what turns "the network delivers
$\Gamma_k$ nats" into "the exponent is at most a function of $\Gamma_k$."

## 2.8 Error exponents and the "second-order" (dispersion) correction

**Intuition.** $\beta_n \approx e^{-nE}$ is the *first-order* (leading) behavior. At *finite* $n$, there is a
correction: the true $-\ln\beta_n$ is not exactly $nE$; it is $nE$ minus a term that grows like $\sqrt{n}$.
That $\sqrt n$ term is the **dispersion** correction; its size is governed by the *variance* of the
log-likelihood-ratio, called the **relative-entropy variance** $V$. Intuitively, $V$ measures how *noisy* the
evidence is around its average strength $D$: even if the average signal is strong, run-to-run fluctuations
mean finite-$n$ performance falls a little short of the asymptote.

**Minimal math (the Strassen / Tomamichel–Tan expansion).**
$$ -\ln\beta_n(\varepsilon) = nD - \sqrt{nV}\,\Phi^{-1}(\varepsilon) + O(\ln n), \qquad
   V = \mathrm{Var}_{P_0}\!\Big[\ln\tfrac{dP_0}{dP_1}\Big], $$
where $\Phi^{-1}$ is the inverse of the standard-normal CDF. Since $\Phi^{-1}(\varepsilon)<0$ for
$\varepsilon<1/2$, the correction *lowers* $-\ln\beta_n$ below the ideal line $nD$ — the finite-$n$ exponent is
approached *from below*.

**Where used in D1.** Experiment D1-E7 measures $V$ from the finite-$n$ curve and checks it against the
analytic relative-entropy variance; this validates the second-order term of §1.5.1 of the bible. It is also
why the other experiments use a "dispersion-corrected" fit to extract the true asymptotic exponent from
finite-$n$ data (Section 9).

## 2.9 Graphs, cuts, and max-flow / min-cut (the network side)

**Intuition.** A *graph* is dots (nodes) connected by lines (edges). Here, nodes are agents; a *directed* edge
$(i,j)$ with *capacity* $C_{ij}$ means "agent $i$ can send up to $C_{ij}$ nats per round to agent $j$." A
**cut** separating a set of *sources* from a *sink* $k$ is a set of edges whose removal disconnects the sources
from $k$; the cut's *capacity* is the sum of the capacities of its edges. The **min-cut** is the smallest such
capacity — the network's tightest bottleneck to $k$.

**Max-flow = min-cut (Menger / Ford–Fulkerson).** The maximum rate of "stuff" (flow) you can push from a
source to a sink equals the capacity of the minimum cut between them. Intuitively, water through pipes: the
most water you can move is set by the narrowest section. This theorem is the reason the *bottleneck* is the
governing quantity.

**Numerical example.** A ring of 4 nodes, each edge capacity $C$: node $k$ has exactly 2 edges touching it, so
to reach $k$ from the other three nodes everything must funnel through those 2 edges — min-cut $= 2C$. A
complete graph of 4 nodes: $k$ has 3 edges, min-cut $= 3C$. (These exact values are checked in
`code/topology.py`.)

**Where used in D1.** The governing network quantity $\Gamma_k$ is a min-cut (time-averaged, for a changing
graph). The achievability uses max-flow to *route* information at exactly the min-cut rate.

## 2.10 Time-expanded graphs and cycles

**Intuition.** If the network changes every round and may contain *cycles* (loops), reasoning about "how much
can reach $k$ over $T$ rounds" is confusing. The trick: make a *copy* of every node for every time step. Draw
an edge from "node $i$ at time $t$" to "node $j$ at time $t+1$" whenever the link $(i,j)$ existed at round $t$.
Add "memory" edges from "node $i$ at time $t$" to "node $i$ at time $t+1$" (a node remembers its own state).
The resulting **time-expanded graph** is *acyclic* (time only moves forward) even though the original had
cycles. Now standard max-flow/min-cut applies, and the total information reaching $k$ over $T$ rounds is the
min-cut of this static, acyclic time-expanded graph.

**Where used in D1.** This is how the theory (and the network-coding experiments D1-N5) handle *directed cyclic
time-varying* graphs: expand in time, and everything reduces to a clean acyclic max-flow.

## 2.11 The Information Bottleneck (IB) — the bridge from "rate" to "exponent"

**Intuition.** Suppose you must summarize an observation $X$ into a compressed message $U$ using at most $R$
nats, and you want $U$ to retain as much information as possible about a *relevance variable* $Y$. There is a
tradeoff: a tighter summary (smaller $I(U;X)$, fewer nats spent) keeps less about $Y$ (smaller $I(U;Y)$). The
**Information Bottleneck curve** $\theta_{\mathrm{IB}}(R)$ is the best you can do: the maximum relevant
information $I(U;Y)$ you can keep while spending at most $R$ nats describing $X$.

**Minimal math.**
$$ \theta_{\mathrm{IB}}(R) = \max_{\,p(u\mid x):\, I(U;X)\le R\,} I(U;Y), \qquad \text{over Markov } U - X - Y. $$
Shape facts (used in proofs and figures): $\theta_{\mathrm{IB}}(0) = 0$ (no bits, no relevance), it is
**increasing** and **concave** (diminishing returns — each extra nat buys less relevance), and it *saturates*
at $\theta_{\mathrm{IB}}(\infty) = I(X;Y)$ (with unlimited rate you keep everything relevant).

**Gaussian closed form (the exactly-solvable case D1 uses).** If $(X,Y)$ are jointly Gaussian with correlation
$\rho$, then
$$ \theta_{\mathrm{IB}}(R) = -\tfrac12 \ln\!\big(1 - \rho^2(1 - e^{-2R})\big). $$
Check the shape: at $R=0$ it is $-\tfrac12\ln 1 = 0$; as $R\to\infty$ it is $-\tfrac12\ln(1-\rho^2) = I(X;Y)$
(saturation); the initial slope is $\rho^2$ (each of the first nats is worth $\rho^2$ nats of relevance). This
formula is `theta_IB_single(R, rho)` in `code/theory.py`.

**Why IB is the bridge.** For "testing against independence," the best exponent you can get from a rate-$R$
summary is *exactly* $\theta_{\mathrm{IB}}(R)$ (Ahlswede–Csiszár). So IB is literally the function that
converts "the network delivered $R$ nats" into "the best exponent is $\theta_{\mathrm{IB}}(R)$." That is the
whole reason $\theta_{\mathrm{IB}}$ appears in the main theorem.

## 2.12 Network coding and Random Linear Network Coding (RLNC)

**Intuition.** Old-school networking *routes*: each packet is forwarded, copied, dropped — but never *mixed*.
**Network coding** allows intermediate nodes to send *combinations* (e.g., XORs, or random linear mixtures) of
the packets they hold. The surprising 2000 result (Ahlswede–Cai–Li–Yeung): for *multicast* (one source, many
sinks that all want the same information), mixing can achieve rates that pure routing cannot. The classic
example is the **butterfly network**, where routing delivers rate 1 to one of two sinks but coding delivers
rate 2 to *both* simultaneously.

**RLNC (Ho et al. 2006).** A practical, decentralized way to do network coding: each node sends *random* linear
combinations (over a finite field $\mathrm{GF}(q)$, i.e., arithmetic modulo a prime $q$) of what it holds, with
random coefficients. A sink can decode once it has collected enough linearly-independent combinations — which
happens as soon as its min-cut $\ge$ the number of source symbols, with probability approaching 1 as the field
size $q$ grows (failure probability $\le |E|/q$ per the Schwartz–Zippel lemma; the bible states the
$(1-h/q)^{|E|}$ form).

**Finite fields in one paragraph.** $\mathrm{GF}(q)$ for prime $q$ is just the integers
$\{0,1,\dots,q-1\}$ with addition and multiplication done modulo $q$, and every nonzero element has a
multiplicative inverse (so you can do Gaussian elimination / solve linear systems). This is the arithmetic in
which the random mixing happens; the "rank" of the collected combinations tells the sink whether it can
recover everything.

**Where used in D1.** The achievability D1★★ is *Type-Preserving Network Coding*: compress each agent's
observation to its IB-optimal summary, then carry the summaries across the (cyclic, time-varying) graph with
RLNC at the min-cut rate. Because D1 is *fusion-free* (every node is its own sink, and needs everyone's
summary), this is a **multicast** problem — exactly where coding beats routing. Experiment D1-N5 simulates a
real $\mathrm{GF}(q)$ code to prove this.

## 2.13 Ergodicity and time-averages (why $\Gamma_k$ is a single number)

**Intuition.** If the network's wiring is random but *statistically stationary* (its statistics do not drift
over time) and *ergodic* (time-averages equal ensemble-averages), then the *long-run average* of the per-round
min-cut settles to a single deterministic number, almost surely. That number is $\Gamma_k$. So even though the
bottleneck fluctuates round to round, the exponent is governed by its *time-average*.

**Minimal math.** Birkhoff's ergodic theorem: for a stationary ergodic sequence, $\frac1T\sum_{t=1}^T g(\cdot_t)
\to \mathbb E[g]$ almost surely. Applied to the per-round min-cut,
$\Gamma_k = \liminf_T \frac1T \sum_t \min_{\text{cut}} \sum_{(i,j)\in\text{cut}} C_{ij}(t)$ is a.s. constant.

**Where used in D1.** Definition of $\Gamma_k$; and experiment D1-E6 verifies that the *ergodic average* (not
the best round, not the worst round) is what predicts the exponent.

---

# SECTION 3 — NOTATION BIBLE (every symbol, once and for all)

This dictionary is grounded in the notation table of `D1_Research_Bible_v3.md` §1.0 and the code in
`code/theory.py` and `code/d1_detect.py`. For each symbol: **meaning**, **type/units**, **domain/range**,
**where first introduced**, **where used later**, and a **common-confusion** note.

| Symbol | Meaning | Type / units | Range | First seen | Used later | Common confusion |
|---|---|---|---|---|---|---|
| $N$ | number of agents | integer | $\ge 1$ | §4 | everywhere | not the sample count $n$ |
| $i$ | agent index | integer | $1..N$ | §4 | sums $\sum_i$ | not time $t$ |
| $k$ | the *deciding* node ("sink") | integer | $1..N$ | §1.3 | $\Gamma_k, E_k$ | every node is a $k$ (fusion-free) |
| $t$ | round / time step | integer | $1..T$ | §4 | $G_t, C_{ij}(t)$ | not sample index $n$ |
| $n$ | number of i.i.d. samples per agent | integer | $\to\infty$ | §2.7 | $\beta_n, E_k$ | **not** $N$; this is the "amount of data" |
| $\theta$ | hypothesis (true state) | element of finite set $\Theta$ | $\{\theta_0,\theta_1\}$ core | §4 | everywhere | $\theta^\star=\theta_0$ is "true"; $\theta$ the alternative |
| $\Theta$ | hypothesis set | finite set | $\vert\Theta\vert<\infty$ | §4 | [H-Fin] | binary is the core case |
| $X_i$ (or $X_{i,t}$) | agent $i$'s observation (at round $t$) | random var in $\mathcal X_i$ | e.g. $\mathbb R$ | §4 | detection | the *raw* data, never fully shared |
| $Y$ (or $Y_i$) | **relevance variable** | random var | Gaussian $\mathcal N(0,1)$ | §2.5 | $I(X;Y), \theta_{\mathrm{IB}}$ | in "against independence," $Y$ is what you test correlation with |
| $\ell_i(\cdot\mid\theta)$ | agent $i$'s likelihood under $\theta$ | prob. measure | — | §4 | $D_i$ | the statistical model |
| $D(P\Vert Q)$ | KL divergence | nats | $[0,\infty]$ | §2.4 | Stein, $D_i$ | not symmetric; not a metric |
| $D_i$ | agent $i$'s evidence strength | nats | $[0,\infty]$ | §4 | $E^{\mathrm{cen}}$ | $D_i=D(\ell_i(\cdot\mid\theta_0)\Vert\ell_i(\cdot\mid\theta_1))$ |
| $I(X;Y)$ | mutual information | nats | $[0,\infty)$ | §2.5 | $\theta_{\mathrm{IB}}$ | $=D(P_{XY}\Vert P_XP_Y)$ |
| $H(X)$ | entropy | nats | $[0,\ln\vert\mathcal X\vert]$ | §2.3 | cut-set bound | $I\le H$ |
| $\rho$ (or $\rho_i$) | correlation of $X_i$ with $Y$ | dimensionless | $(-1,1)$ | §2.1 | Gaussian model | "signal strength": bigger $=$ more informative agent |
| $Z_i$ | agent $i$'s private noise | $\mathcal N(0,1)$ | — | §4 | Gaussian model | independent across agents |
| $G_t=(V,E_t)$ | network at round $t$ | directed graph | — | §2.9 | $\Gamma_k$ | edges are *directed*; may have cycles |
| $C_{ij}(t)$ | capacity of edge $(i,j)$ at round $t$ | nats/use | $\ge 0$ | §2.9 | $\Gamma_k$ | a *hard budget*: $H(\text{msg})\le C_{ij}$ |
| $M_{ij,t}$ | message sent on edge $(i,j)$ at $t$ | random var | $H\le C_{ij}(t)$ | §8 | Lemma A | the transmitted symbol, not the raw data |
| $M_k^{(T)}$ | everything node $k$ received over $T$ rounds | random var | — | §8 | Lemma A/B | the full transcript at $k$ |
| $\mathrm{Cut}(k)$ | all edge-cuts isolating sources from $k$ | set of edge sets | — | §2.9 | $\Gamma_k$ | many cuts; we take the *min* |
| $\Gamma_k$ | **min-cut information flow to $k$** | nats/use | $[0,\infty]$ | §1.3 | main theorem | *time-averaged* min-cut; the network's throttle |
| $E^{\mathrm{cen}}(\theta)$ | centralized (unlimited-comm) exponent | nats | $[0,\infty]$ | §1.0 | main theorem | $=\sum_i D_i$ under [H-CI]; the *ceiling* |
| $\theta_{\mathrm{IB}}(\Gamma)$ | best exponent from a rate-$\Gamma$ summary (against independence) | nats | $[0,\infty)$ | §2.11 | main theorem | a *function*, concave, increasing, saturating |
| $\theta_{\mathrm{SHA}}(\Gamma)$ | the general-pair converse functional | nats | $[0,\infty)$ | §1.0 | scope caveat | used only for the *general* pair; $\ne\theta_{\mathrm{IB}}$ there |
| $C_{\mathrm{DIB}}(\theta)$ | saturation rate | nats/use | $[0,\infty]$ | §1.0 | strictness, kink | smallest $\Gamma$ with $\theta_{\mathrm{IB}}(\Gamma)=E^{\mathrm{cen}}$ |
| $U$ (or $U_i$) | the compressed summary of $X$ | random var | rate $\le\Gamma$ | §2.11 | IB, encoder | the "message"; $U-X-Y$ Markov |
| $\alpha_n$ | Type-I error (false alarm) | probability | $\le\varepsilon$ | §2.7 | [H-T1] | held fixed |
| $\beta_n$ | Type-II error (miss) | probability | $\to 0$ | §2.7 | $E_k$ | its decay rate is the exponent |
| $\varepsilon$ | Type-I level | probability | $(0,1)$ | §2.7 | [H-T1] | the exponent does **not** depend on it |
| $E_k(\theta)$ | **the object of study**: best Type-II exponent at node $k$ | nats | $[0,\infty]$ | §1.1 | main theorem | $=\min\{E^{\mathrm{cen}},\theta_{\mathrm{IB}}(\Gamma_k)\}$ |
| $V$ | relative-entropy variance (dispersion) | nats$^2$ | $\ge 0$ | §2.8 | D1-E7 | governs the $\sqrt n$ finite-sample correction |
| $\Phi^{-1}$ | inverse standard-normal CDF | — | — | §2.8 | dispersion | negative for $\varepsilon<1/2$ |
| $r_{UY}$ | induced correlation of summary $U$ with $Y$ | dimensionless | $(-1,1)$ | §9 | saddlepoint | $r_{UY}^2=\rho^2(1-e^{-2R})$; a *derived* quantity |
| $q$ | finite-field size (RLNC) | prime | $\ge 2$ | §2.12 | D1-N5 | bigger $q$ = more reliable coding |
| $h$ | number of source symbols (RLNC) | integer | $\ge 1$ | §2.12 | D1-N5 | recover iff $h\le$ min-cut |
| $F$ | min-cut in symbol units (RLNC experiment) | integer | $\ge 0$ | §9 | D1-N5 | the coding capacity |

**Superscripts / subscripts / decorations.** $E^{\mathrm{cen}}$: superscript "cen" = centralized. $\theta^\star$:
star = the *true* hypothesis. $M_k^{(T)}$: superscript $(T)$ = "accumulated over $T$ rounds." Hats ($\hat b,
\hat w$): decoder *estimates*. Tildes ($\tilde U$): the SHA auxiliary variable. $\dot=$ ("dot equals"):
"equal to first exponential order," i.e. $a_n \doteq e^{-nE}$ means $-\frac1n\ln a_n \to E$.

**The four symbols never to confuse:** $N$ (agents) vs $n$ (samples) vs $t$ (rounds) vs $q$ (field size); and
$\theta$ (hypothesis) vs $\theta_{\mathrm{IB}}$ (a function whose name happens to contain $\theta$ for
historical reasons — it is an *exponent*, not a hypothesis).

---

# SECTION 4 — PROBLEM FORMULATION (every assumption, every equation)

## 4.1 The abstract problem (what is given, what is asked)

**Given:** $N$ agents; a finite hypothesis set $\Theta$ (core case: two hypotheses $\theta_0, \theta_1$, with
$\theta_0$ actually true); each agent $i$ draws i.i.d.-over-time observations $X_{i,t}$ from a known law
$\ell_i(\cdot\mid\theta)$ that depends on the hypothesis; a time-varying directed network $G_t$ with hard
per-edge rate budgets $C_{ij}(t)$; no fusion center. **Asked:** for each node $k$, the best achievable Type-II
error exponent $E_k(\theta)$ (best decay rate of the miss probability) subject to a fixed Type-I level.

Formally (bible §1.1b):
$$ E_k(\theta) = \sup_{\text{decentralized, fusion-free, rate-constrained schemes}} \ \liminf_{n\to\infty}
   -\tfrac1n \ln \beta_n^{(k)} \quad\text{s.t. } \alpha_n^{(k)} \le \varepsilon. $$
Read this slowly: over *all* legal schemes, take the one whose miss probability $\beta_n^{(k)}$ decays fastest;
its decay rate ($-\frac1n\ln\beta_n$, in the limit) is $E_k$. The "s.t. $\alpha_n\le\varepsilon$" pins the
false-alarm rate so the comparison is fair.

## 4.2 The five standing assumptions, each explained

Each assumption has an intuitive purpose, and a note on what breaks without it.

**[H-Fin] — finitely many hypotheses ($|\Theta|<\infty$).**
*Why needed:* Stein's lemma (the tool that makes exponents equal KL divergences) is cleanest for a fixed pair
of hypotheses; finiteness lets you handle "the true one vs each alternative" one pair at a time. *If removed:*
for countably many hypotheses the per-pair bound still holds; for a continuous parameter you replace Stein by
its parametric large-deviations analog (bible §1.3.1). *Nothing fundamental breaks* — only the bookkeeping.

**[H-CI] — conditional independence across agents given $\theta$.** Formally
$P(x_1,\dots,x_N\mid\theta) = \prod_i \ell_i(x_i\mid\theta)$.
*Why needed:* it makes the centralized exponent a clean **sum** $E^{\mathrm{cen}} = \sum_i D_i$ (evidence adds
up). *Intuition:* once the true state is fixed, each agent's sensor noise is its own; no shared nuisance.
*If removed (correlated observations):* the converse **still holds** as an upper bound, but with
$E^{\mathrm{cen}}$ replaced by the *true joint* divergence $\frac1n D(P^n_{\theta_0}\Vert P^n_{\theta_1})$,
which is generally **not** $\sum_i D_i$; positive correlation typically *lowers* the exponent (shared
information is redundant). The clean single-letter evaluability is what is lost, not the converse itself
(bible §1.3.1-CI). *This is tested by experiment D1-N3's spirit and discussed in the validation.*

**[H-Top] — the topology process $\{(E_t, C(t))\}$ is stationary and ergodic.**
*Why needed:* so that the time-averaged min-cut $\Gamma_k$ converges to a single deterministic number (Birkhoff,
§2.13). *If removed (non-stationary):* $\Gamma_k$ may not converge; you sandwich with $\liminf$/$\limsup$ and
the converse holds with the looser $\Gamma_k^{\sup}$ (bible §1.10).

**[H-Rate] — hard per-edge budgets:** any message on edge $(i,j)$ at round $t$ has entropy $H(M_{ij,t}) \le
C_{ij}(t)$.
*Why needed:* it is the physical meaning of "the link carries only $C$ nats." Crucially, $H(M)\le C$ implies
$I(M;\theta)\le C$ (since $I\le H$), which is the *only* thing the converse uses. *Alternative model:* the
"mutual-information" (soft) model constrains $I(M;X_i)\le C$ instead; the converse holds identically under
both, because $\theta - X_i - M$ Markov gives $I(M;\theta)\le I(M;X_i)\le C$ anyway (bible §1.0-note). *The two
models differ only for the achievability side (the hard model is stricter for the encoder).*

**[H-T1] — the Type-I error is held at a fixed level $\alpha_n \le \varepsilon \in (0,1)$.**
*Why needed:* to define "the" Type-II exponent (you must pin one error to talk about the other's rate).
*Beautiful fact:* by Stein's lemma the exponent is *independent* of $\varepsilon$, so the choice of level does
not matter — a robustness the theorem inherits for free.

## 4.3 The two objects the theorem is built from

**Object 1 — the centralized ceiling $E^{\mathrm{cen}}$.** By Stein's lemma applied to the full data of all
agents, and using [H-CI],
$$ E^{\mathrm{cen}}(\theta_1) = \lim_{n\to\infty} -\tfrac1n \ln \beta_n^{\mathrm{cen}}(\varepsilon)
   = \sum_{i=1}^N D\big(\ell_i(\cdot\mid\theta_0)\Vert\ell_i(\cdot\mid\theta_1)\big) = \sum_i D_i. $$
*Where each term comes from:* Stein gives "exponent = KL divergence"; [H-CI] makes the joint KL a sum of
per-agent KLs (KL of a product is the sum of KLs). *Meaning:* the best exponent if you could see everything.

**Object 2 — the rate-limited exponent $\theta_{\mathrm{IB}}(\Gamma)$.** Defined in §2.11: the most relevance
you can keep about $Y$ using a summary of rate $\Gamma$. For testing against independence it is *exactly* the
best exponent from a rate-$\Gamma$ pipe (Ahlswede–Csiszár). *Meaning:* the best exponent if your pipe is the
limit.

The main theorem simply says $E_k = \min$ of these two. Everything else is *justifying* that min.

## 4.4 The concrete, fully-solvable instantiation: the Gaussian against-independence model

Abstract theorems are validated on a concrete model where every quantity has a closed form. The bible's §1.6-AI
model, and the one used throughout the code (`code/theory.py`, `code/d1_detect.py`), is:

- There is a scalar **relevance** $Y \sim \mathcal N(0,1)$.
- Each agent observes $X_i = \rho_i\, Y + \sqrt{1-\rho_i^2}\, Z_i$, with independent $Z_i \sim \mathcal N(0,1)$.
  So $\mathrm{corr}(X_i, Y) = \rho_i$ — the agent's "informativeness."
- **The test:** $H_0$ = "the true joint law (each $X_i$ correlated with $Y$)" vs $H_1$ = "$X_i$ independent of
  $Y$." This is *testing against independence*: you are testing whether the observations carry information
  about $Y$ at all.

Closed forms (all in `code/theory.py`, all verified numerically in the repo):
- Per-agent evidence / relevance: $I(X_i;Y) = -\tfrac12\ln(1-\rho_i^2)$.
- Centralized ceiling: $E^{\mathrm{cen}} = \sum_i I(X_i;Y) = -\tfrac12\sum_i \ln(1-\rho_i^2)$.
- Per-agent IB curve: $\theta_{\mathrm{IB},i}(R) = -\tfrac12\ln\!\big(1-\rho_i^2(1-e^{-2R})\big)$.
- Symmetric network (all $\rho_i=\rho$, equal split $R=\Gamma/N$):
  $\theta_{\mathrm{IB}}(\Gamma) = -\tfrac N2\ln\!\big(1-\rho^2(1-e^{-2\Gamma/N})\big)$.

**The default numbers to memorize:** $\rho = \sqrt{1-e^{-1}} \approx 0.795$ makes $I(X_i;Y)=0.5$ nat exactly; with
$N=4$ agents, $E^{\mathrm{cen}} = 4\times 0.5 = 2$ nats. These are the standing values in most D1 experiments.

**An important honesty point discovered during validation (documented, not hidden).** The bible's §1.6-AI writes
a *single shared* $Y$ but then uses the *additive* formula $E^{\mathrm{cen}}=\sum_i I(X_i;Y)$. Those two are
only mutually consistent if each agent has its *own independent* relevance $Y_i$ (i.e., $N$ parallel
against-independence channels), because with a *shared* $Y$ the true joint MI is
$I(X_{1:N};Y)=\tfrac12\ln(1+N\rho^2/(1-\rho^2))$, which is *not* $\sum_i I(X_i;Y)$. The repository therefore uses
the **independent-per-agent-relevance** instantiation, under which every bible formula (additive
$E^{\mathrm{cen}}$, symmetric $\theta_{\mathrm{IB}}$, water-filling) is exactly self-consistent, and states this
explicitly (see `resultsD1.md` header and `VALIDATION_AUDIT.md`). This is the kind of scope-precision a
reviewer will probe; know it cold.

## 4.5 Water-filling: how to split a shared budget across unequal agents

If agents have different informativeness $\{\rho_i\}$ and share a total budget $\Gamma$, how should the budget
be split to maximize the exponent $\sum_i \theta_{\mathrm{IB},i}(R_i)$ subject to $\sum_i R_i = \Gamma$? This is
a concave maximization; the optimum (bible §1.6-AI "D1-C5", code `water_filling_allocation`) is:
$$ R_i^\star(\nu) = \tfrac12\ln\!\frac{\rho_i^2(1-\nu)}{\nu(1-\rho_i^2)}\ \text{ if positive, else } 0, $$
where the single "water level" $\nu\in(0,1)$ is tuned so $\sum_i R_i^\star(\nu) = \Gamma$. *Intuition:* pour
rate into the most-informative agents first; an agent too weak for the current water level gets *zero* rate
(cut off). This is the classic water-filling shape from power allocation, here for information rate. Experiment
D1-E4 confirms it beats equal splitting by up to $0.30$ nats.

---

# SECTION 5 — LITERATURE REVIEW (the evolution of the field, not a list)

This section tells the *story* of how the field arrived at the D1 gap, grounded in the prior-art matrix of
`D1_Research_Bible_v3.md` §1.2. For each work: what they solved, their assumptions, where they stop, why they
cannot solve D1, and how D1 extends them.

## 5.1 The root: Stein and Chernoff (≈1952) — exponents are KL divergences

*What they solved:* the best error exponent for a *centralized* binary hypothesis test. *Result:* at fixed
Type-I level, the Type-II exponent is exactly the KL divergence $D(P\Vert Q)$, independent of the level (Stein);
Chernoff gives the symmetric-error exponent. *Assumptions:* you hold all the data; no communication, no network.
*Where they stop:* the moment you cannot see all the data — because it must be compressed and sent over links —
Stein no longer applies directly. *How D1 extends:* D1 recovers Stein as the special case $N=1$, unlimited rate
($\Gamma\to\infty$), where $\theta_{\mathrm{IB}}(\infty)=I(X;Y)=E^{\mathrm{cen}}$ (bible §1.3.6). Stein is the
"ceiling" $E^{\mathrm{cen}}$ in the main theorem.

## 5.2 Ahlswede–Csiszár (1986) — the birth of $\theta_{\mathrm{IB}}$

*What they solved:* hypothesis testing when *one* observer must compress $X$ to a *single* rate-$R$ message for
*one* detector that holds side information $Y$. *Result (the seed of everything):* for **testing against
independence**, the exact exponent is $\theta_{\mathrm{IB}}(R) = \max_{I(U;X)\le R} I(U;Y)$ — the Information
Bottleneck functional, given operational meaning as an *error exponent* for the first time. *Assumptions:* a
single link, a single detector, static, asymptotic block length. *Where they stop:* no network of many
agents, no changing topology, no "everyone decides for themselves." *How D1 extends:* D1★ shows that on a
*network*, the binding rate is the *min-cut* $\Gamma_k$, and the AC exponent $\theta_{\mathrm{IB}}(\Gamma_k)$
governs each node — recovering AC exactly when the network is a single link (bible §1.3.6). AC is the
mathematical heart D1 generalizes from a link to a cut.

## 5.3 Han (1987) and Shimokawa–Han–Amari (1994) — the general pair and its hardness

*What they solved:* multiterminal data compression for hypothesis testing beyond "against independence." *Result:*
the SHA exponent $\theta_{\mathrm{SHA}}(R)$, a KL-divergence-between-induced-marginals functional, with a
"binning" refinement; achievable bounds and converses for special cases. *Assumptions:* static, single/again
few links. *Where they stop:* for a *general* pair of hypotheses (neither being a product measure), the exact
distributed exponent is *still open in the literature*. *How D1 uses them:* D1★'s converse for the general pair
uses $\theta_{\mathrm{SHA}}(\Gamma_k)$ as the upper-bounding functional (Lemma B). *Crucial scope point (bible
COR-4):* $\theta_{\mathrm{SHA}} = \theta_{\mathrm{IB}}$ *only* for testing against independence; for the general
pair they are different, not universally ordered, and D1 does **not** claim a matching achievability there.

## 5.4 Rahman–Wagner (2012) — tightness for against-independence

*What they solved:* when is the binning bound *tight*? *Result:* for testing against independence, binning is
optimal and the achievable exponent meets the converse — i.e., $\theta_{\mathrm{IB}}$ is *the* exponent, exactly.
*Why D1 needs it:* this is the license to claim D1★ is a *strong* converse (exact, not just an upper bound) in
the against-independence case, and it is the ingredient that lets D1★★ *attain* $\theta_{\mathrm{IB}}$.

## 5.5 Tishby–Pereira–Bialek (1999) and Aguerri–Zaidi (2019) — Information Bottleneck, centralized then distributed

*Tishby et al.:* introduced the IB principle (compress $X$, keep info about $Y$) as a *machine-learning*
objective, with the Lagrangian $\min_{p(u\mid x)} I(U;X)-\beta I(U;Y)$ and self-consistent equations. No network,
no operational exponent meaning. *Aguerri–Zaidi:* the *distributed* IB — many encoders compressing to *one*
decoder (a star / CEO problem), exact single-letter rate–relevance region, Gaussian and discrete. *Assumptions:*
**static topology, a decoder/fusion node exists, asymptotic.** *Where they stop:* exactly the three axes D1 turns
on — time-varying, fusion-free, per-edge cut. *How D1 extends:* D1's static-star specialization recovers the
Aguerri–Zaidi converse ceiling (bible §1.3.6); D1 adds the time-varying, fusion-free, cut-limited generalization.

## 5.6 Nedić–Olshevsky–Uribe (2017) and social learning — networks without rate limits

*What they solved:* distributed non-Bayesian learning / belief consensus over *time-varying* graphs with *no*
fusion center. *Result:* each agent's belief on a wrong hypothesis decays geometrically at a rate governed by
the *network-averaged KL* $\sum_i v_i D_i$ (with $v$ the eigenvector-centrality weights); explicit,
non-asymptotic. *Assumptions:* agents exchange *full* belief vectors — essentially **unlimited rate**.
*Where they stop:* they say nothing about what happens when the links are *rate-limited*. *How D1 extends:* D1's
$\Gamma_k\to\infty$ limit recovers their ceiling ($E^{\mathrm{cen}}$), and D1 *adds the finite-rate throttle*
$\theta_{\mathrm{IB}}(\Gamma_k)$ they omit (bible §1.3.6). They are the "unlimited-comm, changing-network"
corner; D1 fills in the rate axis.

## 5.7 Network coding: Ahlswede–Cai–Li–Yeung (2000), Ho et al. (2006)

*What they solved:* the maximum multicast rate in a network when intermediate nodes may *mix* (code) packets,
not just route. *Result:* multicast capacity = min over sinks of the min-cut, *achievable by coding but not in
general by routing* (butterfly). Ho et al.: *random linear* network coding achieves it decentrally, w.h.p. as
field size grows. *How D1 uses them:* the achievability D1★★ (Type-Preserving Network Coding) carries the IB
summaries across the cyclic time-varying graph with RLNC at the min-cut rate; because fusion-free = multicast,
coding is *genuinely necessary* (experiment D1-N5 shows routing falls short). This is a *tool* D1 imports, made
rigorous for the D1 setting via the time-expanded DAG.

## 5.8 The novelty in one table (bible §1.2 "Novelty matrix," paraphrased)

| Prior work | time-varying? | fusion-free? | per-edge rate? | converse? | achievability? |
|---|:--:|:--:|:--:|:--:|:--:|
| Ahlswede–Csiszár '86 | ✗ | ✗ | ✓ (1 link) | ✓ | ✓ |
| Han '87 / SHA '94 | ✗ | ✗ | ✓ | ✓ | partial |
| Aguerri–Zaidi '19 | ✗ | ✗ (has decoder) | ✓ | ✓ | ✓ |
| Nedić–Olshevsky–Uribe '17 | ✓ | ✓ | ✗ | — | ✓ (rate) |
| **D1 (this work)** | **✓** | **✓** | **✓** | **✓ (D1★)** | **✓ (D1★★, against independence)** |

The bottom row — all four network features on at once, with a matching converse *and* achievability — is the
contribution. No prior row has all the checkmarks.

---

# SECTION 6 — OUR CONTRIBUTIONS (simple English and mathematics)

## 6.1 Contribution 1 — the exact limit $E_k = \min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$

*Simple English:* we found the exact best-possible decision quality for any agent in a bandwidth-limited,
fusion-free, ever-changing network, and it is beautifully simple: you are throttled by whichever is scarcer,
your statistics or your bandwidth. *Mathematics:* a matching converse (D1★) and achievability (D1★★) that meet
with zero gap for testing against independence over general time-varying directed cyclic graphs. *Why new:* it
is the first characterization at the intersection of all three network features (§5.8). *Why hard:* the three
features *couple* — the consensus that removes the fusion center must itself flow through the rate-limited,
changing links, so compression and agreement are not separable. *Main insight:* despite the coupling, the answer
*decouples* into a pure-statistics term ($E^{\mathrm{cen}}$) and a pure-network term ($\Gamma_k$) joined by the
universal IB translator — the network's *only* imprint on the exponent is through the single scalar $\Gamma_k$.

## 6.2 Contribution 2 — $\Gamma_k$ is a *sufficient statistic* for the network

*Simple English:* the *only* thing about the network that matters for your exponent is your min-cut $\Gamma_k$.
Two completely different graphs with the same $\Gamma_k$ give the *same* exponent. Topology, degree, diameter,
randomness — all irrelevant beyond the cut. *Why surprising:* one might expect denser or better-connected graphs
to help; they do *not*, beyond raising $\Gamma_k$. *Evidence:* experiment D1-E3 collapses 10 different
topologies (complete, ring, path, star, grid, tree, Erdős–Rényi, Barabási–Albert, Watts–Strogatz, directed) to
a single exponent at matched $\Gamma_k$ (spread $0.0000$ nats). D1-N1 shows this is a *genuine* fact about
routed information, not a tautology (network coding attains it; naive forwarding does not).

## 6.3 Contribution 3 — the time-average is the binding rate

*Simple English:* when the network changes every round, your exponent is set by the *long-run average*
bottleneck, not the best round and not the worst round. *Mathematics:* $\Gamma_k = \liminf_T \frac1T \sum_t
(\text{per-round min-cut})$, an ergodic average (Lemma C-D1). *Evidence:* D1-E6 — the ergodic mean $\Gamma_k
= 2.90$ predicts the exponent ($1.488$ measured vs $1.489$ predicted); using the min-round ($0.592$) or
max-round ($2.157$) mispredicts badly.

## 6.4 Contribution 4 — network coding is *necessary*, not a convenience

*Simple English:* because every agent is its own decision-maker (fusion-free), everyone needs everyone's
summary — a *multicast*. In multicast, plain forwarding provably cannot deliver every agent its full min-cut
simultaneously, but *mixing* (network coding) can. *Evidence:* experiment D1-N5 simulates an actual
$\mathrm{GF}(q)$ random linear network code: on the butterfly network coding delivers the min-cut 2 to *both*
sinks while routing delivers only 1; and naive quantize-and-forward is *sub-additive in nats* (loses up to
$60\%$ of the cut on multi-path graphs, D1-N1). This is the operational reason the achievability construction is
*Type-Preserving Network Coding*, not "compress and forward."

## 6.5 Contribution 5 — a rigorous, non-circular *validation methodology*

*Simple English:* the experiments do not merely re-plug the formula into itself; they *route real information
through real graphs* and *simulate real finite-field codes*, and they *measure* exponents that are far too
small for naive Monte Carlo by using exact saddlepoint mathematics. *Why it matters:* it is what makes the
empirical support believable to a hostile reviewer. Details in Sections 9–10. *Discovered corrections:* the
naive-Monte-Carlo protocol suggested in the bible is *infeasible* (miss probabilities like $e^{-2n}$ are
unmeasurable); the handbook's experiments replace it with an exact saddlepoint method cross-checked against
Monte Carlo where feasible.

---

# SECTION 7 — THEOREMS (statement, plain English, meaning, assumptions, consequences, intuition, reviewer bait)

## 7.1 Theorem D1★ — the Rate–Connectivity Converse (impossibility)

**Formal statement (bible §1.3.1).** Under [H-Fin]–[H-T1], for every node $k$ and every alternative
$\theta \ne \theta^\star$,
$$ \boxed{\,E_k(\theta) \le \min\{\,E^{\mathrm{cen}}(\theta),\ \theta_{\mathrm{IB}}(\Gamma_k)\,\}\,} $$
in the testing-against-independence instantiation (where $\theta_{\mathrm{IB}}$ is the *tight* rate-limited
exponent). For a general pair, replace $\theta_{\mathrm{IB}}$ by $\theta_{\mathrm{SHA}}(\Gamma_k)$.
**Strictness:** if $\Gamma_k < C_{\mathrm{DIB}}(\theta)$ then $E_k(\theta) < E^{\mathrm{cen}}(\theta)$ strictly.

**Plain English.** No decentralized, rate-limited, fusion-free scheme — no matter how clever, how much
interaction, how much cleverness in coding — can achieve an error exponent above the smaller of (the
unlimited-communication ceiling) and (the exponent permitted by the bottleneck $\Gamma_k$). And if your
bottleneck is below the saturation point, you *strictly* lose relative to the ceiling.

**Why it matters.** It is the *hard limit*. It tells engineers the best they can *ever* do, so they do not waste
effort chasing impossible performance, and it tells them exactly which resource to buy (bandwidth vs sensors).

**Assumptions and their role.** [H-CI] fixes $E^{\mathrm{cen}}=\sum_i D_i$ (else the true joint divergence);
[H-Rate] gives the per-edge entropy budget used in the cut-set step; [H-Top] makes $\Gamma_k$ a single number;
[H-T1] fixes the level (exponent is level-independent anyway).

**Consequences.** (i) $\Gamma_k$ is the *only* network quantity that appears — a sufficient statistic. (ii) The
bound is a *strong converse* for against-independence: it is not merely an upper bound, it is the exact limit,
because D1★★ attains it. (iii) It degenerates correctly: $N=1,\Gamma\to\infty$ gives Stein; static star gives
Ahlswede–Csiszár; $\Gamma\to\infty$ gives $E^{\mathrm{cen}}$ (Nedić et al.'s ceiling).

**Limitations.** For the *general pair* it is only a converse (upper bound), with $\theta_{\mathrm{SHA}}$; no
matching achievability is claimed there. For *correlated* observations the value of $E^{\mathrm{cen}}$ changes
and single-letter evaluability degrades, though the converse survives.

**Intuition (one paragraph).** Any node's decision is a function of the messages that reached it. Those messages
had to squeeze through the node's tightest cut, which can carry at most $\Gamma_k$ nats per round about anything,
including the hypothesis (entropy budget). So the node learns at most $\Gamma_k$ nats/round about $\theta$; by
Stein-through-a-bottleneck (the IB functional), that caps its exponent at $\theta_{\mathrm{IB}}(\Gamma_k)$.
Separately, even with infinite bandwidth it cannot beat the full-data detector, capping it at $E^{\mathrm{cen}}$.
Take the smaller. That is the whole converse.

**Reviewer bait (answered fully in Section 12).** *"Is this circular — did you assume the answer?"* No: the two
caps come from two independent inequalities (cut-set entropy bound; full-data data-processing). *"Does
interaction break it?"* No: interaction can use the rate better but cannot exceed the cut's entropy budget.

## 7.2 Theorem D1★★ — Flawless Achievability (construction)

**Formal statement (bible §1.4).** Under [A1]–[A4] (against independence; $Y$ at each deciding node; finite
alphabets; stationary-ergodic directed cyclic $\{G_t\}$), for every node $k$ and every $\delta>0$ there is a
finite-block Type-Preserving Network Coding (TPNC) scheme with Type-I $\le\varepsilon$ and Type-II exponent
$\ge \min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\} - \delta$. Hence
$$ \boxed{\,E_k(\theta) = \min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}\,} $$
**matching D1★ with zero gap.**

**Plain English.** There is an actual recipe — (1) compress each agent's data to its information-bottleneck
summary, (2) carry the summaries across the changing, looping network with random linear network coding at the
min-cut rate, (3) run a joint-typicality test at each node — whose exponent *equals* the converse bound. So the
converse is not just an upper bound; it is *reached*.

**Why it matters.** Converse + achievability = the problem is *solved exactly*, not merely bounded. The recipe
also tells you *how* to build an optimal scheme.

**The three layers (each a lemma, proved in Section 8):**
- *Lemma A-D1 (encoding):* each agent quantizes to the IB-optimal codeword and *bins* it into $\mathrm{GF}(q)$
  symbols; edges carry random linear combinations. Algebraic mixing preserves the "type" (empirical
  distribution) needed for the test.
- *Lemma B-D1 (decoding):* independently-built codebooks are jointly decodable at the sink with *no rate loss*,
  because the number of independent $\mathrm{GF}(q)$ equations reaching $k$ equals the min-cut, and the sink
  solves by Gaussian elimination then un-bins by joint typicality.
- *Lemma C-D1 (time aggregation):* over $T$-round super-blocks the per-round cuts *aggregate* to the ergodic
  mean $\Gamma_k$ with no vanishing gap; growing the field size $q$ with $T$ drives coding failure to zero
  faster than any fixed exponent.

**Limitations / scope.** Closes the *against-independence* target only (its converse's exact domain). The
general-pair distributed exponent is a structurally different, open problem and is *not* claimed. The
construction assumes $Y$ is available at the deciding node (still fusion-free — no node holds another's *raw*
data).

**Intuition.** The IB summary is the *smallest* description that keeps all the relevant information at rate
$\Gamma_k$; network coding is the *only* way to deliver that description to *every* node at once (multicast);
and time-expansion turns the looping, changing graph into a clean acyclic max-flow so the min-cut math applies.
Put together, each node receives exactly $\Gamma_k$ nats of relevant information and runs the optimal test on
it — achieving $\theta_{\mathrm{IB}}(\Gamma_k)$, capped by $E^{\mathrm{cen}}$.

## 7.3 Proposition — existence of the saturation rate $C_{\mathrm{DIB}}$ (bible Prop. 1.0-A)

**Statement.** The set $\{\Gamma : \theta_{\mathrm{IB}}(\Gamma) = E^{\mathrm{cen}}\}$ is non-empty and its
infimum $C_{\mathrm{DIB}}$ is finite ($\le \ln|\Theta|$). **Meaning:** there is a finite bandwidth beyond which
you have *saturated* — you have hit the statistical ceiling and more bandwidth is wasted. **Consequence:** the
main-theorem "min" has two regimes with a *kink* at $C_{\mathrm{DIB}}$: below it, $E_k = \theta_{\mathrm{IB}}
(\Gamma_k)$ (bandwidth-limited, rising); above it, $E_k = E^{\mathrm{cen}}$ (statistics-limited, flat). *Caveat
for the Gaussian model:* there $\theta_{\mathrm{IB}}$ approaches $E^{\mathrm{cen}}$ only *asymptotically*, so the
"kink" is a soft knee and $C_{\mathrm{DIB}}$ is defined at a $\delta$-saturation level (the repo uses $2\%$,
giving $C_{\mathrm{DIB}}\approx 8.887$ for the $N=4,\rho=0.795$ case, per `resultsD1.md` D1-E1).

## 7.4 Strictness proposition (bible §1.3.5)

**Statement.** If $\Gamma_k < C_{\mathrm{DIB}}$ then $\theta_{\mathrm{IB}}(\Gamma_k) < E^{\mathrm{cen}}$ strictly,
so $E_k < E^{\mathrm{cen}}$ strictly. **Meaning:** below saturation you *provably* lose exponent — the bandwidth
limit *bites*. **Why true:** $\theta_{\mathrm{IB}}$ is concave, non-decreasing, and first equals
$E^{\mathrm{cen}}$ at $C_{\mathrm{DIB}}$; a concave non-decreasing function cannot be flat on a sub-interval
before its first saturation without being flat forever, so it is *strictly* increasing on $[0, C_{\mathrm{DIB}})$.

---

# SECTION 8 — PROOFS (the most important section: every step, every inequality, every trick)

> **How to read this section.** For each proof I give: (0) the *goal* in one line; (1) the *strategy* and why it
> works; (2) the step-by-step derivation with *every* inequality justified — where it comes from, which prior
> theorem licenses it, what intuition backs it, and what would fail if it were wrong. External theorems are
> taught inline. Nothing is assumed known beyond Section 2.

## 8.1 Converse D1★ = Lemma A (cut-set) + Lemma B (rate-limited Stein) + full-data DPI, combined

The converse is a chain of three independent bounds. The overall strategy:

1. **Lemma A** shows the *network* can deliver at most $\Gamma_k$ nats/round of information about $\theta$ to
   node $k$ (a pure information-flow bound).
2. **Lemma B** shows that a detector holding only $\Gamma_k$ nats/sample about $\theta$ has exponent at most
   $\theta_{\mathrm{IB}}(\Gamma_k)$ (a pure detection bound).
3. **Full-data DPI** shows that no detector beats the all-seeing one, exponent $\le E^{\mathrm{cen}}$.
4. Take the smaller of 2 and 3. Done.

*Why this decomposition works:* it cleanly separates "how much gets through the network" (Lemma A, graph theory
+ entropy) from "how good a test can be with that much" (Lemma B, information theory of testing). Neither step
knows about the other; their composition is the theorem. This separation is *why the answer is a clean min of a
network term and a statistics term*.

### 8.1.1 Lemma A — the Cut-Set Information Bound (complete, every step)

**Goal.** Show $I(M_k^{(T)};\theta) \le \sum_{t=1}^T \min_{S\in\mathrm{Cut}(k)} \sum_{(i,j)\in S} C_{ij}(t)$,
i.e., the total information about $\theta$ that node $k$ can accumulate over $T$ rounds is at most the sum of
per-round min-cuts. Dividing by $T$: the *rate* of information about $\theta$ is $\le \Gamma_k$.

**Strategy.** Convert the changing, cyclic network into a single static *acyclic* graph by time-expansion; then
bound the information crossing *any* cut by the entropy budget of the edges in that cut; then take the tightest
cut and sum over rounds.

**Step 1 — build the time-expanded graph $\mathcal G$.** Create a vertex $(i,t)$ for every agent $i$ and round
$t$. For each active link $(i,j)\in E_t$, draw a directed edge $(i,t)\to(j,t+1)$ with capacity $C_{ij}(t)$. Add
"memory" edges $(i,t)\to(i,t+1)$ with *infinite* capacity (an agent remembers its own state to the next round).
The observation vertices $\{(i,t): i \text{ sees } X_{i,t}\}$ are the *sources*; the sink is $(k,T)$.
*Why this step:* the original graph is cyclic and time-varying, which makes "information flow" ambiguous. In
$\mathcal G$, time only moves forward, so $\mathcal G$ is a **DAG** (directed acyclic graph) — standard cut/flow
reasoning applies. *What would fail without it:* on a cyclic graph you cannot even define a consistent
topological order; information could appear to "loop," and the cut-set argument would be ill-posed. *Key fact:*
any cut separating the sources from $(k,T)$ in $\mathcal G$ corresponds, round by round, to a cut $S\in
\mathrm{Cut}(k)$ in the original $G_t$.

**Step 2 — the per-edge entropy bound.** On a directed, noiseless, orthogonal edge with a hard budget, the
transmitted message satisfies $H(M_{ij,t}) \le C_{ij}(t)$ (that *is* the meaning of [H-Rate]). Therefore, even
conditioning on the entire past,
$$ I(M_{ij,t};\theta \mid \text{past}) \le H(M_{ij,t}\mid\text{past}) \le H(M_{ij,t}) \le C_{ij}(t). $$
*Justifications, left to right:* (a) $I(A;B)\le H(A)$ always — mutual information cannot exceed the entropy of
either variable (Section 2.3; information about $\theta$ carried by a symbol cannot exceed the symbol's own
uncertainty). (b) Conditioning reduces entropy, $H(A\mid C)\le H(A)$ (Section 2.3). (c) [H-Rate], the physical
budget. *Interaction is allowed:* $M_{ij,t}$ may depend on everything $i$ has heard so far; the bound is on the
*transmitted symbol's* entropy, not on how it was computed — so cleverness in *forming* the message cannot
smuggle in more than $C_{ij}(t)$ nats. *(Under the soft "MI model," replace with $I(M;\theta)\le I(M;X_i)\le C$
via the Markov chain $\theta - X_i - M$ and DPI — same conclusion.)*

**Step 3 — the cut-set bound (the crux).** Fix any source-separating cut $S$ at round $t$. All information about
$\theta$ that crosses from the source side to $k$'s side at that round must ride on the edges of $S$. So
$$ I\big(\theta; \{M_{ij,t}:(i,j)\in S\}\mid\text{past}\big)
   \;\overset{(a)}{\le}\; H\big(\{M_{ij,t}:(i,j)\in S\}\mid\text{past}\big)
   \;\overset{(b)}{\le}\; \sum_{(i,j)\in S} H(M_{ij,t}\mid\text{past})
   \;\overset{(c)}{\le}\; \sum_{(i,j)\in S} H(M_{ij,t})
   \;\overset{(d)}{\le}\; \sum_{(i,j)\in S} C_{ij}(t). $$
*Justifications:* (a) $I\le H$ again; (b) **subadditivity of entropy** — the joint entropy of several symbols is
at most the sum of their individual entropies (the whole is no more uncertain than the sum of parts, Section
2.3); (c) conditioning reduces entropy; (d) [H-Rate]. *What would fail if step (b) were wrong:* if joint entropy
could *exceed* the sum of parts, a cut could carry more than the sum of its edge budgets, and the bottleneck
would not bind — the entire theorem would collapse. Subadditivity is exactly what makes a "cut" meaningful.
Now take the *tightest* cut, $\min_{S\in\mathrm{Cut}(k)}$, and sum over all rounds $t=1..T$. Because $\mathcal G$
is a single static DAG encoding all rounds, the correct bound is the **sum of per-round min-cuts**, *not* the
min-cut of a time-averaged graph (these differ when the binding cut moves round to round — a subtle but
important point). This yields exactly the Lemma A inequality. *(This is the deterministic-orthogonal-network
cut-set argument, El Gamal–Kim Ch. 16; it is tighter than the general noisy-channel cut-set bound, which is not
needed because the links here are noiseless and orthogonal.)*

**Step 4 — from $T$-round total to per-sample rate.** Divide by $T$ and take $\liminf_T$. By [H-Top]
(stationary ergodic) and Birkhoff's ergodic theorem (Section 2.13), $\frac1T\sum_t(\text{per-round min-cut})
\to \Gamma_k$ almost surely. So $\limsup_T \frac1T I(M_k^{(T)};\theta) \le \Gamma_k$. $\blacksquare$

**Why interaction cannot beat this.** Multi-round back-and-forth can *use* the rate more cleverly (raising
achievable exponents), but the *total entropy crossing a fixed cut over $T$ rounds* is still
$\le \sum_t\sum_{(i,j)\in S}C_{ij}(t)$ — an accounting identity, immune to protocol cleverness. So Lemma A is
valid for interactive schemes; the converse is not fooled by chattiness.

### 8.1.2 Lemma B — the Rate-Limited Stein Upper Bound (complete, every step)

**Goal.** Show that if node $k$'s decision uses a description $M_k$ carrying at most $\Gamma$ nats/sample about
$\theta$, then its Type-II exponent is $\le \theta_{\mathrm{IB}}(\Gamma)$ (against independence), or
$\le \theta_{\mathrm{SHA}}(\Gamma)$ (general pair).

**Strategy.** Recognize that "detect from a rate-$\Gamma$ description" is *exactly* the Ahlswede–Csiszár
compressed-hypothesis-testing problem, whose optimal exponent is the IB functional; then invoke that result.

**Step A — against independence (tight).** The test is $H_0: P_{XY}$ (correlated) vs $H_1: P_X P_Y$
(independent), with $Y$ the relevance variable. Node $k$ holds a description $U = M_k$ of $X$ constrained by the
cut to $I(U;X_{\mathcal S}) \le \Gamma$. *Ahlswede–Csiszár (1986), Theorem 5* (taught in Section 5.2) says the
best Type-II exponent achievable from such a rate-$\Gamma$ description is *exactly*
$\max_{p(u\mid x): I(U;X)\le\Gamma} I(U;Y) = \theta_{\mathrm{IB}}(\Gamma)$. Rahman–Wagner (2012) confirm this is
*tight* (the binning correction is inactive for against-independence). Hence $E_k \le \theta_{\mathrm{IB}}
(\Gamma)$. *Intuition:* the best you can do with $\Gamma$ nats about $X$ is to spend them on the *most
$Y$-relevant* nats — which is precisely what the IB maximization computes.

**Step B — general pair (converse only).** For a general $(\theta_0,\theta_1)$, apply the *Shimokawa–Han–Amari*
converse: $E_k \le \theta_{\mathrm{SHA}}(\Gamma) = \min_{p(\tilde u\mid x): I(\tilde U;X)\le\Gamma} D(P_{\tilde
U}\Vert Q_{\tilde U})$. This is a *different* functional (a minimized KL between induced marginals), and it
equals $\theta_{\mathrm{IB}}$ *only* in the against-independence case. This is why the general-pair claim is
weaker (converse only).

**Step C — the two data-processing steps used.** (i) $I(M_k;\theta) \le I(M_k;X_{\mathcal S}) \le \Gamma$ uses
the **DPI for mutual information** along the Markov chain $\theta - X_{\mathcal S} - M_k$ (the message depends on
$\theta$ only through the data $X$). (ii) The exponent-to-divergence link uses the **DPI for KL divergence**:
$D(P_{M_k\mid\theta_0}\Vert P_{M_k\mid\theta_1}) \le D(P_{X\mid\theta_0}\Vert P_{X\mid\theta_1})$ — compressing
the data can only make the two hypotheses *harder* to tell apart, never easier. *What would fail if DPI were
false:* a compressor could *manufacture* discriminating information from thin air, and a rate-$\Gamma$ node
could beat the full-data detector — absurd, and exactly what DPI forbids. $\blacksquare$

### 8.1.3 Combining, and the full-data ceiling

By Lemma A, $\frac1n I(M_k;\theta) \le \Gamma_k$. By Lemma B, $E_k \le \theta_{\mathrm{IB}}(\Gamma_k)$.
*Independently*, node $k$'s data is a function of all observations, so by the KL-DPI its exponent cannot exceed
the full-data detector's, $E_k \le E^{\mathrm{cen}}$ (which equals $\sum_i D_i$ under [H-CI], via Stein). Taking
the smaller of the two ceilings gives the boxed converse
$E_k \le \min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$. Each assumption's role: [H-CI] $\to$
$E^{\mathrm{cen}}=\sum_i D_i$; [H-Rate] $\to$ the per-edge bound; [H-Top] $\to$ $\Gamma_k$ a constant; [H-T1]
$\to$ the (level-independent) Stein exponent. $\blacksquare$

### 8.1.4 Strictness (why below saturation you strictly lose)

$\theta_{\mathrm{IB}}$ is concave and non-decreasing (Section 2.11), and first reaches $E^{\mathrm{cen}}$ at
$C_{\mathrm{DIB}}$ (Prop. 1.0-A). Suppose, for contradiction, it were *flat* on some $[a, C_{\mathrm{DIB}}]$ with
$a < C_{\mathrm{DIB}}$. A concave function that is constant on an interval must be constant on *everything to the
right* of it (concavity forbids it from rising again). That would make it flat on $[a,\infty)$, contradicting
that it only reaches its ceiling at $C_{\mathrm{DIB}} > a$. Hence it is *strictly* increasing on
$[0, C_{\mathrm{DIB}})$, so $\Gamma_k < C_{\mathrm{DIB}} \Rightarrow \theta_{\mathrm{IB}}(\Gamma_k) <
E^{\mathrm{cen}}$. $\blacksquare$ *Intuition:* the concave shape means "no free flat stretch before the top" —
every nat below saturation buys strictly positive extra exponent.

## 8.2 Achievability D1★★ = Lemmas A-D1 (encode) + B-D1 (decode) + C-D1 (aggregate)

**Overall strategy.** Build a scheme whose exponent *reaches* the converse. Three moving parts, each a lemma:
(1) compress optimally into a network-codeable form; (2) transport and decode without rate loss; (3) aggregate
the changing cuts to their ergodic mean. Compose to get exponent $\ge \min\{E^{\mathrm{cen}},
\theta_{\mathrm{IB}}(\Gamma_k)\} - \delta$ for any $\delta>0$.

### 8.2.1 Lemma A-D1 — Type-Preserving Network Encoding over $\mathrm{GF}(q)$

**Construction.** Fix a block length $n$. Each agent $i$ passes its data through the *IB-optimal test channel*
$p^\star(u_i\mid x_i)$ — the compressor that achieves the IB boundary at its allocated rate $R_i$ (allocation by
water-filling, Section 4.5; on the binding cut, the $R_i$ sum to $\Gamma_k$). Concretely: draw a random codebook
of IB codewords; quantize $X_i^n$ to the codeword *jointly typical* with it (index $w_i$); then **bin** the
index into $\mathrm{GF}(q)$ symbols $b_i$ by a random hash (this "binning," from Wyner–Ziv/Berger–Tung source
coding, reduces the description rate to exactly $R_i$ without losing the relevant information, because a decoder
with side information $Y$ can resolve the bin). Each network edge carries a *random linear combination over
$\mathrm{GF}(q)$* of everything the tail node holds.

**Why "type-preserving" is the key phrase.** A hypothesis test based on *typical sets* depends only on the
**empirical joint distribution** (the "type") of the codewords and $Y$ — not on their identity. The worry is
that algebraic mixing (random linear combinations) might scramble the type and ruin the test. The lemma proves
it does not: because finite-field recovery is **exact** (zero distortion — you get the bins back perfectly once
you can solve the linear system), the recovered indices are the *true* indices, so the joint *type* of the
codewords and $Y$ is *invariant under transport*. Coding moves the data around but preserves the one statistic
the test cares about. *That is the entire content of "type preservation."*

**Why it recovers (the finite-field guarantee).** RLNC delivers the bins losslessly iff the global transfer
matrix $M$ (from source bins to $k$'s received symbols, over the time-expanded DAG) has *full column rank* over
$\mathrm{GF}(q)$. By the **Schwartz–Zippel lemma** (a random low-degree polynomial rarely vanishes), $M$ is
full-rank with probability $\ge 1 - |E|/q$ — approaching 1 as the field size $q$ grows. *Cycles* are fine
because the transfer matrix is defined on the acyclic time-expanded DAG (memory edges linearize the loops).

### 8.2.2 Lemma B-D1 — Distributed Independent-Codebook Joint Decoding (no rate loss)

**The worry.** The agents build their codebooks *independently* (sharing only public random seeds). Can node
$k$ jointly decode them without paying a coordination penalty in rate?

**The construction and answer.** Node $k$ collects its incoming linear observations $\mathbf y_k = M\,\mathbf b
\pmod q$. The number of *independent* $\mathrm{GF}(q)$ equations reaching $k$ equals the time-expanded min-cut,
$= n\Gamma_k/\ln q$ (Lemma C-D1). Since $M$ is full column-rank w.h.p., the system is solvable for $\mathbf b$
*iff* the total rate $\sum_i R_i \le \Gamma_k$ — i.e., you can decode exactly up to the min-cut, and no more.
Solve by Gaussian elimination over $\mathrm{GF}(q)$. Then **un-bin**: for each agent, find the unique IB codeword
in the recovered bin that is jointly typical with $Y^n$ (this succeeds w.h.p. because the binning rate was chosen
as $R_i \ge I(U_i;X_i) - I(U_i;Y)$ — the Wyner–Ziv/Slepian–Wolf condition, meaning "the side information $Y$
closes the gap the binning opened"). The *no-alignment-loss* guarantee for *independently* built codebooks is
the Han–Verdú **information-spectrum** method: the relevant "spectral inf-information rate" equals $I(U_{1:N};Y)$
for stationary sources, so independent codebooks lose nothing versus a jointly designed one. Result: $k$ recovers
all summaries and realizes *exactly* $\Gamma_k$ nats/sample of relevant information — the input to the optimal
test.

### 8.2.3 Lemma C-D1 — Ergodic Time-Varying Cut Aggregation

**The worry.** The graph changes every round; does block-coding over $T$ rounds really deliver the *ergodic
mean* min-cut with no leftover gap?

**The answer.** Run RLNC over super-blocks of $T$ rounds on the time-expanded DAG $\mathcal G_{1:T}$. By
min-cut = max-flow for the *static* DAG (ACLY 2000), the source-to-$k$ max-flow equals $\sum_{t=1}^T
(\text{per-round min-cut})$. Divide by $T$ and use ergodicity (Birkhoff): this $\to \Gamma_k$ almost surely.
RLNC achieves any rate below max-flow with failure $\le |E|T/q$; choosing the field size to grow with the block,
$q = q(T) \to \infty$ (e.g. $q = T^2$), sends the coding-failure probability to zero *faster than any fixed
exponent*, at a vanishing field-size rate cost ($\frac{\ln\ln q}{\ln q}\to 0$). So the delivered per-sample
relevant rate converges to $\Gamma_k$ while the transport error exponent $\to\infty$ (transport becomes
effectively free). $\blacksquare$

### 8.2.4 Composition — putting the three lemmas together

For any $\eta>0$: choose $T, q$ (Lemma C-D1) so the delivered rate is $\ge \Gamma_k - \eta$ and the transport
error is $\le e^{-n\zeta}$ with $\zeta$ as large as we like. By Lemmas A-D1/B-D1, node $k$ recovers the
rate-$(\Gamma_k-\eta)$ IB summaries and $Y^n$, then runs the joint-typicality (log-likelihood) test. By
Ahlswede–Csiszár achievability and Rahman–Wagner tightness, this test's Type-II exponent is
$\theta_{\mathrm{IB}}(\Gamma_k-\eta)$. Transport adds at most $e^{-n\zeta}$ to the error; picking $\zeta >
\theta_{\mathrm{IB}}$ makes transport negligible, leaving the exponent at $\theta_{\mathrm{IB}}(\Gamma_k-\eta)$.
The full-data ceiling caps everything at $E^{\mathrm{cen}}$. So the achieved exponent is $\min\{E^{\mathrm{cen}},
\theta_{\mathrm{IB}}(\Gamma_k-\eta)\}$. Let $\eta\to 0$; by continuity of the concave $\theta_{\mathrm{IB}}$ this
$\to \min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$. Since $E_k$ is the supremum over schemes, it
*equals* the converse. **Zero gap.** $\blacksquare$

## 8.3 The Gaussian closed forms (deriving the numbers the experiments use)

The experiments need explicit $\theta_{\mathrm{IB}}$ and the *exponent of a rate-$R$ Gaussian summary*. Here is
the derivation used in `code/d1_detect.py`, taught from scratch.

**The IB-optimal Gaussian summary.** For jointly Gaussian $(X,Y)$ with $\mathrm{corr}=\rho$, the rate-$R$
IB-optimal $U$ is $U = aX + \xi$ (a scaled, noisy copy of $X$) with the noise level set so $I(U;X)=R$, i.e.
$a^2/\sigma_\xi^2 = e^{2R}-1$. *Why linear-Gaussian:* for Gaussian sources the optimal IB channel is Gaussian
(Chechik–Globerson–Tishby–Weiss 2005) — no need to search over exotic compressors.

**The induced $U$–$Y$ correlation.** Plug in $X = \rho Y + \sqrt{1-\rho^2}Z$:
$$ r_{UY}^2 = \mathrm{corr}(U,Y)^2 = \rho^2\big(1 - e^{-2R}\big). $$
*Derivation:* $\mathrm{Cov}(U,Y)=a\rho$, $\mathrm{Var}(U)=a^2+\sigma_\xi^2$, so $r_{UY}^2 = a^2\rho^2/(a^2+
\sigma_\xi^2) = \rho^2(1 - 1/(1+a^2/\sigma_\xi^2)) = \rho^2(1 - e^{-2R})$, using $1+a^2/\sigma_\xi^2 = e^{2R}$.

**The exponent equals a mutual information.** For the against-independence test on $(U,Y)$, the Stein exponent is
$D(P_{UY}\Vert P_U P_Y) = I(U;Y) = -\tfrac12\ln(1 - r_{UY}^2) = -\tfrac12\ln(1 - \rho^2(1-e^{-2R})) =
\theta_{\mathrm{IB}}(R)$. *So the exponent of the rate-$R$ summary is exactly the IB curve* — the concrete
verification of Lemma B in the Gaussian case. This identity ($\text{exponent} = I(U;Y) = \theta_{\mathrm{IB}}(R)$)
is checked numerically in the repo: `exponent_from_r` = `theta_IB_single` to machine precision.

---

# SECTION 9 — EXPERIMENTS (scientific explanation, not code)

## 9.0 The measurement problem, and how it is solved (read this before any experiment)

**The obstacle.** The theorem is about *error exponents* $E_k$. To measure an exponent you must estimate a
Type-II error $\beta_n$ and read off its decay rate. But for the standing model $E^{\mathrm{cen}}=2$ nats, so
$\beta_n \approx e^{-2n}$: at $n=50$ samples that is $e^{-100} \approx 10^{-43}$. No Monte-Carlo simulation with a
realistic number of trials will *ever* see a single error event — the naive "count the errors" method suggested
in the bible's simulation sketch is *physically infeasible*. This is a genuine methodological hazard the
handbook resolves.

**The solution: exact saddlepoint evaluation of the optimal detector.** The best detector is the
Neyman–Pearson likelihood-ratio test: threshold the log-likelihood-ratio (LLR) statistic. For the Gaussian
model, the *per-sample* LLR is a **quadratic form in Gaussian variables**, whose *cumulant generating function*
(CGF) — the log of its moment generating function — is known in closed form. The $n$-sample LLR is a sum of $n$
i.i.d. such variables, so its CGF is $n$ times the per-sample CGF. The exact tail probability of this sum (i.e.
$\beta_n$) is then computed by the **Lugannani–Rice saddlepoint formula**, a classical, extremely accurate
method for tail probabilities of sums (accurate to relative error $O(1/n)$, and — crucially — computed in
*log-space* so it never underflows, working perfectly even at $\beta_n = 10^{-400}$). This is *not* a
simulation; it is an exact numerical evaluation of the optimal detector's error. It is implemented in
`code/d1_detect.py` and is the instrument behind every D1 exponent number.

**Extracting the exponent (dispersion-corrected fit).** From the exact $\beta_n$ over a grid of $n$, the
asymptotic exponent is read off by fitting $-\ln\beta_n = a\,n + b\sqrt n + c$ and taking $a$ as the exponent.
The $b\sqrt n$ term is exactly the Strassen dispersion correction (Section 2.8); including it removes the
finite-$n$ bias that would otherwise make the measured exponent fall short. This is why the reported exponents
match $\theta_{\mathrm{IB}}$ to $\sim 0.001$ nats.

**The independent cross-check.** To prove the saddlepoint is not fantasy, it is compared to a *real* Monte-Carlo
simulation of the detector in the regime where $\beta_n$ *is* measurable (roughly $10^{-1}$ to $10^{-5}$,
achieved by using small $n$ or low-rate points). The repo (`resultsD1.md`, D1-E1) reports, e.g., at
$\Gamma=0.20, n=60$: saddlepoint $\beta = 1.24\times10^{-2}$, Monte-Carlo $\beta = 1.21\times10^{-2}$ — agreement
to $\sim 2\%$. Having validated the instrument, we trust it in the deep-tail regime where MC cannot go.

**Why this increases confidence.** It means the exponent numbers are *exact optimal-detector* values, not noisy
estimates, and they are validated against a genuine simulation where feasible. A reviewer cannot dismiss them as
Monte-Carlo artifacts.

## 9.1 Experiment D1-E1 — the rate sweep (the headline validation)

**Purpose / which theorem.** Validate the *achievability* $E_k = \theta_{\mathrm{IB}}(\Gamma)$ *and* the
*converse ceiling* $E_k \le E^{\mathrm{cen}}$ simultaneously, across a wide range of bandwidths — the core of
both D1★ and D1★★.

**Hypothesis before running.** The measured exponent should (i) track the closed-form $\theta_{\mathrm{IB}}
(\Gamma)$ curve, (ii) never exceed the ceiling $E^{\mathrm{cen}} = 2$, (iii) approach the ceiling with a soft
knee near $C_{\mathrm{DIB}}$.

**Model / parameters.** Gaussian against-independence, $N=4$ agents, $\rho=0.795$ (so $E^{\mathrm{cen}}=2$
nats). Sweep the total cut budget $\Gamma$ over a grid (0.2 to ~12 nats). Type-I level $\varepsilon=0.05$.
Exponents via saddlepoint over $n$-grids, dispersion-corrected; two low-rate points cross-checked against
plain MC.

**Metrics.** Mean absolute error MAE between measured exponent and $\theta_{\mathrm{IB}}(\Gamma)$; the maximum
*exceedance* (measured minus $\theta_{\mathrm{IB}}$) — a positive exceedance would *falsify the converse*.

**Observed outcome (from `resultsD1.md`).** MAE $= 0.0011$ nats; maximum exceedance $= -0.0011$ (i.e. the
measured exponent is *never above* $\theta_{\mathrm{IB}}$ — converse respected everywhere); $E^{\mathrm{cen}}=2$;
knee $C_{\mathrm{DIB}}$(2% saturation) $= 8.887$. Plain-MC spot checks match the saddlepoint (e.g. $1.24$e-2 vs
$1.21$e-2).

**Interpretation.** The single most important plot: the black measured points sit *on* the blue
$\theta_{\mathrm{IB}}(\Gamma)$ curve and *below* the orange $E^{\mathrm{cen}}$ line, everywhere. This is D1★ and
D1★★ in one picture — the exponent is *exactly* $\theta_{\mathrm{IB}}(\Gamma)$ and it *never* beats the ceiling.

**Reviewer questions.** *"Why does it not reach the ceiling at finite $\Gamma$?"* Because for the Gaussian model
$\theta_{\mathrm{IB}}$ saturates only asymptotically (a soft knee); a *hard* kink needs bounded/discrete
relevance. *"Is the fit honest?"* Yes — the dispersion term is the theoretically-predicted Strassen correction,
not a free fudge; the raw slope (reported alongside) is biased low exactly as theory predicts.

## 9.2 Experiment D1-E2 — the converse across schemes (is $\theta_{\mathrm{IB}}$ a real upper bound?)

**Purpose / theorem.** Test that $\theta_{\mathrm{IB}}$ is a genuine *upper envelope* over *all* rate-$R$
schemes, not merely the value of one clever encoder — the essence of the converse D1★.

**Hypothesis.** Every quantizer, plotted at its operating point $(I(U;X), I(U;Y))$, must lie *on or below* the
curve $I(U;Y) = \theta_{\mathrm{IB}}(I(U;X))$. No scheme may poke above it.

**Model / parameters.** For a range of level counts $L$, build *uniform* scalar quantizers and *Lloyd–Max*
(MSE-optimal) quantizers of the Gaussian $X$; compute their exact $(I(U;X), I(U;Y))$ by numerical integration.

**Metric.** The maximum violation $\max[I(U;Y) - \theta_{\mathrm{IB}}(I(U;X))]$; must be $\le 0$ (up to numerical
tolerance).

**Observed (from `resultsD1.md`).** Maximum violation $= -3.30\times10^{-3}$ (no scheme exceeds the envelope);
Lloyd–Max sits *closer* to the envelope than uniform at equal level count, but *neither* touches it — only the
*soft* IB test channel (not a hard quantizer) attains the boundary.

**Interpretation.** This separates the *converse* (the envelope bounds everyone) from *achievability* (only the
IB-optimal soft compressor is tight). It answers the sharpest converse attack — "is $\theta_{\mathrm{IB}}$ just
one encoder's score?" — with "no, it upper-bounds every encoder we can build."

## 9.3 Experiment D1-E3 — min-cut sufficiency (topology does not matter beyond $\Gamma_k$)

**Purpose / theorem.** Validate that $\Gamma_k$ is a *sufficient statistic* for the network (Contribution 2):
at matched $\Gamma_k$, the exponent is the same regardless of graph structure.

**Hypothesis.** Scale edge capacities so that all topologies share the *same* $\Gamma_k$; then all measured
exponents should collapse to the single value $\theta_{\mathrm{IB}}(\Gamma_k)$.

**Model / parameters.** Ten topologies: complete, ring, path, star, grid, tree, Erdős–Rényi, Barabási–Albert,
Watts–Strogatz, and a *directed* ring. For each, compute $\Gamma_k$ by min-cut (`code/topology.py`), then rescale
edge capacities so $\Gamma_k = 3.0$ for all. Measure the exponent at each.

**Metric.** The *spread* (max minus min) of the ten measured exponents; and their MAE vs $\theta_{\mathrm{IB}}
(3.0)$.

**Observed.** Spread $= 0.0000$ nats; MAE vs $\theta_{\mathrm{IB}} = 0.0010$. Ten wildly different graphs, one
exponent.

**Interpretation.** Direct, striking confirmation that only the cut matters. *Caveat noted honestly:* this
version re-uses $\Gamma_k$ analytically, so on its own it could be called "circular" — which is precisely why
experiment D1-N1 re-does it with *genuine routing* (below). Together they make the sufficiency claim airtight.

## 9.4 Experiment D1-E4 — water-filling over heterogeneous agents

**Purpose / theorem.** Validate the optimal budget allocation across agents of unequal informativeness (Section
4.5) and confirm the measured exponent matches the water-filling prediction.

**Hypothesis.** Water-filling beats equal splitting; the measured exponent equals the water-filling
$\theta_{\mathrm{IB}}$.

**Parameters.** $\{\rho_i\} = \{0.95, 0.85, 0.7, 0.5\}$ (so $E^{\mathrm{cen}} = 2.2854$); sweep $\Gamma$; at each
$\Gamma$ compute the water-filling allocation and the equal-split allocation, and measure the exponent under
water-filling.

**Metrics.** Maximum gain of water-filling over equal-split; MAE(measured, water-filling prediction).

**Observed.** Max gain $= 0.3045$ nats (a large, practically meaningful improvement); MAE $= 0.0010$.

**Interpretation.** Confirms both the allocation formula and the additive structure $\sum_i \theta_{\mathrm{IB},i}
(R_i)$. At low budget the weakest agent ($\rho=0.5$) is *cut off* (zero rate) — the water-filling shape — visible
as a slope change in the plot.

## 9.5 Experiment D1-E5 — scaling in the number of agents

**Purpose / theorem.** Characterize how the exponent scales with $N$, in two regimes.

**Hypothesis.** (a) With *fixed per-agent rate*, exponent grows *linearly* in $N$ (more agents = more
independent evidence). (b) With *fixed total budget* $\Gamma$, per-agent rate $\Gamma/N$ shrinks and the
exponent *bends over* (the shared cut throttles).

**Parameters.** $N \in \{2,3,4,6,8,12,16\}$; regime (a) fixed $R=0.5$; regime (b) fixed $\Gamma=2$.

**Observed.** (a) MAE(measured, $N\cdot\theta_{\mathrm{IB},i}$) $= 0.0011$ — clean linear growth. (b)
MAE(measured, $\theta_{\mathrm{IB}}(\Gamma)$) $= 0.0012$ — the exponent flattens as agents are starved of rate.

**Interpretation.** Cleanly separates "more evidence" from "more channel." Adding agents without adding
bandwidth does not help (regime b) — a direct, useful engineering statement.

## 9.6 Experiment D1-E6 — dynamic (time-varying) topology (the ergodic average binds)

**Purpose / theorem.** Validate Lemma C-D1 / Contribution 3: for a changing network, the exponent is set by the
*ergodic mean* of the per-round min-cuts, not the best or worst round.

**Hypothesis.** The exponent equals $\theta_{\mathrm{IB}}(\bar\Gamma_k)$ with $\bar\Gamma_k$ the time-average;
the min-round and max-round predictions are wrong.

**Parameters.** Each round the graph is drawn from a fixed set $\{$ring, path, star, ER, complete$\}$; run many
rounds; compute the per-round min-cuts and their average.

**Observed.** Ergodic mean $\bar\Gamma_k = 2.8950$ (per-round range $[1.00, 5.00]$); measured exponent $=
1.4883$; $\theta_{\mathrm{IB}}(\bar\Gamma_k) = 1.4893$ (error $0.0010$). Using the min-round would predict
$0.592$; the max-round $2.157$ — both badly wrong.

**Interpretation.** The time-average, and *only* the time-average, predicts the exponent — the operational
content of the ergodic cut-aggregation lemma.

## 9.7 Experiment D1-E7 — second-order dispersion (validates §1.5.1)

**Purpose / theorem.** Validate the finite-sample (second-order) correction: the relative-entropy variance $V$
governs the $\sqrt n$ term.

**Hypothesis.** $-\ln\beta_n = n\theta_{\mathrm{IB}} - \sqrt{nV}\,\Phi^{-1}(\varepsilon) + O(\ln n)$, and the
$\sqrt n$ coefficient is linear in $\Phi^{-1}(\varepsilon)$ with slope $\sqrt V$; the measured $V$ matches the
analytic relative-entropy variance.

**Parameters.** A fixed operating point with $\theta_{\mathrm{IB}} = 1.0202$; five Type-I levels
$\varepsilon \in \{0.01, 0.05, 0.1, 0.2, 0.35\}$; measure the $\sqrt n$ coefficient at each from the exact
$\beta_n$ curve.

**Observed.** Analytic $V = 1.5983$; measured $V = 1.6008$ (relative error $0.2\%$); coefficient MAE across the
five levels $= 0.0013$.

**Interpretation.** The dispersion is not a fudge — it is the theoretically-predicted quantity, recovered to
sub-percent accuracy across five false-alarm levels. This validates the second-order refinement and justifies
the dispersion-corrected fit used everywhere else.

## 9.8 Experiment D1-N1 — the *genuine* network (fixing the circularity of E3)

**Purpose / theorem.** Re-do the min-cut-sufficiency test *without* re-using $\Gamma_k$ analytically: route
*real* information through the *actual* graph, so the delivered rate *emerges* from routing and can *differ by
scheme* on the same graph. This is the non-circular version of D1-E3 (Contribution 2 + 4).

**Hypothesis.** Successive-refinement / network coding (SR) should *attain* the min-cut (its exponents collapse
across topologies at matched $\Gamma_k$), while *naive* quantize-and-forward should fall *short* (its exponents
spread, because Gaussian MMSE fusion is sub-additive in nats). No scheme should exceed $\theta_{\mathrm{IB}}
(\Gamma_k)$.

**Parameters.** Matched min-cut $\Gamma_k = 2.5$ across ten topologies; a Monte-Carlo of the actual
sample-and-fuse pipeline verifies the *emergent* effective correlation matches the analytic rate.

**Observed.** SR delivers exactly the cut on every topology $\Rightarrow$ exponent spread $= 0.0000$ (genuine
collapse via real routing). Naive delivers $\tfrac12\ln(1+\sum_p(e^{2f_p}-1)) < $ cut whenever there is more than
one path $\Rightarrow$ exponent spread $= 0.1931$ (topology-dependent!). No scheme on any topology exceeds
$\theta_{\mathrm{IB}}(\Gamma_k)$ (max over-shoot $= -0.0008$). MC effective correlations match analytic to
$\sim 10^{-3}$.

**Interpretation.** This is the decisive answer to "is E3 circular?" — *no*: with real routing, the exponent
*does* depend on the scheme (naive spreads by 0.19 nats), so the SR collapse to $0.0000$ is a *genuine* fact
about achieving the cut, and it simultaneously shows *why coding is needed* (naive forwarding is sub-additive and
falls short). One experiment delivers the converse (nothing exceeds the cut), the achievability (SR attains it),
the sufficiency (collapse), and the coding-necessity insight.

## 9.9 Experiment D1-N2 — large-scale ($N$ up to 1000)

**Purpose.** Show the cut result survives at scale — a reviewer will ask "does this only work for $N=4$?"

**Parameters.** $N \in \{20, 50, 100, 200, 500, 1000\}$ on Erdős–Rényi, Barabási–Albert, Watts–Strogatz graphs;
compute $\Gamma_k$ and the SR vs naive delivered rates and exponents.

**Observed.** The max-flow + path-decomposition pipeline runs in well under a second per graph up to $N=1000$;
the SR exponent tracks $\theta_{\mathrm{IB}}(\Gamma_k)$ at every scale; naive stays below.

**Interpretation.** Scale-independence confirmed; the theory is not an artifact of tiny networks.

## 9.10 Experiment D1-N3 — non-Gaussian discrete converse

**Purpose.** Answer "only Gaussian?" — test the converse on a *discrete* alphabet.

**Parameters.** A discrete $K=8$ model with $E^{\mathrm{cen}} = I(X;Y) = 0.2543$; five "merge" quantizers.

**Observed.** All five quantizers satisfy $I(U;Y) \le \theta_{\mathrm{IB}}(I(U;X))$; maximum violation
$= 3.41\times10^{-6}$ (numerical tolerance).

**Interpretation.** The converse envelope holds for discrete models too, not just Gaussian — the theorem is not
Gaussian-specific.

## 9.11 Experiment D1-N4 — edge cases and failures (graceful degradation)

**Purpose.** Probe the boundary: near-disconnection, random link failures, a single bridge.

**Parameters.** An Erdős–Rényi graph ER(30, 0.25); sweep the edge-failure probability $f$ from 0 to 0.95;
separately, a two-clique graph joined by a single bridge.

**Observed.** $\Gamma_k$ falls from $6.00$ (at $f=0$) to $0.38$ (at $f=0.95$); the exponent $E_k$ tracks
$\theta_{\mathrm{IB}}(\Gamma_k)$ and $\to 0$ as the source disconnects from $k$. The single-bridge graph has
$\Gamma_k = 1.00$ = the bridge capacity exactly.

**Interpretation.** The bound degrades *gracefully*: as connectivity vanishes, the exponent smoothly $\to 0$
(agents cannot beat chance once cut off — $\theta_{\mathrm{IB}}(0)=0$), with *no pathological violations at the
boundary*. The bridge case confirms the *bottleneck* interpretation literally.

## 9.12 Experiment D1-N5 — genuine $\mathrm{GF}(q)$ RLNC achievability (the flagship code experiment)

**Purpose / theorem.** Close the achievability at *code level*: simulate an *actual* random linear network code
over $\mathrm{GF}(q)$ and show it attains the min-cut, on the hard cases — multicast (fusion-free), the butterfly
(coding vs routing), and cyclic + time-varying graphs. This is Contribution 4 made concrete and upgrades D1★★
from "modeled" to "simulated."

**Hypotheses (five sub-claims).** (a) The code recovers all $h$ source descriptions *iff* $h \le F$ (the
min-cut) — a sharp threshold. (b) Recovery probability $\to 1$ as field size $q$ grows (matching the
$(1-h/q)^{|E|}$ Ho bound). (c) On the butterfly, coding delivers the min-cut 2 to *both* sinks while routing
delivers only 1. (d) Cyclic + time-varying graphs are handled by time-expansion. (e) The delivered $\Gamma_k$
gives exponent $\theta_{\mathrm{IB}}(\Gamma_k)$.

**Parameters.** A layered DAG with min-cut $F=4$ for (a); field sizes $q \in \{2,3,5,7,17,61,257,1031\}$ for (b);
the butterfly for (c); a time-expanded 6-round cyclic sequence for (d); a complete graph $K_6$ at $\Gamma_k=3$
for (e).

**Observed (from `resultsD1.md`).** (a) Recovery $=1.0$ for $h \le F=4$ and *collapses* for $h>F$:
`rec=[1.0,1.0,1.0,0.99,0.0,0.0]` for $h=[1,2,3,4,5,6]$ — a razor-sharp min-cut threshold. (b) At the boundary
$h=F$, recovery rises $0.037$ (at $q=2$) $\to 0.998$ (at $q=1031$), above the Ho bound throughout. (c) Butterfly:
coding delivers min-cut $\{T1:2, T2:2\}$ to *both* sinks (rank-recovery $\{T1:0.993, T2:0.983\}$ at $q=257$)
while edge-disjoint routing multicast $=1$ — a *strict* coding gain. (d) Time-expanded (6 rounds): recover-all
rate $=1.000$, recoverable $=5$ ($F_{te}=16$, $h=5$). (e) On $K_6$ the delivered $\Gamma_k=3$ gives exponent
$1.529$ vs $\theta_{\mathrm{IB}}=1.530$.

**Interpretation.** An *actual finite-field code* — not a model — attains the min-cut, reliably as the field
grows, and *beats routing* on the multicast case that D1's fusion-free structure demands. This removes the
"you modeled TPNC, you didn't code it" objection. The small fields ($q=2,3$) failing even at $h=F$ (recovery
0.037 at $q=2$) show the field-size schedule of Lemma C-D1 is *not* cosmetic — it is required for reliability.

---

# SECTION 10 — VALIDATION (proving vs validating; what experiments can and cannot do)

## 10.1 The difference between *proving* and *validating*

A **proof** (Section 8) establishes a statement *with certainty* from axioms and prior theorems — it is true for
*all* cases in its scope, forever. An **experiment** *validates* by checking the proof's *predictions* against
independent computation on specific instances. Experiments cannot make a false theorem true, and they cannot
prove a true theorem (they only test finitely many cases). Their job is different: to catch *implementation
mistakes*, *hidden-assumption violations*, and *arithmetic errors* in the theory, and to build confidence that
the proof's assumptions actually hold in realizable systems. A theorem with a flawless proof but experiments
that disagree signals a *bug in the experiment or a violated assumption* — and chasing that discrepancy is how
the biggest issues (like the circularity below) were found.

## 10.2 What the D1 experiments validate

- **The converse D1★:** no scheme, on any of 10+ topologies, at scales to $N=1000$, on Gaussian *and* discrete
  alphabets, ever exceeds $\min\{E^{\mathrm{cen}}, \theta_{\mathrm{IB}}(\Gamma_k)\}$ (max exceedances are all
  $\le 0$ to numerical tolerance: $-0.0011$, $-3.3\times10^{-3}$, $-0.0008$, $3.4\times10^{-6}$).
- **The achievability D1★★:** the exponent *reaches* $\theta_{\mathrm{IB}}(\Gamma_k)$ (MAE $\sim 0.001$); an
  *actual* $\mathrm{GF}(q)$ code attains the cut (D1-N5); coding beats routing on the butterfly.
- **The sufficient-statistic claim:** genuine routing collapses 10 topologies to one exponent at matched
  $\Gamma_k$ (D1-N1/E3), while naive forwarding spreads — proving the collapse is real, not circular.
- **The ergodic-cut claim:** the time-average predicts the exponent (D1-E6).
- **The second-order refinement:** $V$ recovered to $0.2\%$ (D1-E7).

## 10.3 What the experiments *cannot* validate (remaining assumptions and honest gaps)

- **The general-pair exponent.** Everything tested is *against independence* (the tight, closed case). The
  general-pair distributed exponent is a different, open problem; D1 claims only a converse there.
- **A full symbol-level RLNC pipeline.** D1-N5 simulates the code at the *coding-vector (rank)* level — it proves
  recoverability attains the cut — but does not push quantized payloads through a joint-typicality decoder
  end-to-end. This is a *granularity* gap, not a gap in the bound.
- **The distributed dispersion $V_{\mathrm{dist}}$.** D1-E7 validates the *centralized-cut* variance; the full
  distributed second-order term is open.
- **Correlated observations at full sharpness.** The converse survives (tested in spirit), but the exact value of
  $E^{\mathrm{cen}}$ under correlation and the single-letter evaluability of $\theta_{\mathrm{IB}}$ are not
  fully characterized.

## 10.4 What the adversarial validation phase discovered and fixed (from `VALIDATION_AUDIT.md`)

The project underwent a deliberate "Reviewer #2" phase whose only goal was to find weaknesses. The critical
finds and fixes:
- **G1 — circularity (critical).** The original topology/scaling experiments *discarded the graph* after
  computing the scalar $\Gamma_k$ and re-evaluated the *same* formula — so a "0.0000 collapse" was almost
  tautological. **Fixed** by D1-N1: route real information via max-flow; naive and SR now differ on the same
  graph (spread 0.19 vs 0.00), making the collapse a genuine result.
- **G2 — scale.** Only $N \le 16$ tested. **Fixed** by D1-N2 (to $N=1000$).
- **G3 — Gaussian-only.** **Fixed** by D1-N3 (discrete $K=8$ converse).
- **G4 — no edge cases.** **Fixed** by D1-N4 (failures, near-disconnection, bridge).
- **G9 — achievability modeled, not coded.** **Fixed** by D1-N5 (actual $\mathrm{GF}(q)$ RLNC; coding beats
  routing on the butterfly), upgrading D1★★ confidence from HIGH to VERY HIGH.

## 10.5 Confidence levels (the audit's honest grading)

| Claim | Confidence | Basis |
|---|---|---|
| D1★ converse | **Very high** | respected by all schemes/topologies/scales/alphabets |
| D1★★ achievability (cut attainable) | **Very high** | actual GF(q) code attains the cut; coding>routing |
| D1 centralized dispersion | **High** | $V$ recovered to 0.2% |
| General-pair, distributed dispersion, symbol-level pipeline | **Open (future work)** | honestly documented, not claimed |

## 10.6 Reproducibility

All results are regenerated deterministically from logged seeds; a fresh-seed certification (seed 20260727)
re-confirms every headline number (converse respected, coding beats routing, exponent $=\theta_{\mathrm{IB}}$).
The saddlepoint is deterministic (no seed dependence); the RLNC recovery rates are stable across fresh seeds
(butterfly $\approx 0.98$).

---

# SECTION 11 — FIGURES (what each shows, how to read it, expected vs observed, the conclusion)

The figures live in `results/d1/figures/` as PNG + PDF + SVG. For each: what it plots, how to read the axes, the
*expected* pattern from theory, the *observed* pattern, and the scientific conclusion.

## 11.1 `D1-E1_rate_sweep`
- **Axes.** $x$: cut budget $\Gamma_k$ (nats/use). $y$: error exponent $E_k$ (nats).
- **What is drawn.** Blue curve: the analytic $\theta_{\mathrm{IB}}(\Gamma)$. Orange dashed horizontal line: the
  ceiling $E^{\mathrm{cen}}=2$. Black points with error bars: the *measured* exponents (saddlepoint,
  dispersion-corrected, 95% CIs). A green dotted vertical line: the knee $C_{\mathrm{DIB}}$.
- **Expected pattern.** Black points on the blue curve, always below the orange line, bending toward the ceiling.
- **Observed.** Exactly that; MAE $0.0011$, max exceedance $-0.0011$.
- **Conclusion.** D1★ and D1★★ in one figure: the exponent *is* $\theta_{\mathrm{IB}}(\Gamma_k)$ and *never*
  beats the ceiling.

## 11.2 `D1-E2_converse_schemes`
- **Axes.** $x$: $I(U;X)$ (rate spent, nats). $y$: $I(U;Y)$ (relevance kept = exponent, nats).
- **What is drawn.** Blue curve: the IB envelope $\theta_{\mathrm{IB}}(R)$. Orange squares: uniform quantizers.
  Green triangles: Lloyd–Max quantizers (labeled by level count $L$).
- **Expected.** All markers on or *below* the blue envelope.
- **Observed.** All below (max violation $-3.3\times10^{-3}$); Lloyd–Max closer than uniform; neither touches.
- **Conclusion.** $\theta_{\mathrm{IB}}$ is a *true upper bound* over schemes (converse), attained only by the
  soft IB channel (achievability).

## 11.3 `D1-E3_topology_suff`
- **Axes.** $x$: the ten topology names (categorical). $y$: measured exponent $E_k$.
- **What is drawn.** Points (with CIs) for each topology at matched $\Gamma_k=3$; a dashed line at
  $\theta_{\mathrm{IB}}(3)$.
- **Expected.** All ten points on the dashed line (collapse).
- **Observed.** Spread $0.0000$ nats — a flat line of points.
- **Conclusion.** $\Gamma_k$ is a sufficient statistic; topology is irrelevant beyond the cut.

## 11.4 `D1-E4_waterfilling`
- **Axes.** $x$: total budget $\Gamma$. $y$: exponent (nats).
- **What is drawn.** Blue: water-filling $\theta_{\mathrm{IB}}$. Orange dashed: equal-split. Black points:
  measured (under water-filling). Dotted: the ceiling $E^{\mathrm{cen}}=2.2854$.
- **Expected.** Blue above orange; black on blue.
- **Observed.** Gap up to $0.3045$ nats; black matches blue (MAE $0.0010$); slope change where the weak agent is
  cut off.
- **Conclusion.** Water-filling is optimal and achievable; equal split leaves exponent on the table.

## 11.5 `D1-E5_scaling`
- **Axes.** Two panels. Both $x$: number of agents $N$. $y$: exponent.
- **What is drawn.** (a) fixed per-agent $R=0.5$: $E^{\mathrm{cen}}$ and $N\theta_{\mathrm{IB},i}$ curves plus
  measured points (linear rise). (b) fixed total $\Gamma=2$: $\theta_{\mathrm{IB}}(\Gamma)$ plus measured points
  (bending over).
- **Expected/Observed.** (a) linear growth (MAE 0.0011). (b) saturation/bend (MAE 0.0012).
- **Conclusion.** More evidence helps linearly; a shared cut throttles — two distinct scaling laws.

## 11.6 `D1-E6_dynamic_topology`
- **Axes.** (a) $x$: round $t$; $y$: per-round min-cut. (b) categorical predictors vs exponent.
- **What is drawn.** (a) the fluctuating per-round min-cut (steps) with the ergodic mean as a horizontal line.
  (b) bars for "use min cut / use ergodic mean / use max cut" predictions vs the measured exponent (dashed).
- **Expected/Observed.** Only the ergodic-mean bar matches the measured dashed line; min ($0.592$) and max
  ($2.157$) miss; measured $1.488$ vs $\theta_{\mathrm{IB}}(\bar\Gamma_k)=1.489$.
- **Conclusion.** The time-average binds.

## 11.7 `D1-E7_dispersion`
- **Axes.** (a) $x$: samples $n$; $y$: $-\ln\beta_n$ for five $\varepsilon$ levels, with the first-order line
  $n\theta_{\mathrm{IB}}$. (b) $x$: $\Phi^{-1}(\varepsilon)$; $y$: the fitted $\sqrt n$ coefficient.
- **Expected.** (a) curves below the straight line by a $\sqrt n$ amount. (b) points on a line of slope
  $\sqrt V$.
- **Observed.** $V$ recovered to $0.2\%$; coefficient MAE $0.0013$.
- **Conclusion.** The Strassen dispersion term is real and correctly sized.

## 11.8 `D1-N1_genuine_network`
- **Axes.** exponent per topology, two series: SR (blue) and naive (red), at matched $\Gamma_k=2.5$, plus the
  $\theta_{\mathrm{IB}}$ line.
- **Expected.** SR flat on the line; naive scattered below.
- **Observed.** SR spread $0.0000$; naive spread $0.1931$; nothing above the line (max over-shoot $-0.0008$).
- **Conclusion.** The collapse is genuine (not circular); coding needed; converse holds under real routing.

## 11.9 `D1-N2_large_scale`
- **Axes.** $x$: $N$ (up to 1000, likely log scale); $y$: exponent or delivered rate; series for SR and naive.
- **Expected/Observed.** SR tracks $\theta_{\mathrm{IB}}(\Gamma_k)$ at all scales; naive below; sub-second
  compute to $N=1000$.
- **Conclusion.** Scale-independence.

## 11.10 `D1-N3_nongaussian_discrete`
- **Axes.** $x$: $I(U;X)$; $y$: $I(U;Y)$; the discrete IB envelope with five merge-quantizer points.
- **Expected/Observed.** All points on/below the envelope (max violation $3.4\times10^{-6}$).
- **Conclusion.** The converse is not Gaussian-specific.

## 11.11 `D1-N4_edge_cases`
- **Axes.** $x$: failure probability $f$; $y$: $\Gamma_k$ and $E_k$ (and a marker for the bridge case).
- **Expected/Observed.** Both fall smoothly to 0 as $f\to 1$; bridge $\Gamma_k=1.00$.
- **Conclusion.** Graceful degradation; no boundary pathologies.

## 11.12 `D1-N5_rlnc_achievability`
- **Axes.** Three panels. (a) $x$: number of source symbols $h$; $y$: recovery probability, with a vertical line
  at $F$. (b) $x$: field size $q$ (log); $y$: recovery probability at $h=F$, with the Ho bound. (c) bar chart:
  coding rate to each butterfly sink vs routing.
- **Expected.** (a) step down at $h=F$. (b) rise to 1 with $q$. (c) coding bars at 2, routing at 1.
- **Observed.** (a) `[1,1,1,0.99,0,0]`. (b) $0.037 \to 0.998$. (c) coding 2/2, routing 1.
- **Conclusion.** A real code attains the cut, reliably with field size, and beats routing on multicast.

---

# SECTION 12 — REVIEWER QUESTIONS (an extensive, hostile FAQ with full answers)

**Q1. Is the main theorem circular — did you assume the answer to prove it?**
No. The converse comes from *two independent* inequalities that never mention the answer: (i) the cut-set
entropy bound (Lemma A: information about $\theta$ reaching $k$ $\le \Gamma_k$, from $I\le H$ + subadditivity +
the budget), and (ii) the rate-limited Stein bound (Lemma B: exponent from $\Gamma_k$ nats $\le
\theta_{\mathrm{IB}}(\Gamma_k)$, from Ahlswede–Csiszár), plus the full-data DPI ($\le E^{\mathrm{cen}}$). None of
these presupposes the min form; it *emerges*. Empirically, experiment D1-N1 proves the sufficiency is not
circular by showing that with *real routing* the exponent genuinely *does* depend on the scheme (naive spreads
0.19 nats) — so the SR collapse to 0.0000 is a substantive result.

**Q2. You only solve "testing against independence." Isn't that a toy?**
It is the canonical, operationally central case (Ahlswede–Csiszár's own setting) and the *only* regime where the
distributed rate-limited exponent is known *exactly* in the literature. We are explicit that the general pair is
converse-only ($\theta_{\mathrm{SHA}}$) and its exact distributed exponent is *open* — we do not overclaim. Being
exact on a meaningful case beats being vague on all cases.

**Q3. Does interaction (multi-round chatter) break the converse?**
No. Interaction can *use* the rate more cleverly (raising achievable exponents toward the bound) but cannot push
more than the cut's entropy budget across a cut over $T$ rounds — that is an accounting identity on transmitted
entropy, immune to protocol design (Lemma A, step 4).

**Q4. What if observations are correlated across agents (H-CI fails)?**
The converse *survives* as an upper bound: replace $E^{\mathrm{cen}}=\sum_i D_i$ by the true joint divergence
(which is generally smaller under positive correlation — shared info is redundant), and the cut/IB term is
unchanged because Lemmas A–B use only data-processing and the cut capacity, never the product structure. What is
*lost* is the clean single-letter evaluability of $\theta_{\mathrm{IB}}$ (CEO/Wyner–Ziv machinery enters). We
state this, not hide it (bible §1.3.1-CI).

**Q5. Your exponents are $e^{-2n}$ — impossible to measure. How are your numbers real?**
We do *not* measure them by naive Monte Carlo (which is indeed impossible). We compute the *exact* finite-$n$
error of the optimal Neyman–Pearson detector via a Lugannani–Rice saddlepoint on the LLR's closed-form CGF, in
log-space (no underflow), and extract the exponent with the theoretically-predicted dispersion correction. We
*cross-check* against real Monte Carlo in the measurable regime ($\beta_n \sim 10^{-2}$), where they agree to
$\sim 2\%$ (D1-E1). The saddlepoint is exact, not a simulation.

**Q6. The topology-collapse (E3) reuses $\Gamma_k$ — that's circular.**
Correct criticism of E3 *alone*, which is why D1-N1 exists: it routes real information so the delivered rate
*emerges* and *differs by scheme* (naive spreads 0.19 nats, SR collapses to 0.0000). The genuine collapse under
real routing is the non-circular proof of sufficiency.

**Q7. Why network coding? Isn't routing enough?**
Because D1 is *fusion-free*: every agent decides for itself and needs everyone's summary — a *multicast*. For
multicast, routing provably cannot deliver every sink's min-cut simultaneously (butterfly: routing gives 1,
coding gives 2). D1-N5 shows an actual $\mathrm{GF}(q)$ code achieving 2 to both butterfly sinks while routing
achieves 1. Also, naive Gaussian quantize-and-forward is *sub-additive in nats* (D1-N1: loses up to 60% on
multi-path graphs). So coding is *necessary*, not a stylistic choice.

**Q8. Does it scale? $N=4$ is tiny.**
D1-N2 runs to $N=1000$ (ER/BA/WS) in sub-second per graph; the SR exponent tracks $\theta_{\mathrm{IB}}(\Gamma_k)$
at every scale. The theory has no hidden $N$-dependence beyond $\Gamma_k$.

**Q9. Is the field-size / RLNC reliability just asymptotic hand-waving?**
No — D1-N5 shows the *actual* recovery probability rising $0.037 \to 0.998$ as $q: 2 \to 1031$, above the
$(1-h/q)^{|E|}$ Ho lower bound throughout, and the sharp recover-iff-$h\le F$ threshold. Small fields genuinely
fail, confirming the field-size schedule of Lemma C-D1 is required, not decorative.

**Q10. Why is the answer a *min* and not something more complex (a sum, a product)?**
Because two *independent* ceilings apply: statistics ($E^{\mathrm{cen}}$, from the full-data DPI) and bandwidth
($\theta_{\mathrm{IB}}(\Gamma_k)$, from the cut-set + Stein). You are bounded by *each*, hence by the *smaller*.
There is no interaction term because the two bounds come from disjoint mechanisms (Section 8.1).

**Q11. What is $\theta_{\mathrm{IB}}$, physically? Isn't IB just a machine-learning heuristic?**
Tishby introduced IB as an ML objective, but Ahlswede–Csiszár (1986) — *predating* IB — proved that this exact
functional *is* the error exponent for rate-limited testing against independence. So $\theta_{\mathrm{IB}}$ has a
hard operational meaning here: the best exponent achievable from a rate-$R$ summary. It is not a heuristic; it is
a theorem.

**Q12. The Gaussian model's "kink" at $C_{\mathrm{DIB}}$ is soft, not sharp. Is the claim wrong?**
The *saturation* is real and finite; for Gaussian relevance the approach to the ceiling is asymptotic, so the
knee is soft (we define $C_{\mathrm{DIB}}$ at a 2% level, giving $8.887$ for the standing case). A *hard* kink
requires bounded/discrete relevance; that is a modeling choice, not a flaw in the theorem, which is stated for
general $\Theta$.

**Q13. Could a smarter, non-IB compressor beat $\theta_{\mathrm{IB}}$?**
No — that is exactly what the converse (Lemma B via Ahlswede–Csiszár, tight by Rahman–Wagner) forbids, and D1-E2
confirms empirically: uniform and Lloyd–Max quantizers all lie *below* the envelope; only the IB-optimal soft
channel reaches it.

**Q14. Is $\Gamma_k$ well-defined if the graph is non-ergodic?**
Under [H-Top] (stationary ergodic) it is a single a.s. constant. Without ergodicity it may not converge; you
sandwich with $\liminf/\limsup$ and the converse holds with the looser $\Gamma_k^{\sup}$ (bible §1.10). We assume
ergodicity and say so.

**Q15. What have you *not* done that a follow-up should?**
A full symbol-level RLNC pipeline (payloads through a joint-typicality decoder), the distributed dispersion
$V_{\mathrm{dist}}$, and the general-pair distributed exponent. All are explicitly logged as future work in
`VALIDATION_AUDIT.md`.

---

# SECTION 13 — ORAL DEFENSE GUIDE (how to answer live)

**Golden rule.** Always answer in three beats: *(1) the one-sentence intuition, (2) the mechanism/where it comes
from, (3) the evidence.* Never lead with formulas.

**"Explain the main result to me in one breath."**
"The best decision-error exponent any agent can achieve equals the smaller of two things — the exponent it could
get with unlimited communication, and the exponent permitted by the information that can physically flow to it
across the network's tightest bottleneck. We proved a matching lower and upper bound, so it's exact."

**"Explain $\theta_{\mathrm{IB}}(\Gamma_k)$."**
"(1) It's the best exponent you can get from a summary of size $\Gamma_k$ nats. (2) It comes from Ahlswede–
Csiszár 1986: for testing against independence, the exponent from a rate-$R$ description is exactly the
information-bottleneck curve — the most $Y$-relevant information you can keep while spending $R$ nats describing
$X$. (3) The Gaussian closed form $-\tfrac12\ln(1-\rho^2(1-e^{-2R}))$ is validated to $0.001$ nats in D1-E1."

**"Why Information Bottleneck (and not something else)?"**
"Because the problem *is* an IB problem: you must compress each observation to fit the cut, and keep as much as
possible about the thing you're testing. Ahlswede–Csiszár proved the resulting exponent is *exactly* the IB
functional for against-independence, and Rahman–Wagner proved it's tight. It's not a design choice — it's the
answer."

**"Why RLNC (and not routing)?"**
"Fusion-free means everyone is a sink and needs everyone's summary — that's multicast. In multicast, routing
can't hit every sink's min-cut at once; coding can. The butterfly proves it: routing 1, coding 2. Our D1-N5
simulates a real $\mathrm{GF}(q)$ code doing exactly that. Plus, naive forwarding is sub-additive in nats, so it
literally loses rate on multi-path graphs."

**"Explain the cut-set bound (Lemma A) at the board."**
"Draw the time-expanded graph — copies of nodes at each time, edges going forward, infinite-capacity self-loops
for memory. Now it's acyclic. Take any cut separating sources from $k$. Everything about $\theta$ that reaches
$k$ rides on the cut's edges. Information $\le$ entropy $\le$ sum of edge entropies (subadditivity) $\le$ sum of
budgets. Take the tightest cut, sum over rounds, divide by $T$, use ergodicity: rate $\le \Gamma_k$. Three
inequalities: $I\le H$, subadditivity, the budget. That's it."

**"Why is the answer a *min*?"**
"Two independent walls: statistics and bandwidth. The full-data detector caps you at $E^{\mathrm{cen}}$; the cut
caps you at $\theta_{\mathrm{IB}}(\Gamma_k)$. You're behind both walls, so you're behind the nearer one."

**"How do you measure an $e^{-2n}$ error?"**
"We don't simulate it — that's impossible. The optimal detector's error is a tail probability of a sum of
quadratic forms, whose CGF is closed-form; we evaluate it exactly with a log-space saddlepoint, then read the
exponent off with the predicted dispersion correction. We cross-check against real Monte Carlo where the error
is big enough to see — they agree to 2%."

**"What's the single most convincing experiment?"**
"D1-N1. At the *same* bottleneck, network coding collapses ten different graphs to one exponent (spread
0.0000), while naive forwarding *spreads* by 0.19 nats — so the collapse is a real fact about achieving the cut,
not a tautology, and nothing ever beats the cut. Converse, achievability, sufficiency, and coding-necessity in
one figure."

**"What would falsify your theorem?"**
"Any scheme, on any graph, whose measured exponent exceeds $\min\{E^{\mathrm{cen}},\theta_{\mathrm{IB}}(\Gamma_k)\}$
by more than the confidence interval. We searched hard (10 topologies, $N$ to 1000, Gaussian and discrete, edge
failures) — every exceedance is $\le 0$."

---

# SECTION 14 — COMMON MISUNDERSTANDINGS (and why they are wrong)

1. **"$N$ (agents) and $n$ (samples) are the same thing."** No. $N$ is how many sensors; $n$ is how much data
   each collects over time. The exponent is a decay rate *in $n$*; $N$ enters through $E^{\mathrm{cen}}=\sum_i
   D_i$ and through $\Gamma_k$.
2. **"$\theta_{\mathrm{IB}}$ is a hypothesis because it has $\theta$ in its name."** No. It is an *exponent* (a
   function of rate). The $\theta$ is historical notation for "the exponent"; it is unrelated to the hypothesis
   $\theta$.
3. **"Denser/better-connected graphs give better exponents."** Only insofar as they raise $\Gamma_k$. At *matched*
   $\Gamma_k$, all graphs give the *same* exponent (D1-E3/N1). The cut is everything.
4. **"More agents always help."** Only if you also add bandwidth. With a *fixed shared cut*, adding agents does
   not raise the exponent (D1-E5b) — the cut throttles.
5. **"The converse means our specific scheme is optimal."** The converse bounds *all* schemes. Optimality of a
   *specific* scheme is the *achievability* (D1★★). They are separate; D1-E2 shows the difference (the envelope
   bounds all quantizers; only the soft IB channel is tight).
6. **"Naive quantize-and-forward achieves the cut."** No — Gaussian MMSE fusion is *sub-additive in nats*, so on
   multi-path graphs it delivers strictly less than the cut (D1-N1: 0.19-nat shortfall). Coding is needed.
7. **"The time-varying answer uses the average graph's min-cut."** No — it uses the *average of the per-round
   min-cuts*, which differs when the binding cut moves round to round (Lemma A step 3). D1-E6 shows the ergodic
   average of cuts, not the cut of the average, is correct.
8. **"KL divergence is a distance."** It is not symmetric and violates the triangle inequality. It behaves like a
   *squared* distance only for nearby distributions.
9. **"The exponent depends on the false-alarm level $\varepsilon$."** By Stein's lemma it does *not* (for any
   fixed $\varepsilon\in(0,1)$). D1-E7 exploits this — only the *finite-$n$* dispersion term depends on
   $\varepsilon$, and it does so through $\Phi^{-1}(\varepsilon)$.
10. **"We solved the general multi-agent detection problem."** We solved *testing against independence* exactly.
    The general pair is converse-only and its distributed exponent is open. Precision here is a matter of
    integrity.

---

# SECTION 15 — MENTAL MODEL (the whole paper at five zoom levels)

## 15.1 The 5-minute explanation
Many weak sensors, thin radios, no boss, wiring changes constantly, and each sensor must decide the same
yes/no question. The best any sensor can do — measured as how fast its error shrinks with data — is the *smaller*
of (what it could do with infinite bandwidth) and (what the information squeezing through its tightest network
bottleneck allows). We proved this is *exactly* the answer (matching upper and lower bounds) for the standard
"is there any signal?" test, even when the network loops and changes every instant. The one number that captures
the whole network is the time-averaged min-cut $\Gamma_k$.

## 15.2 The 15-minute explanation
Add the mechanism. Detection quality is an *error exponent* (Stein: exponent = KL divergence). With unlimited
comms the exponent is $E^{\mathrm{cen}}=\sum_i D_i$ (evidence adds up under conditional independence). With a
bottleneck of $\Gamma_k$ nats, the exponent is capped by the *information-bottleneck* curve
$\theta_{\mathrm{IB}}(\Gamma_k)$ (Ahlswede–Csiszár: the exponent from a rate-$R$ summary is exactly the IB
functional). Two independent caps $\Rightarrow$ the exponent is their *min*. The network enters only through
$\Gamma_k$, the *time-averaged min-cut* — a sufficient statistic. Converse (nothing beats it) from a cut-set
entropy bound + Stein-through-a-bottleneck; achievability (something reaches it) from compress-to-IB +
random-linear-network-coding-across-the-time-expanded-graph + joint-typicality-test.

## 15.3 The 30-minute explanation
Add the proofs' skeletons (Section 8): Lemma A (time-expand $\to$ acyclic; $I\le H\le$ subadditive $\le$ budget
$\Rightarrow$ rate $\le \Gamma_k$); Lemma B (Ahlswede–Csiszár $\Rightarrow$ exponent $\le \theta_{\mathrm{IB}}
(\Gamma_k)$); full-data DPI $\Rightarrow \le E^{\mathrm{cen}}$; min. Achievability's three lemmas (encode/bin over
$\mathrm{GF}(q)$; decode independent codebooks with no rate loss via information spectrum; aggregate ergodic cuts
with growing field size). Then the Gaussian closed forms ($I=-\tfrac12\ln(1-\rho^2)$;
$\theta_{\mathrm{IB}}(R)=-\tfrac12\ln(1-\rho^2(1-e^{-2R}))$; water-filling), and why network coding is *necessary*
(fusion-free = multicast; butterfly).

## 15.4 The 1-hour lecture
All of the above plus: the literature evolution (Stein $\to$ Ahlswede–Csiszár $\to$ Han/SHA $\to$ Aguerri–Zaidi
$\to$ Nedić et al. $\to$ the D1 intersection); the measurement methodology (saddlepoint, why naive MC fails,
dispersion correction, MC cross-check); the seven core experiments (E1 rate sweep, E2 converse envelope, E3/N1
sufficiency, E4 water-filling, E5 scaling, E6 ergodic cut, E7 dispersion); and the adversarial validation
(circularity found and fixed; scale, discrete, edge cases, actual GF(q) code).

## 15.5 The 3-hour lecture
Everything, taught from Section 2's prerequisites up: probability/KL/MI/Stein; graphs/cuts/max-flow/
time-expansion; IB; network coding/RLNC/finite fields; then the full formulation with every assumption's role;
the complete proofs of Lemmas A, B, A-D1, B-D1, C-D1 with every inequality justified (Section 8); the Gaussian
derivations; all twelve experiments with their exact numbers; the figure walk-through; and the full reviewer FAQ
and defense guide. End with the honest scope (against-independence exact; general pair open) and the open
problems.

---

# SECTION 16 — LEARNING PATH (the exact order to study, with a dependency graph)

## 16.1 Dependency graph (textual)
```
Probability / Gaussians (2.1)
        ↓
Entropy (2.3) ──────────────┐
        ↓                   │
KL divergence (2.4)         │ (I ≤ H, subadditivity)
        ↓                   │
Mutual information (2.5) ────┤
        ↓                   ↓
Hypothesis testing +     Graphs / cuts / max-flow (2.9)
Stein's lemma (2.7)          ↓
        ↓               Time-expanded graphs (2.10)
Error exponents +           ↓
dispersion (2.8)        Ergodicity / time-average (2.13)
        ↓                   ↓
Data-processing ineq. (2.6) │
        ↓                   │
Information Bottleneck (2.11) ← (needs KL, MI)
        ↓                   │
Network coding / RLNC / GF(q) (2.12)
        ↓                   ↓
   ┌────────────────────────┘
   ↓
Problem formulation (Section 4)
   ↓
Theorem D1★ converse (7.1) ← proof: Lemma A (8.1.1) + Lemma B (8.1.2)
   ↓
Theorem D1★★ achievability (7.2) ← proof: Lemmas A-D1/B-D1/C-D1 (8.2)
   ↓
Gaussian closed forms (8.3) → Experiments E1–E7 (9.1–9.7)
   ↓
Genuine-network + RLNC experiments N1–N5 (9.8–9.12)
   ↓
Validation + audit (Section 10)
```

## 16.2 Recommended study order (with "why this before that")
1. **2.1–2.5 (probability $\to$ mutual information).** Everything is bookkeeping in these quantities. Do not
   proceed until $I(X;Y)=-\tfrac12\ln(1-\rho^2)$ feels obvious.
2. **2.6–2.8 (DPI, Stein, exponents/dispersion).** These turn "information" into "detection." Stein is the hinge:
   exponent = KL divergence.
3. **2.9–2.10, 2.13 (graphs, cuts, max-flow, time-expansion, ergodicity).** The network side. The one trick to
   internalize: *time-expansion makes a cyclic changing graph acyclic.*
4. **2.11 (Information Bottleneck).** The bridge. Understand its shape (concave, increasing, saturating) and the
   Gaussian closed form.
5. **2.12 (network coding / RLNC / finite fields).** Needed only for achievability and D1-N5, but essential to
   understand *why coding, not routing*.
6. **Section 4 (formulation).** Now the problem statement will read like plain English.
7. **Section 7 then 8 (theorems, then proofs).** Read the statement and intuition first (7), then the step-by-step
   proof (8). Do Lemma A by hand at a board.
8. **Section 8.3 + Section 9 (Gaussian forms + experiments).** See the abstract theorem become concrete numbers;
   understand the saddlepoint measurement (9.0) before any specific experiment.
9. **Section 10 + 12–14 (validation, FAQ, misunderstandings).** Cement understanding by defending it.
10. **Section 15 (mental model).** Re-tell the whole story at increasing depth until the 5-minute version is
    effortless.

## 16.3 Milestones (you understand D1 when you can…)
- derive $\theta_{\mathrm{IB}}(R)=-\tfrac12\ln(1-\rho^2(1-e^{-2R}))$ from the IB definition and the Gaussian
  channel, unaided;
- prove Lemma A at a whiteboard using only $I\le H$, subadditivity, and the budget;
- explain *why* the answer is a min (two independent walls);
- explain *why* coding beats routing here (fusion-free = multicast; butterfly);
- explain *why* naive Monte Carlo cannot measure the exponents and what replaces it;
- state precisely what is proven (against independence, exact) and what is open (general pair, distributed
  dispersion, symbol-level pipeline).

---

*End of MASTER_D1_HANDBOOK.md. Everything above is grounded in `D1_Research_Bible_v3.md`, `code/theory.py`,
`code/d1_detect.py`, `code/topology.py`, `code/d1_network.py`, `code/d1_rlnc.py`, `resultsD1.md`, and
`VALIDATION_AUDIT.md`. Where a quantity was stated it was cross-checked against those files; numbers such as
$E^{\mathrm{cen}}=2$, MAE $=0.0011$, spread $=0.0000$, naive spread $=0.1931$, $V=1.5983$ vs $1.6008$, butterfly
coding 2 vs routing 1, and recovery `[1,1,1,0.99,0,0]` are quoted directly from `resultsD1.md`.*
