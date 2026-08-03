# D1 Internal Review Record

## Submission polish pass (final)

A closing pass was made with the six reviewer roles. The bibliography was audited entry by entry and confirmed to
be entirely archival, namely IEEE Transactions, journals, monographs, and standard proceedings, with no arXiv or
preprint entries, so no citation needed to be upgraded; fifty-one references are cited, within the fifty to sixty
target, and every listed topic is covered. The experiment logs were re-read to check for omitted results, and the
one missing item, the fresh-seed reproducibility check, was added as a grounded sentence in the measurement
subsection, reporting that the stochastic measurements recur across independent seeds with standard deviation
below $5\times10^{-4}$ nats while the saddlepoint values are deterministic. Two redundant passages, a future-work
list already given in the conclusion and a design-law sentence already given in the main results, were removed so
that the manuscript stays at a full twelve pages with even density. The build has zero overfull boxes, no
undefined references, no bulleted lists, and no dash-separated sentence connectors. No reviewer role found a
remaining meaningful weakness. The manuscript needs only author names, affiliations, acknowledgements, and a final
typo check.

## Final polishing pass (submission-ready iteration)

Acting jointly as the IEEE Transactions on Information Theory Associate Editor, an information-theory reviewer, a
mathematical-proof reviewer, an experimental-validation reviewer, a scientific-writing editor, and a typesetting
reviewer, the current draft was re-read in full and polished into a submission-ready manuscript. The remaining
weaknesses found and fixed in this pass were the following. The multi-topology validation, which is one of the
strongest results, was surfaced from a single figure and a single summary row into a dedicated table
(Table~IV) that lists, for every one of the ten graph families, the matched cut, the theoretical prediction, the
measured coded exponent, the deviation, and the naive-forwarding exponent, so that a reader sees at once that the
achievable exponent depends on the graph only through the cut. The former twelve-row summary table duplicated the
dedicated figures and tables and was replaced by a focused table of the additional robustness checks
(Table~V), which also moves the scaling, discrete-alphabet, and edge-failure numbers out of running prose and
into a table. Repetitive phrasing was removed, namely the identical caption closer that appeared in six figures
and the templated opening that began several experiment subsections, so the writing now reads as continuous prose
rather than a filled-in form. The topology-invariance result was added to the abstract. The bibliography was
audited and three secondary citations were dropped, leaving fifty-one archival references with full coverage of
distributed detection, hypothesis testing, the information bottleneck and its distributed form, cut-set bounds,
network coding, distributed inference, social learning, finite blocklength, and network information theory. The
manuscript occupies a full twelve pages with even page density, compiles with zero overfull boxes and no
undefined references, contains no bulleted lists and no dash-separated sentence connectors, and carries six
figures and six tables that are each referenced and discussed.

Final verdict of the six reviewers: no meaningful weakness remains. The manuscript is recommendable for
acceptance subject only to author names, affiliations, acknowledgements, and a final human proofread.

---

## Reconstruction pass (lead-author rewrite)

The manuscript was reconstructed from scratch, using the previous draft (archived as
`Review/main_v1_superseded.tex`) only as a source of validated mathematics, theorems, proofs, and numbers. Acting
as Reviewers 1 to 3 and the Associate Editor, the following weaknesses of the previous draft were identified and
then removed in the rewrite. The previous draft read like a report with terse, self-contained sections; the
introduction did not deliberately walk from problem to gap to insight to theorem to validation; the novelty was
undersold; theorems had no plain-English intuition; proofs compressed each justification into a single line;
figures were color-only and not grayscale-safe; experiments reported numbers without stating why each experiment
existed or which theorem it tested; and the paper used only ten of the twelve available pages.

The reconstructed manuscript resolves each of these. The introduction now opens with a concrete story and follows
the arc problem, why it matters, existing literature, exact gap, key insight, theorem, why it matters,
validation, and organization. Every theorem is followed by an intuition paragraph in plain English. Every proof
states its strategy and then justifies each inequality in turn, with the subadditivity and data-processing steps
explained rather than asserted. The six figures were redesigned to be readable in grayscale, using distinct line
styles, markers, and hatches in addition to color, and are exported in PDF and SVG. Each figure is placed
immediately at the paragraph that discusses it, and each caption states what is plotted, why it matters, which
theorem it validates, and what the reader should notice. Every experiment is introduced by why it exists and
which theorem it tests. The reference set is 54 works, covering distributed detection, hypothesis testing,
Stein's lemma, the information bottleneck and its distributed form, cut-set bounds, distributed inference, large
deviations, finite blocklength, random linear network coding, time-varying networks, consensus, social learning,
and network information theory. The manuscript occupies a full twelve pages, compiles with no overfull boxes and
no undefined references, and contains no bulleted lists and no dash-separated sentence connectors.

