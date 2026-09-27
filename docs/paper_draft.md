# Paper draft — Computers & Security (Elsevier, full research article)

**Title (working):** *Poisoning Federated Class-Incremental Network Intrusion
Detection: continual-learning methods, Byzantine aggregation, and defence
confusion under non-IID drift*

Status: sections 1–5, 8 drafted from locked material; **section 6 (Results)
and 7 (Discussion) are placeholders** until the Phase-2/3/4 grids land — every
number slot is marked `[PENDING:<table>]` and must trace to
`results/wilcoxon.csv` / `results/stats_summary.csv`. The argument and
interpretation text is human-owned (per `docs/ai_disclosure_log.md`).

---

## Abstract (draft; final numbers PENDING: <abstract table>)

Continual-learning intrusion detection systems (IDS) are increasingly trained
federated across network segments, yet the security properties of the
*federated continual* setting are uncharacterised: existing federated IDS
poisoning work assumes static training, and existing continual-IDS work
assumes honest clients. We close that intersection. On CICIDS2017 (5 clients,
Dirichlet(0.5) shards, one malicious), we compare fine-tuning, EWC, LwF, ER and
DER++ under targeted label flipping across four budgets, and we characterise
three further axes that prior work leaves open: Byzantine update attacks
(sign-flip, little-is-enough, model replacement) against four server-side
robust aggregators; defence-specific *adaptive* attackers; and the effect of
task order, architecture, and a third dataset. Methodologically we also
quantify two preprocessing pitfalls that our own earlier measurements
inverted: per-task re-standardisation inflates average accuracy by ~25 points
and manufactures a method ranking that a leakage-free protocol does not
support, while random-within-day splitting inflates it by only ~2–3 points.
Our central result is that **no continual-learning method in our set separates
from plain replay once the protocol is leakage-free, but the federation
boundary — not the poison budget — determines what survives** [PENDING: <f2 +
byzantine headline>], and that defences that separate drift from poison fail
in both directions [PENDING: <defence + adaptive tables>].

**Keywords:** federated learning; continual learning; intrusion detection;
data poisoning; Byzantine-robust aggregation; replay attacks

---

## 1. Introduction

Network intrusion detection systems (IDS) trained on static traffic snapshots
decay as threat distributions shift; continual-learning (CL) IDS keep them
adaptive by learning new attack families sequentially. Two deployment pressures
now push CL IDS into a federated form: privacy constraints that forbid
centralising flow records across sites [refs], and heterogeneity — different
segments see different traffic mixes — which federated averaging (FedAvg)
[McMahan et al. 2017] is designed to absorb.

The security consequences of that combination are not understood. Three gaps
motivate this work.

**Gap 1 — federated IDS poisoning is studied, but only statically.** Recent
work systematically characterises label-flipping against federated IDS
(Lavaur et al., *Computers & Security* 2025) and reviews FL-IDS poisoning
defences broadly; other efforts add backdoors, feature poisoning, and
Byzantine-robust aggregation to FL-IDS (BRFID 2026; FedSecure 2026;
WeiDetect 2025). All of it trains a single model. None asks what happens to
*past* knowledge when the model is both federated and continually updated.

**Gap 2 — continual IDS is studied, but with honest clients.** Federated
class-incremental learning for IDS now exists (Korba et al. 2024; Mao et al.
2024; a 2026 EdgeFedCIL system that explicitly assumes honest server and
clients and scopes poisoning out). The nearest continual-IDS poisoning work
stays single-node (arXiv:2608.04602 replays-buffer attacks on CICIDS2017). A
2025 federated CIL cyber-attack-detection method states, in its limitations,
that it assumes honest clients and IID client data and names federated
poisoning and non-IID client data as future work — the call this paper
answers.

**Gap 3 — defence evaluation ignores that drift is legitimate.** Poison
detectors must separate *poison* from *legitimate distribution change*. In a
continual IDS the latter is guaranteed, which makes drift/poison confusion a
first-class failure mode rather than an edge case.

We contribute: (i) the first adversarial evaluation of federated
class-incremental IDS across five CL methods and four poison budgets, with
Byzantine update attacks and four server-side robust aggregators [PENDING:
<§6.2–6.3>]; (ii) defence-specific adaptive attackers that test whether each
defence holds when the attacker knows it [PENDING: <§6.4>]; (iii) a
methodological correction we had to make to our own measurements — a
leakage-free, scaler-consistent protocol under which two of our earlier
conclusions reversed, quantified rather than hidden [PENDING: <§6.1>]; and
(iv) generalisation evidence across task orders, three architectures, and two
further datasets [PENDING: <§6.5>].

---

## 2. Related work

*(Human-owned prose; evidence base verified in `docs/search_protocol.md` and
`docs/positioning_memo.md`. Coverage required by instruction 25: 5–10 recent
papers in this subfield, calibrated to the venue.)*

**2.1 Continual IDS.** CIL-for-NIDS surveys and systems (Cerasuolo et al.
2025 cross-dataset CIL NIDS; SSF, INFOCOM 2025), method taxonomies
(fine-tuning / fixed-representation / model-growth), and the CL-benchmark
lineage. Distinction: prior work targets accuracy under drift with no
adversary; T-DFNN/EEIL-type systems evaluate benign-traffic placement, not
poisoning.

