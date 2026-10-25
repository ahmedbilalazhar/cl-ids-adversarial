# Data-release decision after the full-source census

24 October 2026. New acquisition/census evidence changes the earlier header-only contingency. Neither release is automatically selected for final execution. No models or final performance results were produced.

**Latest recommendation:** the additional [source-semantics review](feature-semantics-and-final-recommendation.md) proposes 74 inputs after identifying positive header inconsistencies. The 76-feature screened results below remain candidate evidence, not the final adopted dataset.

## 1. What is now available locally

| Candidate | Acquisition evidence | What it does not establish |
|---|---|---|
| Original metadata-bearing `GeneratedLabelledFlows.zip` | Public mirror pinned to commit `ab4a10050a2a5c3a9b36c126a409f1898a589059`; 283,876,488 bytes; archive SHA-256 matches its recorded Git-LFS object; all eight members read with CRC verification | Provider authentication, perfect labels, reliable sub-minute time, successful isolation/support or conformance of the legacy builder |
| Authors' corrected `CICIDS2017_improved.zip` | 343,549,013 bytes; all five members fully read with CRC/SHA-256 evidence; complete candidate census | Original-feature semantic equivalence, automatic 15-class taxonomy compatibility or adequate E3 support |

See [original-acquisition-full.json](original-acquisition-full.json), [corrected-acquisition-full.json](corrected-acquisition-full.json) and [corrected-full-census.json](corrected-full-census.json). Raw archives/working arrays are under Git-ignored `data/raw/phase3-feasibility-*`; they are not included in the planning ZIP.

