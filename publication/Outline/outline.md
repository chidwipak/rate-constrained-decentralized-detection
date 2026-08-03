# D1 Outline Freeze — one continuous scientific story

Title: The Exact Error Exponent of Rate-Constrained Decentralized Detection over Time-Varying Networks

Working abstract target: 150 to 200 words. One paragraph. States the gap (the intersection of time-varying
topology, no fusion center, and per-edge rate), the result E_k = min{E_cen, theta_IB(Gamma_k)}, the matched
converse and Type-Preserving Network Coding achievability, and the exact numerical confirmation.

Section flow (each section transitions into the next; no fragmentation; prose only, tables allowed):

I. Introduction
   Motivation (distributed agents deciding over thin, changing links); the three coupled obstacles; the one
   sentence result; the four contributions; paper roadmap. Ends by pointing to the formal model.

II. Problem Formulation
   Agents, observations, conditional independence, the hard per-edge budget, the time-varying directed graph,
   the ergodic min-cut Gamma_k, the centralized exponent E_cen, the achievable exponent E_k. Defines
   theta_IB and C_DIB. Ends by asking for the exact E_k, motivating the results.

III. Related Work
   The seven strands from the literature survey, woven as prose: classical exponents; rate-limited testing;
   information bottleneck; social learning over networks; network coding and cut-set; finite blocklength;
   resilient detection. Ends with the novelty cell no prior row occupies.

IV. Main Results
   Theorem 1 (converse D1-star) and Theorem 2 (achievability D1-star-star), the zero-gap statement, the
   strictness proposition, and the three degeneracies (Stein, Ahlswede-Csiszar, Nedic-Olshevsky-Uribe ceiling).
   Intuition stated before formal mathematics. Ends by promising the proofs.

V. Proof of the Converse
   Strategy paragraph; Lemma 1 (cut-set information bound) with proof; Lemma 2 (rate-limited Stein) with proof;
   combination and strictness. Ends by turning to achievability.

VI. Achievability by Type-Preserving Network Coding
   Strategy paragraph; Lemma 3 (GF(q) encoding), Lemma 4 (independent-codebook joint decoding), Lemma 5
   (ergodic time-varying cut aggregation); composition to the matched exponent. Ends by specializing to the
   Gaussian model for computation.

VII. Gaussian Instantiation and Rate Allocation
   Closed-form theta_IB,i(R); symmetric network curve; asymmetric water-filling with the closed-form allocation
   and the O(N log N) algorithm. Ends by setting up the measurement instrument.

VIII. Experiments
   Measurement methodology (exact saddlepoint optimal-detector error plus dispersion-corrected fit; why naive
   Monte Carlo is infeasible). Then, each experiment as prose with why-it-exists, setup, and finding:
   rate sweep (Fig. rate-sweep), converse envelope (table), topology sufficiency and the genuine routed network
   with the coding-necessity insight (Fig. network), the actual GF(q) code (Fig. rlnc), water-filling
   (Fig. waterfilling), scaling and large-scale and discrete and edge cases (tables), time-varying ergodic cut
   (Fig. dynamic), and second-order dispersion (table). A results-summary table anchors the section.

IX. Discussion and Limitations
   Scope (testing against independence, conditional independence); the general-pair SHA converse as a different
   problem; distributed dispersion as open; correlated and Byzantine and non-ergodic cases; the honest
   modelled-vs-coded status now closed by the GF(q) experiment.

X. Conclusion
   The closed loop, its operational meaning (classical average-throughput design is inadequate for decision
   fidelity), and the outlook.

Appendix
   Supporting closed-form derivations (Gaussian IB curve; water-filling stationarity) if space in the body is
   tight; otherwise kept inline.

Figures (exactly six, each one scientific idea):
   1. System model (TikZ): time-varying directed rate-limited network, sources X_i, node k, binding cut.
   2. fig_e1_rate_sweep: measured exponent tracks theta_IB under the E_cen ceiling (main result).
   3. fig_n1_network: genuine routed network; converse holds, coding attains the cut and collapses topology,
      naive forwarding is sub-additive (achievability plus coding necessity).
   4. fig_n5_rlnc: an actual GF(q) random linear network code attains the cut; coding beats routing on the
      butterfly.
   5. fig_e4_waterfilling: heterogeneous rate allocation; water-filling beats equal split.
   6. fig_e6_dynamic: time-varying topology; only the ergodic-mean cut predicts the exponent.

Tables (unlimited): notation; prior-art novelty matrix; converse-envelope quantizers (E2/N3); experiment
results summary (E1-E7, N1-N5); dispersion coefficients (E7); scaling and edge-case numbers.

Writing rules enforced: no itemized lists in the manuscript body; no dash or hyphen sentence connectors; simple
English; every figure and table referenced and explained; every numerical value traceable to resultsD1.md.
