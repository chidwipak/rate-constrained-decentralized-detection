# D1 Literature Freeze — Rate-Constrained Decentralized Detection

Target venue: IEEE Transactions on Information Theory. Goal: an exhaustive prior-art survey so that no
reviewer can reasonably claim an important omission. For each work we record what it solved, the assumptions it
made, its limitations, and how the present paper differs. Every entry corresponds to a real, verifiable
publication in `refs.bib`. All information quantities are in nats.

The problem characterized in this paper is the exact Type-II error exponent achievable at an arbitrary node of
a fusion-free, rate-limited, time-varying directed network performing a distributed test against independence.
The result is the closed pair E_k = min{E_cen, theta_IB(Gamma_k)}: a converse (Theorem D1-star) and a matching
Type-Preserving Network Coding achievability (Theorem D1-star-star). The literature is organized into seven
strands that jointly bound this contribution.

## Strand 1 — Classical hypothesis testing and error exponents
- Chernoff 1952; Stein's lemma (Cover-Thomas Ch. 11). Solved: the centralized binary test; best Type-II
  exponent at fixed Type-I equals D(P0||P1), independent of the Type-I level. Assumptions: full centralized
  samples, no communication limit. Limitation: no network, no rate constraint. Difference: recovered here as the
  N=1, Gamma to infinity limit and as the E_cen ceiling.
- Blahut 1974; Han-Kobayashi 1989 (strong converse for HT). Solved: exponent trade-off and the strong converse
  making the exponent independent of the Type-I level. Use here: justifies the epsilon-independence of E_cen and
  of theta_IB used throughout.
- Csiszar-Korner (book) method of types; Csiszar 1998 (method of types survey). Provides the large-deviation
  machinery behind the achievability typicality arguments.

## Strand 2 — Hypothesis testing with communication (rate) constraints
- Ahlswede-Csiszar 1986. Solved: the exact rate-R one-sided-compression exponent for testing against
  independence, theta_IB(R) = max_{I(U;X)<=R} I(U;Y); an achievable bound for the general pair. Assumptions:
  single observer to single detector, static, asymptotic. Limitation: no network, no time variation, no
  fusion-free consensus. Difference: this paper lifts the same functional to the binding cut Gamma_k of a
  time-varying directed graph.
- Han 1987. Solved: multiterminal one-sided and two-sided compression; general achievable exponents and special
  converses. Difference: orthogonal axis (more sources), reused here as a rate-limited converse ingredient.
- Shimokawa-Han-Amari 1994. Solved: the SHA exponent with binning, theta_SHA(R), reducing to theta_IB for
  testing against independence. Use here: the general-pair converse functional referenced in the scope
  discussion.
- Han-Amari 1998 (statistical inference under multiterminal data compression, survey). Frames the whole
  multiterminal inference program; positions the against-independence case as the solved sub-case.
- Shalaby-Papamarcou 1992 (zero-rate compression). Solved: the exponent under vanishing rate. Boundary check:
  consistent with theta_IB(0)=0 here.
- Rahman-Wagner 2012. Solved: optimality of binning for a class of distributed tests, proving SHA tightness for
  testing against independence. Use here: certifies that theta_IB is exactly the tight functional in the target,
  so the converse and the achievability meet with no gap.
- Katz-Piantanida-Debbah 2017 (distributed binary detection with lossy compression); Salehkalaibar-Wigger-Timo
  2018 (against conditional independence, multiple decision centers); Zhao-Lai 2018 (multiple terminals);
  Sreekumar-Gunduz 2020 (over noisy channels); Xiang-Kim 2013 (interactive testing against independence).
  Solved: successive refinements, multiple decision centers, noisy links, interaction. Limitation: none treats
  time-varying topology plus fusion-free plus per-edge rate simultaneously. Difference: this paper is exactly the
  intersection they leave open; interaction is admitted by the converse (Lemma A) without loosening it.
- Tian-Chen 2008 (successive refinement for HT). Solved: layered descriptions for testing. Related to the
  successive-refinement scheme used as the operational achievability baseline in D1-N1.

## Strand 3 — The information bottleneck
- Tishby-Pereira-Bialek 1999. Solved: the IB principle and its Lagrangian/self-consistent equations. Use here:
  defines theta_IB.
- Gilad-Bachrach-Navot-Tishby 2003. Solved: concavity and monotonicity of the relevance-rate curve. Use here:
  the strictness proposition (below saturation the exponent is strictly less than E_cen).
- Chechik-Globerson-Tishby-Weiss 2005 (Gaussian IB). Solved: closed-form Gaussian IB, giving
  theta_IB,i(R) = -1/2 ln(1 - rho^2 (1 - e^{-2R})). Use here: the exact Gaussian instantiation and the
  water-filling allocation.
- Aguerri-Zaidi 2019 (distributed IB). Solved: the exact single-letter rate-relevance region for a star of
  encoders to one decoder. Assumptions: static topology, a decoder node exists, asymptotic. Difference: this
  paper removes the decoder (fusion-free) and the static assumption; the static-star specialization recovers
  their converse ceiling.
- Estella Aguerri-Zaidi (one-shot/finite-sample IB). Solved: one-shot IB bounds by convex duality. Limitation:
  single decoder, static; does not close the distributed dispersion question raised here.
- Goldfeld-Polyanskiy 2020 and Zaidi-Aguerri-Shamai 2020 (IB surveys). Context: connect IB to representation
  learning and to distributed source coding, situating theta_IB operationally.

## Strand 4 — Distributed inference and social learning over networks
- Nedic-Olshevsky-Uribe 2017. Solved: geometric belief concentration over time-varying graphs at the
  network-averaged KL rate. Assumptions: essentially rate-unconstrained belief exchange, doubly or column
  stochastic mixing, B-strong connectivity. Difference: this paper adds the per-edge Shannon-rate throttle they
  omit; their rate is the Gamma to infinity ceiling here.
