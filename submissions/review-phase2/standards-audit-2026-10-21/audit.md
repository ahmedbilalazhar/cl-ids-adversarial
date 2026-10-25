# Second Phase 2 review: methodology, implementation precision and diagram corrections

Started 21 October 2026; completed 22 October 2026. The confirmed target remains `submissions/phase2-with-claude.tex`. This review follows the first audit without overwriting its backup or validation record. `phase2-before-standards-review.tex` preserves the input to this pass.

## Outcome

Addressed 20 grouped issues and clarifications. They are not all mathematical errors: some are missing operational definitions, claim-scope corrections or presentation problems. The source compiles to 25 pages with 42 bibliography entries. All 40 document checks pass. This is a stronger research proposal, not a certified or empirically validated production IDS.

The largest substantive finding is the schedule-induced limitation of DC: fresh attack labels are always new, so DC protects those labels and filters benign-labelled records. The report now states exactly what that comparison identifies. Importance estimation is per-example and initialised explicitly; replay targets are cached before updates; retained memory is genuinely bounded in the proposed algorithm. Oracle label repair is interpreted as a downstream intervention rather than direct mechanism attribution.

## Diagram review

The workflow on page 20 separates T0, training, development and sealed testing, with a protocol lock and one-way final evaluation. The framework on page 21 identifies the poisoning entry point, one-time stage setup, repeated federated rounds, local replay reads/writes, stage-end EI state and checkpoint evaluation. E3/E4 stop fresh corruption but may retain poisoned replay. Crossings use white gaps to distinguish independent paths.

Both diagrams are native TikZ. Exact editable mirrors are in `submissions/figures/phase2-workflow-reviewed.tex` and `submissions/figures/phase2-framework-reviewed.tex`; their contents are inlined in the main source so the submission can compile as one TeX file. Older `phase2-methodology.*` assets remain historical and are not used by this submission.

## Concern register

| ID | Severity | Location | Concern | Correction |
|---|---|---|---|---|
| S01 | Major | Step 5, Eqs. 3-4 | A squared mini-batch mean gradient can cancel across records and is not the usual diagonal empirical-Fisher estimate. Initial importance and sampling size also needed definitions. | Average squared per-example supplied-label log-likelihood gradients; initialise importance to zero; sample exactly min(1024,n); evaluate at the final aggregate with dropout off; disclose the empirical-Fisher and online-EWC adaptations. |
| S02 | Major | Step 5, Eq. 5; Algorithm 1 | Replay target timing and stochastic dropout could make stored dark targets depend on an already updated model or inconsistent scoring modes. | Cache evaluation-mode logits before each update, read existing replay before inserting, match logits with dropout off and gradients enabled, and declare the adaptations and loss reductions. |
| S03 | Major | Step 5, Memory and Capacity accounting | A historical seen-ID set grows beyond the claimed bounded memory, and record count alone does not describe retained bytes. | Insert only on round 1/epoch 1; retain a scalar counter, pass cursor and RNG state; give Algorithm R; account for 381 raw bytes per slot and 190,500 per 500-slot client buffer, with overhead separate. |
| S04 | Major | Step 5, What DC actually tests | The schedule has no recurring fresh attack class, so the class-aware rule degenerates to preserving all supplied new attack labels and filtering benign labels. | Narrow the identified comparison to new-label protection at equal admitted volume; do not claim general recurring-class balancing or an independently demonstrated small-class benefit. |
| S05 | Minor | Steps 5 and 7 | Head-copy semantics and hidden optimisation defaults could yield different implementations. | Keep all active output rows trainable; define new-row initialisation, Adam parameters, last-update selection, reset policy, loss means, no reweighting/oversampling and reproducibility metadata. |
| S06 | Major | Step 8 and metrics table | Scores on families passing the support floor could be interpreted as whole-dataset IDS performance. | Label eligible-subset outcomes; retain a separate descriptive full-inventory view with rare-family support and errors. |
| S07 | Minor | Step 8, Operational error view | Multiclass scores alone do not specify an alert decision or operational false-alarm denominator. | Use the fixed multiclass argmax decision, alert on non-benign, and report attack misses and false alerts per 10,000 benchmark benign flows; do not invent a daily volume or deployment prevalence. |
| S08 | Major | Step 10, memory diagnostic | Oracle replay-label repair changes future optimisation and admission, so it cannot isolate a direct gradient effect. | Interpret it as the total downstream effect of that intervention, including mediated changes; preserve prior logits and weights and retain zero-repair pairs. |
| S09 | Minor | Steps 3-4 | The text claimed no learned feature transformation despite a fitted scaler, and a zero T0 feature range was unspecified. | Describe the frozen scaler as the fitted transformation; use denominator one for zero range, no clipping/refitting, and finite transformed FP32 input checks. |
| S10 | Minor | Step 10, eviction ablations | FIFO and class-balanced eviction were names without complete replacement rules. | Define oldest-insertion FIFO and largest supplied-label occupancy eviction with deterministic ties; bound and charge the extra order metadata; retain first-pass-only insertion and no retuning. |
| S11 | Minor | Table 11 and Appendix B | Stage-averaged ACC/BWT relied on disjoint benign cohorts without a declared allocation rule. | Partition whole benign test components into four non-empty seeded cohorts before outcomes, use their union for cumulative metrics and require at least four test components. |
| S12 | Minor | Step 7 | Attacker-site selection and the new importance RNG stream needed an explicit pairing contract. | Sample the eligible attacker site uniformly; record independent importance sampling, poison, ordering, initialisation, replay and dropout streams, plus bounded checkpoint state. |
| S13 | Major | Algorithm 1 and Step 12 | Immediate test access after each checkpoint could permit feedback into later scope or model choices. | Write checkpoints first, evaluate after the complete locked run set, and version/disclose amendments after any test inspection. |
| S14 | Major | Step 12 and bibliography | An industry-standard claim needs concrete research controls and must not be confused with certification or production readiness. | Use NIST RMF/AML and NeurIPS guidance with primary citations; specify hashes, versions, predictions, resource counts, deviations and planned acceptance gates; retain independent-site/deployment validation as future work. |
| D01 | Major | Figure 1, page 20 | The methodology overview omitted or blurred calibration, development, locked final runs and sealed-test information boundaries. | Show T0/train/dev/test branches, the protocol lock, checkpoint-only evaluation and one-way analysis/reporting; give the external dataset its own audit and protocol. |
| D02 | Major | Figure 2, page 21 | The framework omitted the actual label-poisoning entry point and could imply server access to client data. | Show one-client E2 training-label corruption before admission, supplied-label-only class registration and model/count messages to the server. |
| D03 | Major | Figure 2 and Algorithm 1 | Once-per-stage setup and repeated broadcasts/optimisation were not clearly separated. | Separate registry/head expansion/frozen admission from the repeat-round loop; show the final aggregate and the previous-stage parameter input. |
| D04 | Major | Figure 2 and Step 5 | EWC retained state had no clear read/write lifecycle or stage-end update. | Show local importance/anchor reads during updates and a single stage-end commit; restrict the computation to EI and preserve absent-client importance. |
| D05 | Major | Figure 2 and captions | Replay state was incomplete, and claiming E3/E4 had no poison ignored retained corrupted records. | Show feature/label/ID/pre-update-logit/width tuples, read and write paths, persistent counter/cursor, and the distinction between no fresh corruption and retained poisoned memory. |
| D06 | Minor | Figures 1-2 and document pagination | Crossed labels, ambiguous path intersections, isolated headings and a nearly empty final references page weakened readability. | Route connectors outside labels, bridge independent paths, preserve native editable TikZ mirrors in a self-contained source, keep section starts with their content and compact references to two readable pages. |