**2.2 Federated IDS.** FL-IDS for IoT/IIoT/vehicular networks, non-IID
partitions and class imbalance, personalised FL variants, and the vehicular
SoK that documents field-wide pitfalls (artificial IID splits, trivial
benchmarks, weak adversarial evaluation). Distinction: single training pass.

**2.3 Adversarial ML for IDS.** Poisoning and backdoors in FL-IDS
(Lavaur 2025; BRFID; Nowroozi; FedSecure; WeiDetect), robust aggregation
(Krum, trimmed mean, coordinate-wise median, FedRDF-style dynamic weighting),
and their known weaknesses against adaptive attackers.

**2.4 Attacks on continual learning.** Persistent backdoors in CL
(USENIX S&P 2025; Salish & Kuniyilh 2026), replay-buffer manipulation
(arXiv:2608.04602 single-node IDS; Amnesia sampler-level), discovery-stage
poisoning of novelty/clustering pipelines (Sonic, Inf. Sci. 2026; AE
poisoning for ICS). Distinction: our persistent-flip and discovery-stage
results are inside an IDS, and our Byzantine results target the *aggregation
step* of a continual learner.

**2.5 Measurement pitfalls in IDS ML.** CICIDS2017 artefact and
duplication literature (Liu et al. CNS'22; Engelen et al. SPW'21; Galal 2026
on serialisation artefacts), which motivate our preprocessing audit.

---

## 3. Threat model

*As in `docs/threat_model.md` (federated poisoning + Byzantine primary;
discovery-stage secondary and separated).* Assumptions in one paragraph:
white-box, persistent adversary controlling a minority of federated clients
through data poisoning and/or update manipulation, with no server or
aggregation-rule control; conservative black-box defence evaluation;
adaptive attackers per defence; benign-only discovery threshold is
out of reach by design, so discovery poisoning is evaluated for *misfiling*
rather than suppression.

---

## 4. Methodology

**4.1 Continual-learning methods (hand-rolled PyTorch).** Fine-tuning, EWC
(diagonal Fisher, Kirkpatrick form with the ½ factor and per-task Fisher
accumulation), LwF (temperature-2 distillation restricted to the seen
head width), ER, DER++ — replay buffers use uniform random eviction and
inherit stream class imbalance (disclosed in every table). Classification head
is pre-sized over the full label space, uniform across methods; a growing-head
variant is reported as a named ablation rather than a silent choice.

**4.2 Federation.** 5 clients; per-task Dirichlet(0.5) label-skew shards; 1
round per task; FedAvg weighted by shard size; per-client CL state persists
across tasks. The clean FedAvg path is byte-identical to the earlier locked
implementation; robust aggregators operate on client *deltas*.

**4.3 Attacks.** Data: targeted and random label flipping at shard-relative
budgets; a persistent multi-task variant (each task's own majority attack
class); backdoor with a feature-space trigger (realism comparison) and a
physically grounded trigger whose feature values are exactly reproducible from
a documented TCP SYN burst. Updates: sign-flip, little-is-enough
(mean − z·σ over the benign update population, white-box), and model
replacement. Adaptive: loss-preserving flips against small-loss filtering and
kNN-preserving flips against label-consistency filtering.

**4.4 Defences.** Client-level small-loss filtering and kNN label
consistency; server-level Trimmed-Mean, coordinate-wise Median, Krum, and a
dynamic-trust aggregator (named for what it is).

**4.5 Protocol (the methodological core).** Chronological (per-class,
capture-order) train/test splits as primary; random-within-day as an explicit
secondary; frozen scaler fit on T0(+T1) train only; 12 seeds (1–11, 42);
Wilcoxon signed-rank within named families with Holm–Bonferroni correction,
bootstrap CIs of paired differences, and matched rank-biserial effect sizes;
full task-accuracy matrices throughout.

---

## 5. Experimental setup

Datasets: CICIDS2017 (primary, day-ordered CII sequence), UNSW-NB15 and
CICIoT2023 (replication; provenance, caps, and fingerprints recorded in
`data/processed/*.json`). Statistics: as §4.5. Compute: CPU grids with
per-run result files checkpointed on completion; deployment-cost measurement
is software-level and its platform is reported (no physical edge hardware was
available; stated in §8).

---

## 6. Results — PENDING GRIDS

*Fill order: §6.1 protocol decomposition → §6.2 federated headline →
§6.3 Byzantine + robust aggregation → §6.4 defences + adaptive attackers →
§6.5 order/architecture/dataset generalisation → §6.6 discovery-stage
secondary.* Every claim must cite raw p, Holm p, r, and the bootstrap CI from
`results/wilcoxon.csv`.

---

## 7. Discussion — PENDING §6

## 8. Threats to validity (draft; §6 numbers to be inserted)

*Internal:* hyperparameter bias is reported via order/architecture sensitivity;
our earlier per-task-scaler protocol is disclosed as a retracted measurement
path, with the corrected protocol primary. *External:* 5-client simulation
with 1 round/task; simulated, not captured, attacker traffic; CICIDS2017
artefacts; two replication datasets use published pre-split files (UNSW) and
a capped subsample (CICIoT2023). *Construct:* attack success is measured on
flow features, not full packet streams. *Scope:* deployment numbers are a
cloud/laptop software proxy — dedicated edge hardware was unavailable, and no
physical edge-device validation is claimed. *Chronological-vs-random split
delta, adaptive-attacker results, and cross-architecture/cross-dataset
generalisation are reported as resolved findings, not open limitations.*