- Lalitha-Javidi-Sarwate 2018; Shahrampour-Rakhlin-Jadbabaie 2016; Jadbabaie-Molavi-Sandroni-Tahbaz-Salehi 2012;
  Molavi-Tahbaz-Salehi-Jadbabaie 2018 (non-Bayesian social learning). Solved: almost-sure exponential belief
  concentration with network-weighted KL rates. Limitation: full-belief or finitely parameterized exchange, not
  Shannon-rate limited. Difference: same missing rate axis.
- Kar-Moura-Ramanan 2012 (consensus plus innovations detection); Bajovic-Jakovetic-Xavier-Sinopoli-Moura 2011
  (Gaussian running-consensus detection); Braca-Marano-Matta-Willett 2010 (asymptotic optimality of running
  consensus). Solved: distributed detectors with explicit large-deviation rates. Limitation: no per-edge Shannon
  budget. Difference: the running-consensus detector is the practical instrument that this paper's cut bound
  upper-bounds.
- Tsitsiklis 1988 and Tsitsiklis 1993 (decentralized detection); Tenney-Sandell 1981; Viswanathan-Varshney 1997
  (survey); Chamberland-Veeravalli 2003, 2004. Solved: the foundational decentralized detection framework with
  local quantizers and a fusion center, including person-by-person optimality of likelihood-ratio quantizers and
  the value of having more sensors under a power or rate budget. Difference: those results assume a fusion center
  and a fixed architecture; this paper is fusion-free with a time-varying cut.
- Olfati-Saber-Fax-Murray 2007; Nedic-Ozdaglar 2009; Tsitsiklis-Bertsekas-Athans 1986. Context: consensus and
  distributed optimization over graphs, providing the mixing-dynamics background.

## Strand 5 — Network information theory and cut-set bounds
- Cover-Thomas (book), cut-set outer bound; Cover-El Gamal 1979 (relay channel); El Gamal-Kim 2011 (Network
  Information Theory). Solved: the general cut-set outer bound and the deterministic-network specialization used
  in Lemma A. Difference: applied here per-round on the time-expanded DAG so the bound is a sum of per-round
  binding cuts, which is tighter than the time-averaged-graph cut when the binding cut moves.
- Ahlswede-Cai-Li-Yeung 2000 (network coding); Li-Yeung-Cai 2003 (linear network coding); Koetter-Medard 2003
  (algebraic network coding); Ho-Koetter-Medard-Karger-Effros-Shi-Leong 2006 (random linear network coding);
  Jaggi-Sanders-Chou-Effros-Egner-Jain-Tolhuizen 2005 (polynomial-time codes). Solved: multicast capacity equals
  the min-cut and random GF(q) linear codes attain it with probability at least (1 - h/q)^{|E|}. Use here: the
  backbone of the Type-Preserving Network Coding achievability, including the butterfly coding-beats-routing
  separation validated in the experiments.
- Slepian-Wolf 1973; Wyner-Ziv 1976; Berger 1977 and Tung 1978 (Berger-Tung). Solved: distributed source coding
  and binning with side information. Use here: the quantize-and-bin front end of the achievability.
- Schwartz 1980; Zippel 1979 (Schwartz-Zippel lemma). Use here: full-rank of the random network transfer matrix.
- Kang-Ulukus 2011 (a data-processing inequality for distributed coding). Context: interaction and the limits of
  processing gains, consistent with the interactive tightness note in Lemma A.

## Strand 6 — Finite-blocklength and second-order analysis
- Strassen 1962; Polyanskiy-Poor-Verdu 2010; Tomamichel-Tan 2013. Solved: the second-order (dispersion)
  expansion -ln beta_n = n D - sqrt(nV) Phi^{-1}(epsilon) + O(ln n) with V the relative-entropy variance. Use
  here: the dispersion experiment validates V along the binding cut and frames the open distributed-dispersion
  question.
- Han 2003 (information-spectrum methods); Han-Verdu (information-spectrum). Use here: the independent-codebook
  joint-typicality decoder whose spectral inf-information rate equals I(U;Y) for stationary sources.

## Strand 7 — Adversarial and resilient distributed detection
- Vempaty-Tong-Varshney (Byzantine detection survey); Chen-Vempaty-Varshney; and time-varying Byzantine
  hypothesis-testing work. Solved: resilient consensus and detection under a fraction of adversarial nodes or
  links. Limitation: constrains adversarial behavior, not bits per edge. Difference: as a converse, the present
  bound only tightens under Byzantine links, since adversarial edges reduce honest information flow.

## Novelty statement (the cell no prior row occupies)
No prior work characterizes the exact error exponent at a node under the simultaneous presence of a time-varying
directed topology, no fusion center, and per-edge Shannon-rate constraints. Ahlswede-Csiszar, Han, and
Aguerri-Zaidi solve the static rate-limited case with a detector; Nedic-Olshevsky-Uribe and the social-learning
line solve the time-varying case without a rate limit; the Byzantine line changes the adversary model, not the
rate. The present paper occupies the intersection as a matched converse-achievability pair, and confirms it with
an exact optimal-detector measurement, a genuine routed-network simulation, and an actual GF(q) random linear
network code.

## Reference count
The reconstructed manuscript cites 54 works spanning all seven strands, within the target range of fifty to
sixty, with priority on IEEE Transactions on Information Theory, foundational monographs, and the directly
competing rate-limited and time-varying lines. The `refs.bib` database retains a few additional background
entries that are available but not cited in the final manuscript.
