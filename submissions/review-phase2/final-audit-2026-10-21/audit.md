# Final Phase 2 submission audit and corrections

Reviewed on 21 October 2026. Target confirmed by the authors: `submissions/phase2-with-claude.tex`, as pulled at `fac09ec`.

The source has been revised and compiled to a 23-page PDF. This audit records 45 issues and clarifications, including substantive design changes, evidence corrections and presentation repairs. It does not claim an exhaustive proof that no issue remains.

## Main design changes

The acquisition endpoint now excludes Hulk so that legitimate untargeted learning is not mixed with the targeted attack endpoint. The main threat remains one client at doses 0, 0.10, 0.30 and 0.50; a weak attack is reported rather than triggering an underspecified stronger confirmatory setting. The memory diagnostic repairs only stored poisoned labels in a DC clone, making its causal interpretation narrower and explicit.

Canonical numeric records and session metadata now come from the same TrafficLabelling row. Session and content links define atomic split/ownership components. The revised protocol uses a fixed group-stratified split and calls the study a simulated class-arrival experiment; it does not promise globally future-only prediction. This is a deliberate protocol correction, not a report of a completed data rebuild.

Client-local importance, replay IDs/logits, admission inputs, inactive clients, head expansion and paired random streams now have operational definitions. The statistical plan uses one Holm correction across 29 confirmatory contrasts. The old separate C1/C2 corrections were not automatically invalid; the revision gives the overall document a clearer error-control scope. The generic interaction formula was redundant/ambiguous rather than necessarily numerically wrong when zero-dose changes are zero. The original 633 full-run arithmetic was also correct and is retained.

## Evidence and scope

The review used the complete target source, the proposal-scope preference, earlier review notes, the local source papers in `docs/papers/` and their page-level extracts, and the official June 2025 JCR table already downloaded in `tmp/literature/jcr-2024.pdf`. The table's dated category entries verify the ranking statements now used. Sensors and Electronics are category-dependent Q2 entries; Electronics is explicitly Q3 in Computer Science, Information Systems in the same edition. Scientific Reports is Q1 in Multidisciplinary Sciences. Evidence excerpts, page numbers and the ranking PDF hash are recorded in `ranking_evidence.json`.

The paper-review skill's mandated external `claude -p` launcher was unavailable: no Claude executable was installed. This is a direct review, not a fabricated independent panel or consensus. The built-in compiler timed out; local Tectonic 0.17.0 successfully compiled the document instead. The course brief itself was not among the inspected project files, so assignment coverage was checked against the project's documented Phase 2 requirements rather than a claimed independent reading of the brief.

## Concern register

“Addressed” means the manuscript's claim or proposed rule was corrected; it does not mean the experiment was executed. Some entries strengthen or clarify an otherwise defensible choice, rather than repair a mathematical error.