## Evidence and standards

The review uses the full manuscript, the preceding audit, relevant local paper evidence and the primary sources below. The purpose of the NIST and NeurIPS references is to make the research controls concrete. The document does not claim compliance, certification, a completed preregistration or executed experimental results.

- [NIST AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1): Research context, measurement, documentation and limitations; voluntary framework, not certification.
- [NIST AML Taxonomy E2025](https://csrc.nist.gov/pubs/ai/100/2/e2025/final): Threat goals, knowledge and capabilities; label-data poisoning scope.
- [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist): Claims, limitations, reproducibility and experimental/resource disclosure.
- [Kirkpatrick et al. EWC](https://doi.org/10.1073/pnas.1611835114): Importance-weighted regularisation baseline.
- [Schwarz et al. Progress & Compress](https://proceedings.mlr.press/v80/schwarz18a.html): Online accumulated importance/anchor adaptation, explicitly declared.
- [Kunstner et al. Empirical Fisher limitations](https://arxiv.org/abs/1905.12558): Empirical Fisher is not an exact model Fisher or a general curvature guarantee.
- [Buzzega et al. DER++](https://proceedings.neurips.cc/paper/2020/hash/b704ea2c39778f07c617f6b7ce480e9e-Abstract.html): Dark replay baseline; manuscript declares its caching, masking and normalisation adaptations.

The paper-review skill required an external `claude -p` reviewer launcher, which was unavailable because the executable was not installed. This was a direct review; no reviewer panel or consensus is claimed. Local Tectonic 0.17.0 compiled the existing source after the built-in compiler had timed out in the preceding review.

## Verification and remaining limits

`validation.json` records source/PDF/diagram SHA-256 hashes, 40 checks and per-page bounds/character counts. The checks cover references, bibliography, steps/reviews, arithmetic, declared lifecycle rules, exact diagram mirrors and PDF text/page integrity. Source assertions verify what the protocol states, not what experimental software executes. `visual_review.json` records the rendered-page review. Compiler notices are recorded, including one visually harmless underfull TikZ paragraph; no overfull boxes, unresolved references or replacement glyphs occur in the PDF.

The fixed budget remains 633 full trajectories plus 24 continuations (81 development and 240 core final trajectories). The 29-test Holm family and seed-level inference remain unchanged. No training experiments, production checks or implementation acceptance tests were run. Single-capture simulated clients, support-floor conditioning, empirical-Fisher approximations and DC's limited identified comparison remain explicit limitations. No exhaustive proof of correctness is implied.

All edits and artifacts are local. This pass did not commit or push to GitHub.