The official original-release page still supplies the acquisition form. Direct-path probes returned HTTP 200 **HTML**, not ZIP data. HTTP status alone is therefore an invalid download-success check. No form or personal data was submitted. The mirror provides an auditable candidate, not a vendor signature. [Official dataset description](https://www.unb.ca/cic/datasets/ids-2017.html).

## 2. The corrected E3 problem is structural

Using the authors' conservative attempted-to-benign rule, the complete corrected-source census has the following finite candidate-input counts **before** component grouping, duplicate/conflict handling or T0 exclusion:

| Thursday family | Rows | Implication for the 50 train / 50 dev / 50 test floor |
|---|---:|---|
| Web brute force | 73 | Impossible: even the necessary 150 total rows are unavailable |
| Web XSS | 18 | Impossible |
| Web SQL injection | 13 | Impossible |
| Infiltration | 36 | Impossible |
| Infiltration - Portscan | 71,767 | Potential candidate only; label mapping and component/split support still need audit |

These counts are an observed **source census**, not experimental performance. A group split cannot create the missing rows. Lowering the floor or counting attempted traffic as successful attacks solely to rescue a stage would compromise the stated rationale. The authors explicitly distinguish attempted traffic and advise against giving it a separate model class. [Author label guidance](https://intrusion-detection.distrinet-research.be/CNS2022/Dataset_Download.html).

The corrected source has sixteen confirmed labels including benign before a deliberate taxonomy merge. The existing head/buffer maximum of fifteen cannot be copied automatically. Merging `Infiltration - Portscan` into Infiltration changes the semantic class and can make E3 overwhelmingly a scan-recognition task; it is not a cosmetic alias. Keep a table of original label, mapped label, stage, reason and retained support.

## 3. Original timestamps need a separate decision

The original archive contains both second-resolution and minute-only timestamps without AM/PM. Monday's seconds do not resolve its afternoon clock ambiguity. The full format/hour census is saved by `tools/census_original_feasibility.py`. Preserve original strings and file identity. Parse the date as the documented July capture week; do not let a locale-dependent parser reinterpret it.

A capture-window interpretation can potentially resolve 1–5 o'clock as afternoon, but that is an explicit source-specific rule, not information present in the string. Never manufacture seconds or a UTC offset. A 120-second operational session gap on minute-resolution records needs its precision limitation and 60/300-second sensitivity stated. Consider a conservative interval-uncertainty grouping sensitivity if exact boundary decisions matter.

Data from the two releases must never be joined by row position or feature equality to borrow better timestamps. The corrected extractor produces different flows; both features and metadata stay on their own source row.

## 4. The source-family security construct is limited

The correction authors document an implementation defect in Hulk and unusually distinctive flow artifacts. Thus this study measures recognition of the release's reference Hulk family and its label-poisoning response. It does not demonstrate prevention or recovery of a successful real-world DoS. This caveat affects the original capture too; changing only the CSV release does not remove the underlying attack-generation artifact. [Author investigation, Hulk section](https://intrusion-detection.distrinet-research.be/CNS2022/CICIDS2017.html).

An alternative-source sensitivity can address source specificity if declared and budgeted before final outcomes. A maximum-dose five-core-arm, twelve-seed sensitivity would add at most 60 poisoned full trajectories, with exact clean references potentially reusable. It changes the source bank, eligible attacked-site population and acquisition positive-family set; all those contracts must be explicit. It is not included in the 441/513 base plan.

## 5. Recommended conditional route

### Course fidelity to the submitted Phase 2

Complete the original same-row metadata/schema/clock and full component audit. If the required anchors/source/new-family support survives, retain the original schedule and fifteen-class maximum with the limitations above. Document the mirror route and seek provider-side provenance confirmation when possible. Do not call the existing MachineLearningCSV cleaner the new canonical builder.

### Stronger corrected-release publication candidate

If prioritizing correction of known annotations, amend prospectively to the corrected release. Preserve confirmed label distinctions initially, use a sixteen-output maximum if all have training support, and let a fully audited Infiltration-Portscan class support E3 only if scientifically justified. Explicitly narrow the acquisition claim; the web families remain rare/descriptive under this policy. Do not promise a web-attack acquisition result that the data cannot support.

At sixteen logits, the declared raw replay tuple is `304 + 64 + 8 + 8 + 1 = 385` bytes, or 192,500 bytes per 500-slot client buffer. Maximum model parameters are `18,112 + 65*16 = 19,152`, or 76,608 FP32 bytes. Update capacity/registry/message specifications and retune under that data contract before any final experiments.

If component isolation makes the revised stage infeasible, choose a different scientifically justified dataset/schedule before development. Corrected and original CICIDS2017 remain the same capture; do not count agreement between them as independent external replication.

### Immediate priority

Finish the data gate and a conforming reference implementation before expanding the experiment grid. The new source evidence is more useful now than adding optional GPU trajectories. Keep both candidate audits traceable and make the final release/stage decision before model outcomes.

## 6. Completed screened-corrected feasibility route

The fixed canonical-component split now has 817,226 train, 272,407 development and 272,406 test survivors, with zero cross-role component intersections. Hulk has 95,086/31,695/31,687 rows and 8,563/2,858/2,849 components. FTP/SSH and all required E2/E4 untargeted families pass; Infiltration-Portscan is the only E3 family meeting the declared floor, at 3,592/1,198/1,197 rows.

Heartbleed has zero training/development rows and eight test rows in one component. It is held-out-only/unlearnable under this fixed supervised protocol: report its coverage, never pre-register its output or score it as an acquired class. The candidate therefore has sixteen annotated labels but fifteen train-supported active outputs, with stage widths 3/7/12/15. Sixteen remains a taxonomy-dependent allocation ceiling, not the realized trained width. Do not search a new split seed to rescue Heartbleed.

The benign-bundle candidate selects exactly 3,500 benign examples per stage, 183,039 fresh training records overall, and valid eligible attackers for all twelve prescribed seeds. Maximum local source dose corresponds to 0.209%-34.642% global raw E2 contamination. Actual DC admission remains unobserved; the quota forces positive retained poison in ten of twelve maximum-dose seed inventories. See [realized-dose-and-quota-limits.md](realized-dose-and-quota-limits.md).

The additive screened-source ledger is [corrected-domain-checked-exclusion-accounting.json](corrected-domain-checked-exclusion-accounting.json); original counterpart counts are separate. The data audit does not select the profile, prove feature semantics or implement the production builder.

## 7. Annotation novelty is not behavioral novelty

Distinct Thursday Infiltration-Portscan and Friday PortScan reference labels do not by themselves establish distinct attack techniques. Their capture/scenario provenance can justify a declared annotation-class task, but the paper must explain the semantic target before claiming new attack-family acquisition. The screened corrected candidate therefore passes the stated count/isolation checks while its taxonomy remains a scientific adoption gate. If that distinction cannot support the intended question, choose a justified dataset/schedule before development instead of manufacturing novelty from label names. This is an inference about the task definition, not a claim that the annotations should be silently merged.