| ID | Severity | Location | Concern | Correction |
|---|---|---|---|---|
| F01 | Major | Abstract; gap synthesis | Novelty claims extended beyond the selected accessible corpus. | Bound claims to the reviewed studies and identify the preprint as closest located work, without asserting worldwide absence. |
| F02 | Major | Gap justification | The proposed comparison was called pre-registered without evidence of a completed registration. | State that protocol and analysis will be frozen before final runs; keep the document prospective. |
| F03 | Minor | Search strategy | The stated search window extended through December 2026, beyond the October submission. | Close eligibility at 20 October 2026. |
| F04 | Major | Search strategy | Full-text accessibility and database coverage could bias conclusions about gaps. | Describe this as a focused accessible-corpus review and explicitly limit the inference. |
| F05 | Major | Corpus table | Ranking edition, category and verification status were not consistently explicit for the new journals. | Use 2025 JCR / 2024 JIF consistently; verify Sensors Q2 (II), Electronics Q2 (EE) and Q3 (CS-IS), Scientific Reports Q1 (MS) against the archived official table; add the actual source citation. |
| F06 | Major | P7 summary; comparison; gaps | The WeiDetect auxiliary-size claim pointed to Table 9 rather than the CSE-CIC-IDS2018 Appendix Table 11; its scope and the reported +70% magnitude were easy to overread. | Correct the table, name the auxiliary-pool denominator and dataset-specific setting, and remove the ambiguous percentage/percentage-point magnitude. |
| F07 | Major | P4/P9/P10/P12 critiques | Score gaps, uncertain samples, rare-class confusion and acquisition triggers were treated as stronger causal evidence than they provide. | Distinguish demonstrated results from plausible vulnerabilities and hypotheses; label-poisoned features need not be outliers. |
| F08 | Major | Cross-paper reporting critique | Missing repeated-seed uncertainty was sometimes equated with proof that no repeated runs occurred. | Retain the documented single seed in P11; qualify P12/P13 as lacking reported repeated-seed uncertainty. |
| F09 | Major | Step 1; support table | Fixed 3/8/12/15 output widths did not explain what happens when rare classes lose training support. | Treat these as maximum widths, omit classes with no usable training rows, and freeze actual widths/eligibility before final runs. |
| F10 | Major | Step 2; source appendix | Aligning MachineLearningCSV feature rows to separate metadata rows was not identifiable in the presence of duplicates. | Project numeric features and metadata from the same TrafficLabelling row; use MachineLearningCSV as the schema reference; prohibit positional/value-only joins. |
| F11 | Major | Step 2 | Session identity, endpoint direction and reconstruction uncertainty were underdefined. | Use unordered endpoint-and-port pairs plus protocol and interval-based 120-second idle gaps, with data-only threshold sensitivity and a metadata feasibility gate. |
| F12 | Major | Step 3; isolation appendix | Session isolation and exact-content isolation could conflict if split assignment was done separately by class. | Group connected components of session and duplicate links before assigning splits/owners; quarantine conflicting labels and retain deterministic same-label survivors. |
| F13 | Major | Step 3; validity | Per-family chronology could be mistaken for globally future-only testing, especially with mixed-label components. | Use one fixed group-stratified split with approximate ratios and explicitly limit conclusions to simulated class arrival; report dates and host/testbed confounding. |
| F14 | Major | Steps 1/3 | T0, later benign cohorts, scaler behaviour and metadata availability needed coherent boundaries. | Use isolated Monday T0 only for the frozen scaler, forbid refitting/clipping and fresh-record reuse; permit IDs for bookkeeping but exclude metadata from predictive inputs. |
| F15 | Major | Support table; acquisition | Row counts alone did not define adequate group support or guarantee nonempty acquisition sets. | Add a distinct-component floor, required anchors/source and at least one eligible untargeted new family in each acquisition stage; call the floor operational rather than a power guarantee. |
| F16 | Major | Step 4; external tier | The external dataset was budgeted without an explicit transferred source-family/schedule protocol. | Make it conditional on an independently locked schema, source mapping, schedule, dose and isolation audit; transfer method settings only. |
| F17 | Major | Step 7 dose | The equal-client 10% global corruption example did not describe the actual Dirichlet ownership design. | Report realised global and source-local denominators, admitted poison and aggregation weights. |
| F18 | Major | Step 7 pairing | Dose draws were not explicitly nested or protected from filter-induced changes to random-number consumption. | Use nested prefixes of one eligible-ID permutation, common attack IDs across arms, and separate random streams. |
| F19 | Major | Threat model; pilots; budget; failure taxonomy | Fallbacks changed attacker count/maximum dose while the final four-dose grid and contrasts remained underspecified. | Keep one attacker and the original four doses for confirmation; report weak/null attacks and require a separate exploratory protocol for stronger threats. |
| F20 | Major | Development pilots | Hyperparameter pair values, pilot defaults, score aggregation and tie-breaking were missing. | Specify the grids/defaults, one common synchronisation budget, clean development tuning, and deterministic ties; reuse DR settings for its admission variants. |
| F21 | Major | Step 7 | An identical E1 checkpoint was not fully specified as model plus persistent client state. | Clone replay, counters and random states as well as weights; retain all final seeds regardless of attack effect. |
| F22 | Major | Admission rule | Loss ranking of new classes depended on newly initialised outputs, stochastic scoring and undefined ties. | Expand before scoring, disable dropout, freeze one scorer per stage, break ties by immutable ID, and acknowledge that novelty scores may be unreliable. |
| F23 | Major | Steps 1/5; algorithm | It was unclear whether counts/new-class protection could access true labels or poison markers. | Register supplied current labels before filtering and use only supplied labels for counts/quotas; restrict reference labels to the builder/evaluator and oracle diagnostic. |
| F24 | Major | Algorithm; reservoir | Admission could be read as applying to memory only, while all current rows still trained. | Use admitted mini-batches and admitted IDs for both training and replay insertion; bypass memory in FT/EI. |
| F25 | Major | FedAvg; algorithm | Zero-current-data clients and repeated-epoch/replay counts were not explicitly excluded from aggregation weights. | Weight distinct admitted current rows once, exclude inactive clients, and invalidate a stage with no active clients. |
| F26 | Major | EWC-style learner | The anchor, importance owner, evaluation point and relation to the final aggregate were incomplete. | Broadcast the final shared model, update client-local importance there once, anchor at that model, preserve old importance and zero-pad new coordinates. |
| F27 | Major | Learner definitions | The design could be mistaken for exact Fisher-EWC and canonical DER++ implementations. | Identify squared minibatch-mean gradients as an approximation and explicitly disclose masked/normalised, post-update-logit DER++-style choices. |
| F28 | Major | Reservoir | First-pass insertion was ambiguous across multiple synchronisation rounds, and reservoir fairness did not name the admitted population. | Persist seen-ID/counter state across rounds/epochs, consider each admitted ID once, and specify replay sample size and the empty-memory case. |
| F29 | Major | Stored logits | Storage timing, dropout state, head alignment and post-broadcast refresh were undefined. | Cache post-update evaluation-mode logits once, align by class ID, and leave stored logits unchanged across broadcasts. |
| F30 | Major | Acquisition equation; traceability | Averaging Hulk together with honest new families entangled the adaptation endpoint with the targeted attack endpoint. | Define confirmatory acquisition over eligible untargeted new families; keep an all-new score including Hulk descriptive. |
| F31 | Major | Admission diagnostics | Honest-new admission could be presented as evidence for DC even though it retains those supplied labels by construction. | Treat 100% retention as a mechanism check and require measured untargeted-family F1 for adaptation. |
| F32 | Major | Persistence endpoint; validity | A later source error alone does not establish replay causation or recovery after honest source data return. | Use matched clean trajectories, call H attack-associated persistence, and distinguish withdrawal without fresh source data from recovery. |
| F33 | Major | Memory diagnostic; budget | Replacing poison with unspecified honest records altered several memory fields and did not define a unique causal contrast; the diagnosed arm was unclear. | Use two DC clones per seed; correct stored poisoned labels only, holding IDs/features/logits/weights/states fixed; restrict interpretation to erroneous-label replay and keep 24 continuations. |
| F34 | Major | Metric undefined-value rule | Undefined precision with no predicted positives could lead to dropping a valid zero-recall/zero-F1 class. | Calculate F1 directly from TP/FP/FN, preserve legitimate zeros, and reserve N/A for actual zero denominators with declared handling. |
| F35 | Major | Metrics appendix | ACC, BWT, forgetting, test-bank composition and clean FAR timing were named without full operational definitions. | Define stage cohorts, current-head predictions, cumulative scoring, equal-stage ACC, BWT/forgetting and E4 clean FAR on a fixed benign bank. |
| F36 | Minor | Interaction appendix | A generic clean-subtraction formula obscured that H and recall change were already clean-adjusted. | Write their learner contrast as a direct difference. The original is numerically equivalent if its zero-dose adjusted endpoint is correctly set to zero. |
| F37 | Major | Confirmatory statistics | Separate C1/C2 error control was legitimate only for the separately scoped question groups. | Strengthen the proposal to one 29-test Holm family for document-wide claims; explicitly note this is a conservative design refinement, not proof the old two-family arithmetic was invalid. |
| F38 | Major | Statistical appendix | Exact testing and interval language did not fully state symmetry, zero/tie handling or coverage limitations. | Specify sign enumeration on ranked nonzero differences, all-zero p=1, tied ranks, rank-biserial effects and descriptive bootstrap intervals; remove an underqualified exact-interval claim. |
| F39 | Major | Statistical conclusions | P-value resolution could be confused with power, and null significance with robustness/equivalence. | Recalculate the 29-test first-Holm resolution (11 nonzero pairs), state no demonstrated power guarantee, and retain uncertainty/null findings. |
| F40 | Major | Failure handling | Discard-and-fix language did not ensure that all affected matched runs were rerun. | Version repairs, rerun complete matched sets, avoid imputation, and preserve the fixed multiplicity count with unavailable tests reported explicitly. |
| F41 | Minor | Budget; ablations | The original 633-run sum was correct, but clone arms, eight changed settings, cached prefixes and the core/development distinction needed clarity. | Retain 633 full trajectories plus 24 continuations; explain 81 development, 240 core final, and the eight ablation settings. |
| F42 | Major | Cost; model paragraph | Raw parameter bytes and a small MLP did not establish total state size or CPU feasibility. | Separate the 76,348-byte raw payload from replay/importance/optimiser/serialisation costs; require pilot timings and report component costs. |
| F43 | Major | Baseline table | Fine-tuning was called a lower bound, which need not hold under poisoning or even clean learning. | Describe it as a reference without explicit retention, which can outperform continual-learning methods; distinguish the low-loss control from actual Co-teaching. |
| F44 | Minor | Architecture; captions | Figure labels implied generic leakage-free data and did not match the corrected acquisition endpoint. | Use group/content checks and honest-new F1; preserve the separate exploratory branch and compact its footer without shrinking diagram text. |
| F45 | Minor | Typesetting; navigation | A floating glossary interrupted prose; comparison tables crowded one landscape page; section/float barriers produced a nearly empty page; heading/column text overflowed. | Keep tables/algorithms near their introductions, give comparison tables separate landscape pages at 9 pt, fix column widths and wrapping, group the RQs, and fit both diagrams together; add PDF metadata and caption hierarchy. |