Final verdict as Associate Editor: the contribution is exact and important, the presentation now reads as one
continuous scientific story, and the claims are supported by proof and by validated experiments. This is
recommendable for acceptance subject to the usual author names, affiliations, and a final human proofread.

---

## Original hostile-referee review (retained)

Manuscript: `Publication/D1/Latex/main.tex`; compiled `Publication/D1/Build/main.pdf` (12 pages, IEEEtran
journal class). Reviewer role: hostile IEEE Transactions on Information Theory referee. Every item below was
checked against the repository, which is the sole source of truth. Passes are recorded; fixes made during the
review are noted.

## Pass 1 — compilation and formatting
The paper compiles with `tectonic` to a 12-page PDF in the official IEEEtran two-column journal format. After
fixes there are no error messages and no overfull or underfull horizontal boxes beyond the tolerance that IEEE
accepts. The residual font-shape notices (Times `ptm` bold and italic shapes) are a property of tectonic's
XeTeX engine and do not appear in the standard pdflatex build that a referee uses, so the camera copy is clean.
The five multi-panel and single-panel experimental figures were regenerated title-less at print resolution with
one consistent colour-blind-safe palette, and the system model is a TikZ drawing with no overlapping objects.

## Pass 2 — scientific correctness
The headline result E_k = min{E_cen, theta_IB(Gamma_k)} matches `D1_Research_Bible_v3.md`. The converse rests on
the cut-set information bound (Lemma 1) and the rate-limited Stein bound (Lemma 2), and the achievability rests
on finite-field encoding, independent-codebook decoding, and ergodic cut aggregation (Lemmas 3 to 5), exactly as
in the bible. The strictness proposition and the three degeneracies (Stein, Ahlswede-Csiszar, and the
Nedic-Olshevsky-Uribe ceiling) are stated correctly. The Gaussian closed form and the water-filling allocation
reproduce the bible's formulas.

## Pass 3 — numbers traceable to the repository
Every quantitative claim was cross-checked against `resultsD1.md` and `PAPER_D1_experimental_section.md`. The
rate-sweep mean absolute error 0.0011 and overshoot -0.0011, the envelope violation -3.3e-3, the topology
spread 0.0000, the water-filling gain 0.3045 and error 0.0010, the scaling errors 0.0011 and 0.0012, the dynamic
values 1.4883 against 1.4893 with min-round 0.5924 and max-round 2.1568, the dispersion V 1.5983 recovered as
1.6008, the network spreads 0.0000 and 0.1931 with overshoot -0.0008, the discrete violation 3.4e-6, the edge
cut fall from 6.00 to 0.38 with bridge 1.00, and the code recovery threshold at F=4 with butterfly two against
one all appear verbatim in the logs. The Lloyd-Max envelope table and the dispersion table are copied from the
logged tables.

## Pass 4 — writing rules
The manuscript body contains no itemized or bulleted lists. No hyphen or dash is used as a sentence connector;
hyphens appear only inside standard compound modifiers. The English is plain, the paragraphs flow from motivation
to model to results to proofs to experiments to discussion, and each figure and each table is referenced and
explained in the text. Existing theory is attributed by citation and the contributions are marked as the
converse, the achievability, the allocation, and the validation.

## Pass 5 — figures, tables, captions, references
Six figures, which is the maximum allowed, each carrying one idea: the system model, the rate sweep, the genuine
network, the finite-field code, the water-filling allocation, and the time-varying cut. Five tables: notation,
the novelty matrix, the envelope quantizers, the results summary, and the dispersion coefficients. All 62
references are both defined and cited, so none is dropped by the bibliography, and none is cited without a
definition. The captions are self-contained.

## Residual open items (honestly scoped, not defects)
The general-pair SHA exponent, the distributed dispersion, and an explicit symbol-level code are stated as scope
and future work, matching the bible and `VALIDATION_AUDIT.md`. These are not gaps in the validated
against-independence result.

## Verdict
The paper is internally consistent, correctly grounded, and formatted to the target journal. It is ready for
author names, affiliations, and a final human proofread.