## Validation

The compiled PDF has 23 pages, 37 bibliography entries and 37 labelled objects. All 22 automated checks pass: citation/reference resolution, unique labels, ten additional critical reviews, twelve methodology steps, readable source encoding, no PDF replacement glyphs, no blank pages, no text beyond physical page boundaries, no overfull TeX boxes, and the parameter/run-budget/test-count/resolution arithmetic. Whole-page renders were inspected, with enlarged inspection of comparison tables and both diagrams. Visual inspection supplements these mechanical checks; neither certifies empirical validity.

The remaining compiler notices concern the bundled font configuration and an upstream style-file encoding comment; no missing glyphs or layout overflows appear in the output. The two diagrams share a page without reducing their text size. Comparison tables have their own landscape pages. The detailed machine-readable results and PDF/source hashes are in `validation.json`.

## Remaining empirical gates

- Validate actual TrafficLabelling metadata, feature projection, session reconstruction, duplicate components, T0 isolation and required class support before final runs. The manuscript states a stop/revise rule if these are infeasible.
- Measure clean-learning and CPU/resource feasibility using development seeds. No experiment result, effective defence, privacy guarantee or powered sample size has been invented.
- Lock the optional CICIoT2023 source-family/schedule protocol before its independent runs; omit that exploratory tier if infeasible.
- Treat corpus novelty as bounded by the documented accessible review, and all statistical conclusions as conditional on the capture, split and label-only attacker.

## Files

- Revised editable source: [phase2-with-claude.tex](../../phase2-with-claude.tex).
- Compiled submission: [PDF](../../../output/pdf/phase2-with-claude.pdf).
- Exact original source: [backup](phase2-before-audit.tex).
- Full concern register: [CSV](concerns_table.csv).
- Reproducible document checks: [validation script](validate_submission.py).

All work is saved locally. No experimental implementation or results files were modified as part of this submission review.
