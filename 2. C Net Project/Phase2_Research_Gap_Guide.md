# Phase 2 Guide — Choosing Your Research Gap
### A from-scratch walkthrough for Continual Learning for Network Security
**Project:** Continual Learning for Network Security · Saneedullah (23I-2568) · Ahmed Bilal (23I-2581)
**Document version:** 17 September 2026
**Read time:** ~60–75 minutes (or read Parts 0 and 4 first, then come back)

---

## Table of contents

- [Part 0 — The short answer](#part-0--the-short-answer)
- [Part 1 — Crash course: everything you need to understand the three gaps](#part-1--crash-course)
- [Part 2 — Your three papers in plain English](#part-2--your-three-papers-in-plain-english)
- [Part 3 — The three gaps, explained properly](#part-3--the-three-gaps-explained-properly)
- [Part 4 — Choosing your primary gap: pros, cons, scoring](#part-4--choosing-your-primary-gap)
- [Part 5 — The concrete Phase 2 plan for the recommended choice](#part-5--the-concrete-phase-2-plan)
- [Part 6 — Tools, datasets and your development environment](#part-6--tools-datasets-and-your-development-environment)
- [Part 7 — Annotated reading list](#part-7--annotated-reading-list)
- [Part 8 — Glossary](#part-8--glossary)
- [Part 9 — Supervisor Q&A (rehearse these)](#part-9--supervisor-qa)
- [Part 10 — This week's checklist](#part-10--this-weeks-checklist)

---

## Part 0 — The short answer

**Where you are.** Phase 1 was a *survey*: three papers, three critical summaries, a comparison table, and three gaps.

**Where you go next.** Phase 2 is a *decision*: pick **one** gap, turn it into a single falsifiable research question, and prove with a small experiment that it is answerable. Phase 2 is not "learn everything about continual learning". It is "choose the hill".

**The recommendation, stated once:**

> **Primary gap: Gap 2 (adversarial robustness of the continual-learning mechanism), narrowed to the unknown-attack *discovery* stage and to *federated* continual learning.**
> **Carrier dataset: Gap 1's fix (use CICIDS2017 / CICDDoS2019 instead of NSL-KDD) — this is not a separate objective, it is where you run the experiment.**
> **Optional extra table, not an objective: Gap 3's runtime + memory measurement on one real device.**

**Why not Gap 1 or Gap 3 as the headline?**
Gap 1 is mostly re-running known methods on newer data — valuable, low-risk, but a weak novelty claim for a final-year project and easy for an examiner to call "just a dataset swap". Gap 3 needs hardware you may not own, and its novelty is in *measurement methodology* rather than in security science; it is also the easiest to bolt onto another gap as a bonus. Gap 2 sits where the literature is genuinely thin, is 100% software, costs nothing, and produces a headline result you can put in a title.

**The critical warning — read this before you pitch Gap 2.** On 17 September 2026 an arXiv metadata search for `"continual learning" AND "adversarial" AND "intrusion detection"` returned **exactly one paper** (arXiv:2608.04602, Aug 2026). That one paper already does *single-node replay-buffer poisoning on CICIDS2017*. If you pitch "we will test poisoning attacks on a continual-learning IDS", a good examiner will find that paper and say "that exists". **You must aim at the part it left untouched:** the *unknown-attack discovery* stage (autoencoder + clustering), and the *federated* setting. Part 3.2 shows exactly how to phrase this.

---

## Part 1 — Crash course

Everything in Parts 3 and 4 assumes you know the following. If you already know a term, skip it. The [glossary](#part-8--glossary) at the end is a lookup table.

### 1.1 What an intrusion detection system (IDS) actually is

A network IDS watches traffic and decides: *is this normal, or is this an attack?*

Two flavours matter for your project:

| Type | How it works | Your project |
|---|---|---|
| **Signature-based** (Snort, Suricata) | Matches traffic against known attack patterns | Fails on new attacks — this is the motivation for everything you are doing |
| **Anomaly / ML-based** | Learns a statistical model of normal vs malicious from data | What your three papers use |

**What the model actually sees.** ML-based IDS almost never read packet payloads (traffic is often encrypted). Instead, a feature extractor (CICFlowMeter, Argus, Zeek) turns packets into **flows** — a flow is one conversation between two endpoints — and represents it as a row of numbers:

```
src_ip, dst_ip, dst_port, protocol, flow_duration, tot_fwd_pkts, tot_bwd_pkts,
fwd_pkt_len_mean, bwd_pkt_len_max, flow_iat_mean, ...  (≈ 78–80 features in the CIC family)
```

The label is `benign` or an attack name (`DoS Hulk`, `PortScan`, `DDoS`, `Bot`, …). Rows in, label out. That is the whole task — a tabular classification problem. **This matters practically: your models will be little MLPs/CNNs/transformers on tables, not giant neural networks.** That is why this project is feasible with free Colab or Kaggle GPUs, and even on a laptop CPU.

### 1.2 The problem that makes continual learning necessary: concept drift

A model trained on January traffic silently degrades in June, because:

- **New attack types appear** (concept drift in the attack space).
- **Normal behaviour changes** (new applications, new devices, new user habits).
- **The same attack mutates** (slightly different packets, same intent — called *novelty* or *covariate shift*).

There is a clean, citable measurement of this from the literature: arXiv:2412.00911 (SOUL) reports that a classifier trained on two days of traffic drops from **0.985 to 0.506** in attack-class detection performance when tested on three days of later traffic. That single number is the reason your project exists. Use it in your proposal.

**Two naive fixes, both bad:**

1. **Retrain from scratch on everything.** Works, but cost grows forever, you must store all history, and privacy rules (GDPR, hospital/ISP data) may forbid it. In a federated or edge setting it is physically impossible.
2. **Fine-tune on the new data only.** Cheap, but the network **catastrophically forgets** the old attack classes. This is the single most important concept in your project.

### 1.3 Catastrophic forgetting, and the stability–plasticity dilemma

**Catastrophic forgetting** (McCloskey & Cohen 1989; French 1999): when a neural network trains on task B after task A, gradient descent overwrites the weights that encoded task A. Performance on A collapses — often to near-random.

Concretely: train your IDS on Tuesday's attacks (FTP-Patator, SSH-Patator). It works. Then train it on Wednesday's attacks (DoS variants). If you just fine-tune, the model reaches ~99% on Wednesday and **~0% on Tuesday's attacks**. It has forgotten how to see them. In deployment this is a catastrophic security failure: an attacker uses an old exploit precisely because you stopped detecting it.

**The stability–plasticity dilemma** is the name for the trade-off you are now permanently negotiating:

- **Plasticity** = ability to learn the new thing (→ forgetting if maximised).
- **Stability** = ability to retain the old thing (→ rigidity/underfitting if maximised).

Every continual-learning method is a different bargain between these two. Every evaluation in your project measures that bargain.

### 1.4 The three continual-learning scenarios (get these labels right — examiners love them)

This is the vocabulary your Phase 1 report already used implicitly; Phase 2 should name it explicitly.

| Scenario | What changes across tasks | Can the model use the task ID at test time? | Example in *your* project |
|---|---|---|---|
| **Task-incremental (Task-IL)** | New tasks, distinct label sets | **Yes** (you know which task a sample belongs to) | "Which DoS *subtype* is this, given we know it's a DoS" |
| **Domain-incremental (Domain-IL)** | Same label space, distribution shifts | No | "Benign vs attack on Monday's traffic, then Tuesday's, then Wednesday's" — same labels, different statistical world |
| **Class-incremental (Class-IL)** | New **classes** appear over time; the model must distinguish all classes seen so far, **without** task ID | **No** | "After seeing Tuesday, Wednesday and Friday, correctly name *any* attack class seen so far" |

**Class-IL is the hard one** and the realistic one for IDS. When a paper says "class-incremental intrusion detection", it means: benign + a growing list of attack classes, and at test time the model gets a raw flow and must name any class it has ever seen. Paper 1 (Ge et al.) and Paper 2 (EdgeFedCIL) are both doing class-IL.

There is a fourth, useful one for Gap 1:

- **Class-instance incremental (CII)**, introduced by arXiv:2608.04602: benign traffic is *not* confined to task 0 — it reappears in every task alongside new attacks. This is more faithful to reality (benign traffic never goes away) and is a cheap way to look sophisticated in your proposal, since you can adopt it and cite it.

### 1.5 The three families of continual-learning methods (your baseline list lives here)

**Family 1 — Regularisation (protect important weights).**
Add a penalty that stops the model from changing weights that mattered for old tasks.

- **EWC** (Elastic Weight Consolidation, Kirkpatrick et al., PNAS 2017): compute the Fisher information matrix (≈ "how important is this weight"), penalise changes to important weights. *Weakness:* multiple Fisher matrices become intractable; tends to over-constrain and hurt plasticity.
- **SI** (Synaptic Intelligence, Zenke et al. 2017): cheaper online approximation of the same idea. Interesting result for you: arXiv:2603.00363 (Feb 2026, IoT IDS) found SI gave **near-zero forgetting with high training efficiency** — worth citing as a strong baseline.
- **LwF** (Learning without Forgetting, Li & Houlsby 2017): on new data, ask the *old* model for its soft predictions and distil them into the new model. Requires no data storage. *Weakness:* weak on long task sequences.

**Family 2 — Replay / rehearsal (keep a memory).**
Store a small buffer of old samples and mix them into every new training batch.

- **ER / Experience Replay** (Rolnick et al. 2019; Chaudhry et al. 2019).
- **iCaRL** (Rebuffi et al. 2017): exemplar selection + nearest-mean-of-exemplars classifier for class-IL.
- **DER++** (Buzzega et al., NeurIPS 2020, "Dark Experience Replay"): replay the old model's *logits*, not just labels. Usually the strongest simple baseline.
- **Generative replay** (Shin et al. 2017): train a generator instead of storing real data.
- *Weakness of the whole family:* you must store data, which is a privacy problem in networks — and, as we will see, **the buffer becomes an attack surface**. That weakness is Gap 2.

**Family 3 — Parameter isolation / architecture (carve out space per task).**
- **PackNet** (Mallya & Lazebnik 2018): prune then freeze; give each task its own subnet.
- **HAT** (Hard Attention to the Task, Serra et al. 2018): learn a per-task attention mask that blocks old weights.
- **Dynamic expansion / expert routing** (e.g. arXiv:2609.06346 CLUBA): add capacity when the task stream demands it.
- *Weakness:* the model grows; needs to know task boundaries.

**Your papers are hybrids.** Paper 1 = replay + distillation (Families 1+2). Paper 2 = replay + distillation + compression, federated. Paper 3 = feature-level distillation + decaying regularisation + replay. Translating their designs into this vocabulary is a quick way to show mastery in your Phase 2 write-up.

### 1.6 Federated learning (FL) in ten lines

Instead of shipping data to a server, you ship **models**:

1. A server holds the global model θ.
2. Each client *k* downloads θ, trains locally on its own private data, and uploads the update (its parameters or gradient).
3. The server aggregates: **FedAvg** (McMahan et al. 2017) computes a weighted average of the updates.
4. Repeat for many rounds.

It solves privacy and bandwidth. It creates two new problems:

- **Non-IID data.** Client A sees only port scans; client B sees only botnet traffic. Averaging such divergent updates is unstable. Standard benchmark trick: split one dataset *artificially* across clients using a **Dirichlet(α) partition** — one dataset, carved up unevenly. α smaller ⇒ more heterogeneous. **This is considered weak evidence of generalisation in the literature** (see the SoK, arXiv:2607.10914: "artificial IID data splits" is listed as a *recurring pitfall*), which is Gap 1's ammunition.
- **Malicious participants.** The server accepts updates it cannot verify. A single client can flip signs, scale its update up, or plant a trigger. This is Gap 2.

**Federated Continual Learning (FCL)** = FL + CL: clients learn a continuously growing sequence of tasks, aggregated through the server. This is Paper 2's setting, and it is *much harder* than either half alone: you must simultaneously fight forgetting (CL), non-IID-ness (FL), and now adversaries.

### 1.7 How continual learning is evaluated (you will be graded on this)

Let R(i, j) = accuracy on task *j* after training through task *i*. The standard numbers:

| Metric | Meaning | Formula (informal) |
|---|---|---|
| **Average Accuracy (ACC / AA)** | Final performance across all tasks | mean of R(T, j) for j = 1…T |
| **BWT** (Backward Transfer) | Did learning new tasks *hurt* old ones? Negative = forgetting | mean of R(T, j) − R(j, j) for j < T |
| **FWT** (Forward Transfer) | Did old knowledge help *new* tasks? | compare against random-init performance |
| **Forgetting (F)** | Average drop from each task's best-ever score | mean over j of (max_i R(i, j) − R(T, j)) |
| **Task-accuracy matrix** | The full T×T table; always report it | (just the matrix) |
| **Oracle / Joint baseline** | Model trained on *all* data at once. The upper bound. | One number |
| **Attack Success Rate (ASR)** | *(for Gap 2)* fraction of trigger/malicious inputs misclassified as the attacker's target | — |
| **Clean accuracy drop** | *(for Gap 2)* how much normal accuracy the attack cost | — |

The canonical reference for these metrics is **Díaz-Rodríguez et al. 2018, arXiv:1810.13166** ("Don't forget, there is more than forgetting: new metrics for Continual Learning"), which also proposes folding accuracy/latency/memory into one ranking score — useful for Gap 3.

⚠️ **The single most common mistake in student CL papers:** reporting only the final average accuracy. Paper 3's own critical summary in your report catches this exact sin — its headline 0.884 average hides a collapse to 58.4% by the last drift stage. **Always report the full matrix plus the last-task-to-first-task decay.** Averaging hides collapse; collapse is the result.

### 1.8 The vocabulary of research papers you will need to speak

| Term | Meaning |
|---|---|
| **Benchmark** | A standard dataset + protocol everyone reports on |
| **Baseline** | The method you must beat; usually a well-known simpler one |
| **Oracle / upper bound** | Best possible performance (train on everything at once) |
| **Ablation** | Remove one component of your method to prove that component matters |
| **SOTA** | State of the art — the current best published result |
| **Ablation**, **oracle**, **task sequence**, **buffer budget** | … |
| **Threat model** | For adversarial work: who is the attacker, what do they control, what do they know, what is their goal? **You cannot write a Gap 2 paper without one.** |
| **Q1 / SJR** | Journal quartile by SCImago Journal Rank (you already used this in Phase 1) |

---

## Part 2 — Your three papers in plain English

| | **Paper 1** — Ge, Feng & Sakurai (Future Internet 18(3):145) | **Paper 2** — Wu et al., "EdgeFedCIL" (Sensors 26(14):4630) | **Paper 3** — Luo et al. (Future Internet 18(9):457) |
|---|---|---|---|
| **Task** | Find *unknown* DoS attacks | Federated IDS at the IoT edge | Re-authenticate devices as RF fingerprints drift |
| **Setting** | Single node, class-IL | Federated, class-IL, non-IID | Single node, closed class set, domain drift |
| **Data** | NSL-KDD, DoS subset, 6 subclasses | ToN-IoT + X-IIOTID, artificially split across clients | Fully synthetic RF fingerprints, 10 devices, 20 drift stages |
| **Method** | Autoencoder flags unknown → HDBSCAN clusters it → distillation-weighted CIL learns the new cluster | Local replay + distillation; low-rank compression + quantisation to cut comms; classifier-head protection | Two-branch CNN; three-term feature distillation; decaying distillation strength; replay buffer |
| **Claim** | Adds new attack classes "without significantly degrading" old recognition | ~10.5× less data transmitted, competitive accuracy | Best stability–adaptability trade-off; S = 0.939 vs 0.871 for LwF+Replay |
| **Cost of the claim** | Only DoS; only 1999-era data; no adversarial test | Assumes honest server + benign clients; simulated edge devices | Fully synthetic; still falls to 58.4% historical accuracy by stage 20 |

**What each one gives you:**

- **Paper 1 gives you a mechanism to attack.** Its unknown-attack discovery (autoencoder + HDBSCAN) is the most interesting target in the three papers, and *nobody has attacked it*. Part 3.2.
- **Paper 2 gives you a setting to work in.** Federated + continual is where the adversarial surface is largest (malicious clients) and where the authors themselves declare the vulnerability out of scope.
- **Paper 3 gives you a warning and a metric.** The warning: averages hide collapse. The metric: EER-style reporting for authentication-shaped tasks.

---

## Part 3 — The three gaps, explained properly

For each gap: **what it means**, **why it exists (evidence)**, **what a project on it looks like**, **what could go wrong**, and **how strong the novelty claim really is as of Sept 2026**.

I verified novelty claims below using the arXiv API (metadata + abstract search, *not* full text — see the caveat in Part 3.4). Counts are as of **17 September 2026**.

---

### 3.1 Gap 1 — Validation on old, narrow, or synthetic data

#### What it means

All three papers prove their method works, but on data that does not resemble a modern network:

| Paper | Data | Why it is weak |
|---|---|---|
| 1 | NSL-KDD (derived from KDD Cup 1999) | Traffic from 1999: no encryption, no IoT, no cloud, no modern protocols. Also narrowed to one attack family (DoS) with six subclasses |
| 2 | ToN-IoT + X-IIOTID, split with Dirichlet(α) | One dataset carved into fake "organisations". No genuinely distinct networks. No live drift |
| 3 | 100% synthetic RF fingerprints | Generated from a fixed mathematical drift formula. **Zero real hardware anywhere in the paper** |

So: **the field's evidence base is legacy, artificial, or synthetic.** A method that wins on NSL-KDD may be worthless in 2026.

#### Evidence beyond your three papers (this is what makes Gap 1 credible)

- **arXiv:2009.07352** — *Data-Driven Network Intrusion Detection: A Taxonomy of Challenges and Methods* — a 38-page survey naming **eight** dataset-collection challenges, including: attack classes being extreme minorities, and datasets collected on **virtual machines or simulated "sandbox" environments rather than real networks**. Direct support.
- **arXiv:2607.10914** — *SoK: Federated Learning for Intrusion Detection in Vehicular Networks* — audits 60+ publications and lists recurring pitfalls verbatim: *"artificial IID data splits, reliance on trivial benchmarks, weak adversarial evaluation, and omission of real-time CAN constraints."* **This one sentence justifies Gap 1, Gap 2 and Gap 3 simultaneously — cite it in your introduction.**
- **Data-quality literature on the CIC datasets themselves.** CICIDS2017 has a well-known set of defects documented in the community (duplicate/near-duplicate flows, unidirectional flow representation, features with inf/NaN values such as `Flow Bytes/s`, very uneven class support, and questionable benign-traffic realism). The canonical critique is Engelen et al., *"Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study,"* IEEE Security & Privacy Workshops (2021). **Action: find and read this paper before you cite these defects** — I flagged it from domain knowledge and could not fetch it in this session (see §3.4).

#### What a project on Gap 1 looks like

> "We take the class-incremental IDS pipeline of Paper 1 (and/or the federated pipeline of Paper 2) and re-benchmark it on CICIDS2017 → CICDDoS2019 → CICIoT2023, with task sequences derived from real capture days rather than a hand-picked subset, and we report whether the reported gains survive."

Work required:

1. Download and clean the modern datasets (dedup, drop inf/NaN, class remapping). **This is 3–5 days of unglamorous work** — do not underestimate it.
2. Define honest task sequences (see Part 5.3 for the CICIDS2017 day-based sequence — it writes itself).
3. Re-implement or run 4–6 baselines.
4. Re-run and compare against the published numbers for the original datasets.

#### Pros and cons as a *primary* gap

**Pros:** lowest technical risk; everything is public; no hardware; you learn the full experimental pipeline; guaranteed to produce a result (even "the gains do not survive" is a result); directly answers a published criticism.
**Cons:** **weak novelty** — it is "apply existing methods to a newer dataset", which is a legitimate *contribution to evidence* but a thin *contribution to knowledge*. Risk of an examiner asking "what is new here other than the dataset?" You also need to be careful: other people are doing exactly this right now (e.g. arXiv:2409.18736 surveys adversarial NIDS; arXiv:2506.19877 compares ML models on CICIDS2017 known-vs-unseen).
**Verdict:** **Excellent as the carrier for another gap. Weak as the headline.**

---

### 3.2 Gap 2 — Nobody attacks the continual-learning mechanism itself ⭐ *recommended*

#### What it means

Your three methods are all learning systems that **continuously retrain themselves on data they do not fully trust**:

- Paper 1: learns from traffic the autoencoder flagged as "unknown" — i.e. from exactly the inputs an attacker can influence, and then teaches itself that data is a new attack class.
- Paper 2: accepts updates from clients it cannot verify, and stores them in a replay buffer.
- Paper 3: updates a security-critical authenticator over time, on the basis of a drift signal.

None of the three papers tests what happens when an **adversary targets the adaptation mechanism**, rather than the detector's output. This is a whole class of attacks:

| Attack | Who does it | Against which part | Concretely, in your project |
|---|---|---|---|
| **Label flipping** | Poisoner of the *training stream* or the replay buffer | Buffer integrity | Flip labels in 1% of stored flows → model collapses (see evidence below) |
| **Backdoor / trojan (trigger)** | Same | Buffer / federated updates | Plant a trigger pattern (e.g. a specific TCP flag + window-size combination); model keeps ~97% clean accuracy but the trigger makes attack traffic look benign → silently disables your IDS |
| **Model poisoning / Byzantine updates** | Malicious federated client | Aggregation | A client uploads a scaled-up or sign-flipped update; "little-is-enough" attacks stay under aggregation thresholds |
| **Model replacement** | Malicious FL client | Global model | Scale the malicious update so the backdoor survives averaging |
| **Evasion of the drift/novelty detector** | Attacker who can shape traffic | The discovery stage | Craft attacks that the autoencoder *does not* flag as novel, so they are never learned; or conversely flood it with benign-looking novelty to poison the cluster |
| **Cluster poisoning** | Attacker who can generate "unknown" traffic | HDBSCAN clustering (Paper 1) | Bias the discovered "new attack class" to absorb future benign traffic → permanent false-alarm generator, or blend real attacks into a benign-looking cluster |
| **Spoofed drift** | Attacker with an RF transmitter | Paper 3's authenticator | Delay/replay/synthesise a drifting fingerprint to keep an old device authorised, or to force re-enrolment |

#### Why Gap 2 exists (the group-level argument)

Your Phase 1 synthesis already made it: Paper 1 has no adversarial evasion test; Paper 2 explicitly declares malicious clients, poisoning and backdoors *out of scope*; Paper 3 has no spoofing test for a method whose entire purpose is authentication. **Add the meta-argument:** these are learning systems whose *defining feature* is that they keep updating themselves from untrusted data. Untrusted-data-updating is precisely the definition of a poisoning surface. The gap is not accidental; it is structural.

#### Evidence beyond your Phase 1 (critical — this is your novelty map)

I searched arXiv on 17 Sept 2026. Results:

| Search (arXiv metadata/abstract) | #Results | What it tells you |
|---|---|---|
| `"continual learning" AND "intrusion detection"` | 15 | A small, active field — healthy for citations |
| `"continual learning" AND "adversarial" AND "intrusion detection"` | **1** | **The gap is real and narrow** |
| `"backdoor" AND "continual learning"` | 18 | The *generic* problem is heavily studied — good for methodology, bad for naive novelty |
| `"federated learning" AND "intrusion detection" AND "poisoning"` | 15 | FL-IDS poisoning is studied, but **not** combined with continual learning |
| `"CICIDS2017"` | 66 | Chosen-carrier dataset is mainstream and well understood |

**The one paper in the intersection — and why it matters enormously to your pitch:**

> **arXiv:2608.04602** — *Adaptive Intrusion Detection System using Transformer-Based Neural Networks and Continual Learning Approach with Adversarial Investigation* (Aug 2026). Tabular transformer encoder + class-balanced experience replay on **CICIDS2017**. Introduces the **class-instance incremental (CII)** scenario (benign traffic reappears in every task). Then it does exactly what your Gap 2 proposes: **probes the replay buffer with label flipping and backdoor poisoning.** Findings: label flipping **collapses the model entirely** (0.0053 accuracy at a **1%** poison budget); the backdoor keeps **0.97 clean accuracy while achieving 95% ASR** on trigger flows, evading standard monitoring. Its conclusion: *"ensuring buffer integrity emerges as a strict operational requirement."*

**Read that as good news and as a constraint.**

- Good news: it proves the phenomenon is real and consequential, giving you a citable hook and a motivation ("existing work shows single-node replay buffers are catastrophically fragile; we ask whether the same is true of *discovery-based* and *federated* systems").
- Constraint: **"single-node replay-buffer poisoning on CICIDS2017" is now taken.** Do not pitch that.

**Other key papers to build your threat model on (all found, listed in Part 7):**

- **arXiv:2409.13864** — *Persistent Backdoor Attacks in Continual Learning* (USENIX Security 2025). Introduces **Blind Task Backdoor** and **Latent Task Backdoor**, which survive continual updates and **evade SentiNet and I-BAU** (two standard backdoor defences). This is your proof that continual learners are *worse* than static models against backdoors — the persistence-through-updates property your project is about.
- **arXiv:2609.06346** — *Robust Dynamic Expansion for Continual Learning under Backdoor Attacks* (CLUBA, Sept 2026). Formalises "every incremental task may contain a small fraction of poisoned samples" and proposes purification + selective recovery + robust expert routing. **This is your competitor *and* your defence baseline** — it shows the defence side is just opening up.
- **arXiv:2406.19753** — *Attack On Prompt: Backdoor Attack in Prompt-Based Continual Learning* (AAAI 2025). Up to **100% ASR**; the trigger persists *because* CL remembers well ("its impressive remembering capability can become a double-edged sword" — a beautiful line to quote).
- **arXiv:2602.13062** — *Backdoor Attacks on Contrastive Continual Learning for IoT Systems* (Feb 2026). Embedding-level attacks reinforced *by replay itself*; argues replay mechanisms amplify long-lived representation-level threats. Nearer to your domain than the vision papers.
- **arXiv:2409.18736** — *Adversarial Challenges in Network Intrusion Detection Systems* (survey). Your citation for "adversarial ML on **tabular/structured** network data is under-explored relative to images and text".
- **arXiv:2409.09794** — *Federated Learning in Adversarial Environments: Testbed Design and Poisoning Resilience in Cybersecurity*. Raspberry Pi + Jetson + **Flower**; shows FL-IDS remains *vulnerable to poisoning*. Also your Gap 3 hardware blueprint, if you want both.
- **arXiv:2601.06466** — *SecureDyn-FL* (IEEE TNSM): poisoning detection via gradient auditing, tested up to **50% adversarial clients** on N-BaIoT. A defence baseline to compare against.
- **arXiv:2312.04432** — *FreqFed* (NDSS 2024): frequency-domain filtering of malicious updates, evaluated on **IoT intrusion detection**. Another defence baseline.

#### What a project on Gap 2 looks like (properly scoped)

**The version that is already taken (avoid as your sole claim):**
❌ "We test label-flipping and backdoor attacks on a single-node class-incremental CIDS replay buffer on CICIDS2017."

**The versions that are still open — pick one primary, one secondary:**

**Option 2-A (strongest novelty, most interesting): attack the *discovery* stage.**
Paper 1's pipeline has three stages — autoencoder flags novelty → HDBSCAN clusters it → CIL learns the new class. Every existing poisoning study attacks a *classifier*. Nobody has attacked an *open-world discovery pipeline*, where the adversary can choose what gets discovered. Research question:

> *RQ: Can an adversary who can influence the traffic stream cause a novelty-detection-and-clustering continual IDS to (a) permanently miss real attacks, or (b) invent fictitious attack classes and merge them into benign intent — and do standard replay-based defences detect this?*

This is genuinely new, it directly extends Paper 1, and "attacks on the *learning* of new attack classes" is an appealing, memorable framing. It also produces an elegant negative result if the answer is "no".

**Option 2-B (federated, directly extends Paper 2): attack the aggregation.**
EdgeFedCIL assumes honest clients by construction. Research question:

> *RQ: How much of the continual-learning gain of a federated class-incremental IDS survives when a fraction of clients are malicious, and does the compression step (low-rank + quantisation) make poisoning easier or harder to detect?*

The "does compression help or hurt the attacker" angle is a nice, non-obvious twist that follows directly from Paper 2's own design.

**Option 2-C (defensive, if you want to build rather than break):**
Design and evaluate a lightweight **buffer-integrity defence** for continual IDS — e.g. loss-based sample purification (small-loss selection, as in AER, arXiv:2408.14284), gradient/update auditing (2601.06466), or frequency filtering (FreqFed) — and show whether it preserves the plasticity that makes CL valuable. Continual learning makes this harder than usual because *your defence itself runs on a non-stationary stream*, which is a genuinely under-explored setting.

**Minimum viable scope (what to actually commit to in Phase 2):**
- 1 dataset (CICIDS2017), 1 task sequence (day-based), 1 setting (whichever of 2-A/2-B), 3 clean baselines + 1 upper bound.
- 3 attack types: label flipping, backdoor, and **one of** {Byzantine update, cluster poisoning / evasion of novelty detection}.
- 2–3 budget levels per attack (e.g. 0.5%, 1%, 5%).
- Metrics: clean ACC/BWT (does the attack destroy utility?), ASR (**does the attack succeed silently?**), plus a defence comparison.
- 3 random seeds, mean ± std, and a simple significance test.

That is a complete, defensible final-year project and a plausible workshop/conference paper.

#### Pros and cons as a *primary* gap

**Pros:** genuinely thin literature in the exact intersection; 100% software; zero hardware cost; highly citable motivation (the *one* existing paper proves the phenomenon); builds directly on two of your three Phase 1 papers so your literature review is already 60% written; produces a memorable result ("we broke the model it taught itself"); strong security framing that examiners reward; and the *pessimistic* outcome is still a publishable finding.
**Cons:** you must write a **threat model**, which newbies find the hardest part (see §5.5 — it is a fill-in-the-blanks exercise, not a mystery); attack *implementation* on tabular flow data is fiddly (what is a "trigger" for a network flow? — see the discussion in §5.6); risk of being scooped (mitigate by aiming at 2-A or 2-B, not at the taken single-node variant); you need to be honest that generic backdoor-on-CL is well studied, so you must frame the contribution precisely.
**Verdict:** ⭐ **Best primary gap for this team.** Highest novelty-per-hour, lowest cost.

---

### 3.3 Gap 3 — No runtime, memory, or deployment-cost measurement

#### What it means

All three papers describe methods intended for *operational deployment* and then never measure whether they can actually run there:

- Paper 1: a three-stage pipeline (autoencoder → HDBSCAN → CIL) with no runtime, throughput or memory figure. Clustering is the expensive part and it is unmeasured.
- Paper 2: reports a client-side encoding latency (134 ms) *but* never measures end-to-end inference latency, energy, or memory on a physical device. The "edge devices" are simulated. Its communication saving (~10.5×) is a cumulative best-case figure with a sensitivity analysis but no full accuracy-vs-compression curve.
- Paper 3: none at all — despite "continuous" authentication implying *frequent, near-real-time* inference on the authenticating device.

#### Evidence beyond your Phase 1

- **arXiv:2607.10914 (SoK)** again: "omission of real-time constraints" as a field-wide pitfall.
- **arXiv:2311.11420** — *LifeLearner: Hardware-Aware Meta Continual Learning for Embedded Platforms* (SenSys 2023). The reference for **how** to do this properly: it reports memory footprint, end-to-end latency and **energy consumption** on two edge devices and a microcontroller, with very large reported savings (memory ×178.7, latency −80.8–94.2%, energy −80.9–94.2%). **Methodology model for your Gap 3 table.**
- **arXiv:2007.13631** — *Memory-Latency-Accuracy Trade-offs for Continual Learning on a RISC-V Extreme-Edge Node*: defines the metric-triple framing (memory, latency, accuracy) explicitly.
- **arXiv:2409.09794** — the Raspberry Pi + Jetson + Flower testbed paper: a ready-made blueprint (hardware list, framework, poisoning tests) if you want to combine Gap 2 and Gap 3.
- **arXiv:2608.26720** reports ~6.5× lower **energy** for a parameter-efficient CL variant — showing energy comparison is now a publishable axis in CL.
- **arXiv:1810.13166** (metrics) already folds latency + memory into CL evaluation; adopting it is a ready-made protocol.

#### What a project on Gap 3 looks like

> "We implement continual-learning IDS inference on representative edge hardware (Raspberry Pi 5 / Jetson Orin Nano) and report accuracy-vs-latency-vs-memory-vs-energy trade-off curves for the methods of Papers 1 and 2, establishing a deployment-aware evaluation protocol."

Work required: buying/borrowing hardware; writing a measurement harness; measuring power (needs a USB power meter or smart plug on a Pi — **the Pi has no built-in power sensor**, unlike a Jetson which exposes `tegrastats`/`jtop`); handling thermal throttling; pinning CPU frequencies; deciding batch size 1 vs batched; choosing an inference runtime (ONNX Runtime, TensorRT, TFLite); and reporting confidence intervals. Note that a lot of this is *systems engineering*, not network security.

#### Pros and cons as a *primary* gap

**Pros:** very practical, examiners like deployment relevance, tangible demo (a Pi on the table is a great viva moment), and the metrics work is reusable for any future project.
**Cons:** **hardware cost** (Pi 5 8 GB ≈ $80 + power meter ≈ $25; Jetson Orin Nano ≈ $250) and availability; **measurement maturity** — energy measurement is easy to do badly (thermal throttling, background processes, no repetitions) and easy to be criticised for; **novelty is methodological rather than scientific** ("we measured things that others didn't"); the most valuable result (accuracy-vs-energy Pareto curves) requires Gap 2's or Gap 1's experiments to exist first; and there is a real risk you spend your semester fighting `apt`, USB cables and throttling instead of doing research.
**Verdict:** **Strong as a supporting contribution, weak as the whole project.** Bolt it on as one table plus one figure: "we additionally report latency and peak memory for the best method, on a Raspberry Pi 5" — that is a week of work and adds a lot of polish for very little risk.

---

### 3.4 A caveat about how I verified novelty

I could not use a general web search in this session (the search backend returned no results), so the novelty counts in §3.2 come from the **arXiv API metadata/abstract search**, which indexes titles, abstracts, authors, comments and journal references — **not full paper text**. Consequences:

- A paper that mentions "poisoning a continual IDS" only in its experiments section may not be counted. So the "1 paper" figure is a *lower bound*, and I have flagged the alternative framing needed anyway.
- arXiv does not index most IEEE/ACM/Elsevier journals. Your three papers are MDPI and are not on arXiv either. **The real literature search must include Google Scholar, Scopus and IEEE Xplore** — which your university library provides.
- **Action for you:** before pitching, run these queries on Google Scholar and IEEE Xplore and record what you find. Reproducible query strings are in Part 5.9.

I have marked the one fact I cited from memory rather than from a fetched source (the Engelen et al. CICIDS2017 critique). **Verify page numbers and exact claims for any reference before it enters your report.**

---

## Part 4 — Choosing your primary gap

### 4.1 The scoring table

Scores: 1 = poor, 5 = excellent. "Weight" reflects what actually decides a final-year grade: feasibility first, novelty second.

| Criterion | Weight | **Gap 1** (modern data) | **Gap 2** (adversarial) | **Gap 3** (deployment/efficiency) |
|---|---|---|---|---|
| Novelty of the knowledge claim | ×3 | 2 | **5** | 3 |
| Feasibility in one semester | ×3 | **5** | 4 | 2 |
| Cost (money) | ×2 | **5** (free) | **5** (free) | 2 (hardware) |
| Data availability | ×2 | **4** (public, messy) | **4** (same) | 3 |
| Skill fit for an AI student | ×2 | 4 | **4** | 2 (systems-heavy) |
| Literature already in hand | ×2 | 4 | **5** (2 of 3 papers) | 3 |
| Examiner appeal / demo value | ×2 | 2 | **5** | 4 |
| Risk of being scooped | ×2 | 2 (high — obvious idea) | 3→**4** if aimed correctly | **5** (underexplored) |
| Risk of producing no result | ×2 | **5** | 3 (attacks may fail → still a result) | 3 |
| **Weighted total** | | **3.5** | **4.4** | **2.8** |

### 4.2 The one-paragraph verdicts

**Gap 1 — the safe road.** You will finish. You will learn the entire pipeline. Your result will be believed. But your contribution will be "new evidence", and you will spend most of your time on data cleaning rather than research. **Use it as the bed, not the headline.**

**Gap 2 — the rewarding road.** You are entering a field that a single Aug-2026 paper just opened. You have two of three papers in hand, and the exact intersection is nearly empty. The intellectual work is in *designing* the threat model and choosing targets nobody has chosen. There is a genuine possibility of a publishable result. The risk is scope creep and a weak threat model — both of which the plan in Part 5 mitigates.

**Gap 3 — the expensive road.** Interesting, practical, and it will eat your semester in hardware logistics for a contribution that is largely about measurement hygiene. **Add it as a bonus table.**

### 4.3 The recommended combination (say this in your proposal)

```
PRIMARY  : Gap 2  — adversarial robustness of the continual-learning
                    adaptation mechanism, aimed at the UNKNOWN-ATTACK
                    DISCOVERY stage (Paper 1) and/or the FEDERATED
                    setting (Paper 2).

CARRIER  : Gap 1  — run everything on CICIDS2017 (+ optionally
                    CICDDoS2019) instead of NSL-KDD, with task
                    sequences derived from real capture days and the
                    CII scenario from arXiv:2608.04602.

BONUS    : Gap 3  — one table of inference latency + peak memory for
                    the best-performing configuration, on one real
                    device (Raspberry Pi 5 or a lab machine).
```

**Why this combination scores well:** the headline is novel; the carrier makes the headline *credible* (modern data, honest splits); the bonus is cheap and shows deployment awareness. All three of your Phase 1 gaps are addressed, but only one is the contribution. This structure is exactly what an examiner wants to see: **one claim, properly supported.**

### 4.4 Decision tree (if you are still unsure)

```
Do you have a Raspberry Pi / Jetson / lab machine available by week 3?
├─ NO  → do not pick Gap 3 as primary.
└─ YES → still prefer Gap 2 primary; use the device for the bonus table.

Do you enjoy writing/simulating defences more than designing experiments?
├─ YES → Gap 2 Option 2-C (defensive).
└─ NO  → Gap 2 Option 2-A or 2-B (offensive).

Is your supervisor oriented toward "practical systems" or "security theory"?
├─ Practical  → lead with the CII + deployment table framing.
└─ Theoretical → lead with the threat model + discovery-stage framing.

Is your tolerance for boring work high?
├─ High  → Gap 1 can be your fallback if Gap 2 stalls.
└─ Low   → never let Gap 1 be the fallback; make the fallback
           "reduce to one attack type on one dataset".
```

### 4.5 Pre-empting the three questions your supervisor will ask

1. *"Isn't this just applying known attacks to a known model?"*
   → No: generic backdoor-on-CL is studied (18 arXiv hits) and single-node IDS buffer poisoning was just published (2608.04602). **The untested object is the open-world discovery pipeline and the federated aggregation of a continual learner** — where the attacker influences *what the model decides to learn*, not merely what it predicts. (§3.2, Option 2-A/2-B.)
2. *"Will you have any result if the attacks fail?"*
   → Yes, and it is a good one: "the discovery stage is robust to X under budget Y" is exactly the assurance the field lacks. Note this commitment in the proposal — examiners reward pre-committed interpretations of failure.
3. *"Why not just use a public dataset as-is?"*
   → Because the SoK (2607.10914) identifies artificial splits and trivial benchmarks as the field's recurring weakness, and because CICIDS2017's defects are documented; we define sequences from real capture days and report the cleaning decisions explicitly. (See Part 5.3.)

---

## Part 5 — The concrete Phase 2 plan

### 5.1 Research question and hypotheses

Write these down verbatim in your proposal. Everything else is execution.

**Primary RQ (Option 2-A — discovery stage):**

> Can an adversary who can influence the traffic stream that a continual-learning IDS learns from cause the novelty-detection-and-clustering stage to either permanently miss real attacks or manufacture spurious attack classes — and can a lightweight buffer/data-integrity defence prevent this without destroying the model's ability to learn new attacks?

**Hypotheses:**

- **H1** An IDS pipeline using replay-based class-incremental learning loses most of its utility (clean accuracy) under label-flipping poisoning of its memory at budgets ≤ 1%, reproducing the single-node finding of arXiv:2608.04602 — establishing that our experimental setup is comparable to published work.
- **H2** Poisoning the *novelty-discovery* stage is **more dangerous per unit of attacker effort** than poisoning the classifier: a small number of crafted "novel" samples can (a) suppress detection of a real attack family permanently, or (b) create a fictitious class that absorbs future benign traffic. Success is measured by *missed detections over the remaining task sequence*, not by a single accuracy number.
- **H3** At least one defence that works against classifier poisoning (small-loss buffer purification, gradient auditing, or frequency filtering) performs **worse** in the continual setting because the drift it must distinguish from poisoning is legitimate — quantifying this "drift vs. poison" confusion is a contribution in itself.

**Fallback interpretation if H2 is rejected:** "the discovery stage is robust to crafted-novelty poisoning at budgets up to X%" is a publishable assurance result, and the paper becomes a robustness characterisation instead of an attack paper. **Decide this now so a negative result cannot derail you.**

### 5.2 The contribution statement (three bullets for your proposal)

1. We define and execute the first adversarial evaluation of an **open-world continual-learning IDS** — attacking the novelty-detection and clustering stage rather than only the classifier.
2. We introduce **[name your attack]** — e.g. *"benign-anchored novelty poisoning"* — a low-budget attack that manipulates what the system discovers to be a new attack class, and we characterise its persistence across the remaining task sequence.
3. We benchmark **three existing defences** (small-loss purification, gradient auditing, frequency-filtering aggregation) in the continual setting and show where they fail, releasing a reproducible evaluation harness on CICIDS2017 with day-based task sequences.

### 5.3 Datasets and the task sequence

**Primary dataset: CICIDS2017** — because (a) it is the dataset the one competing paper uses, so your numbers are comparable; (b) it has a natural **day-based** ordering; (c) it is what the field expects.

CICIDS2017 was captured over five working days, and the attacks are documented per day. That gives you a task sequence that is *real*, not invented:

| Task | Day | Content | Labels introduced |
|---|---|---|---|
| T0 | Monday | Benign only | `Benign` |
| T1 | Tuesday | FTP-Patator, SSH-Patator | 2 brute-force classes |
| T2 | Wednesday | DoS Slowloris, DoS Slowhttptest, DoS Hulk, DoS GoldenEye, Heartbleed | 5 classes |
| T3 | Thursday | Web Attack (Brute Force, XSS, SQL Injection), Infiltration | 4 classes |
| T4 | Friday | Bot, PortScan, DDoS, LOIT (infiltration variant) | 4 classes |

Design decisions you must state and justify:

- **Class-IL or CII?** Adopt **CII** (benign present in every task) and cite arXiv:2608.04602 — it is more realistic and connects you to the newest work. Report the classic class-IL setting as an ablation.
- **Cleaning protocol:** drop duplicate rows, drop rows with `inf`/`NaN` (CICIDS2017 has these in rate features), fix inconsistent label strings (whitespace/case variants appear in the raw CSVs), and report how many rows you removed per class. **Publish this table in your report — it is a credibility marker.**
- **Class imbalance:** attack classes are tiny compared to benign. Either subsample benign or use class-weighted loss; state which, because it changes results dramatically. (Note also that Paper 2's use of **SMOTE on attack classes** is questionable — synthesising fake attack traffic may not be physically meaningful. Making that point in your report shows critical thinking.)
- **Validation dataset (Gap 1's carrier, if time allows):** CICDDoS2019 for the DDoS family — which also directly answers Paper 1's own complaint that "real attacks are DDoS, not DoS". CICIoT2023 if you want the IoT angle (33 attacks, 7 categories, 105 devices).
- **Never mix datasets for training and testing** and never let flows from the same capture appear in both — that is the classic leakage that makes IDS papers look good and be wrong.

### 5.4 Baselines (all must be run by you, on your sequence)

| # | Baseline | Family | Why it is in the table |
|---|---|---|---|
| 1 | **Sequential fine-tuning** | none | The lower bound. Shows forgetting in its purest form |
| 2 | **EWC** | regularisation | Universal CL baseline |
| 3 | **LwF** | regularisation/distillation | Used in Papers 1 and 3; no data storage |
| 4 | **Experience Replay (ER)** | replay | Simplest replay; used in Paper 3 |
| 5 | **DER++** | replay | Strong simple baseline; report if time allows |
| 6 | **Joint / Oracle** | upper bound | Trained on all data at once. **Always report** |
| 7 | **[Your defended variant]** | — | Baseline + your defence |

Optional if you take Option 2-B: add **FedAvg** and **FedProx**, plus a robust aggregation rule (**Krum**, **Trimmed Mean** or **FreqFed**) as baselines.

**Software:** do not write trainers from scratch unless you must. Use **Avalanche** (`avalanche-lib`, Lomonaco et al., arXiv:2104.00405) or **Mammoth** (github.com/aimagelab/mammoth) — both implement EWC/LwF/ER/DER++/iCaRL and both are accepted in the literature. Use **Flower** (flower.dev) for federated simulations; the testbed paper arXiv:2409.09794 uses exactly this stack on Pi/Jetson.

### 5.5 Your threat model (fill in the blanks — this is the hardest part for beginners)

A threat model is six answers. Write them as a table in your proposal; you cannot be criticised for a clearly stated threat model, only for a vague one.

| Question | Your answer (pick and justify) |
|---|---|
| **What is the adversary's goal?** | Availability (make the IDS stop detecting a real attack family) / Integrity (make the IDS detect a fake class; or make attack traffic look benign) / Both |
| **What can the adversary control?** | (a) A fraction ρ of *labelled training samples* entering the stream (poisoner); (b) a fraction of *federated clients* (Byzantine); (c) the *traffic* itself (evader, for trigger design); state exactly which |
| **How much can they control?** | Budget ρ ∈ {0.5%, 1%, 5%} of samples, or k clients out of N; state the unit — flows, clients, or tasks |
| **What does the adversary know?** | White-box (knows architecture and defence) vs black-box (only API/observations). **Default to white-box for attacks, black-box for defence evaluation** — that is the conservative, accepted choice |
| **When can they act?** | Once at the start (static poison) vs every task (persistent). **Persistent is the interesting case in CL** — it is what makes CL different from static poisoning |
| **What are they assumed NOT to do?** | Usually: cannot modify the server, cannot alter the aggregation algorithm, cannot change the benign traffic statistics. State it explicitly |

**The single best sentence you can put in your report:** *"We assume a white-box, persistent, low-budget poisoner who cannot influence the server, and we evaluate whether defences that succeed in the static setting succeed when the data distribution is itself drifting."*

### 5.6 Attack implementations on tabular flow data (the practical bit)

Backdoors on images use a small pixel patch. A network flow is a row of ~78 numbers, so "a trigger" needs thought. Three levels of realism — **pick the one you can defend**:

1. **Feature-space trigger (easiest, weakest realism).** Choose a feature combination unlikely to occur naturally (e.g. `dst_port = 6666` **and** `TCP flags = 0x02` **and** `fwd_pkt_len_mean > 800`). At poison time, apply it to attack samples and relabel them benign. At test time, apply it to otherwise-malicious flows and measure ASR. Cheap, fast, standard in tabular backdoor work. **Weakness:** an examiner will ask whether such a flow can exist. Answer: yes if the attacker chooses a payload that produces it — but you must argue this, ideally by showing the trigger's flow statistics are reachable.
2. **Physically grounded trigger (recommended).** Derive the trigger from a real traffic characteristic you can actually generate — e.g. a specific packet-size sequence, an unusual but legal TCP flag combination, or a specific inter-arrival-time pattern that you can reproduce with a traffic generator (Scapy/hping3). This is much more defensible: "an attacker can send this traffic" is trivially true. It costs an extra week.
3. **Novelty-poisoning trigger (for Option 2-A).** No trigger at all — instead, the attacker sends traffic *designed to be flagged as novel* by the autoencoder (e.g. samples that maximise reconstruction error), then lets the pipeline cluster and learn them. This is the attack most specific to your project and the most novel. Implementation: take benign samples, perturb them to maximise reconstruction error, submit them as "unknown attack" traffic. Measure whether the resulting fictitious class (a) captures future benign traffic (→ false alarms) or (b) absorbs a real attack family (→ missed detections).

**Label flipping** needs no trigger: just flip the class labels of ρ of the samples for a chosen class (e.g. relabel `DoS Hulk` as `Benign`). Report both random flipping and *targeted* flipping (only one class), because targeted is far more damaging and more realistic.

**Byzantine/model poisoning (Option 2-B):** implement (a) sign-flip, (b) update scaling ("little is enough", Baruch et al.), and (c) model replacement with a backdoored local model (Bagdasaryan et al.). Measure the fraction of malformed clients that breaks the global model, and whether the compression in EdgeFedCIL (low-rank + quantisation) attenuates or masks the attack. **That last question is a genuine, unasked research question and a great paragraph in your report.**

### 5.7 Experiment matrix (your whole semester, as a table)

| ID | Experiment | Attacks | Budgets | Baselines | Question answered |
|---|---|---|---|---|---|
| **E1** | Clean protocol reproduction | none | — | 1–6 | Does your setup reproduce published behaviour? (validates H1's premise) |
| **E2** | Label-flip the buffer/stream | random + targeted | 0.5 / 1 / 5% | 1–4 | H1 |
| **E3** | Backdoor (feature + physical trigger) | static vs persistent | 1 / 5% | 1–4 | Persistence of the trigger across tasks |
| **E4** | Novelty-poisoning of the discovery stage | suppression + fake-class | 0.5 / 1 / 5% | 1–4 | **H2 (your headline)** |
| **E5** | Evasion of the novelty detector | crafted-novel benign | — | 1, 4 | Can the attacker prevent discovery at all? |
| **E6** | Defences | best attack from E2–E4 | fixed | + purification, + auditing, + freq-filter | H3 |
| **E7** | *(bonus, Gap 3)* Deployment cost | clean | — | 4, 6 | Latency (ms, batch 1), peak RSS, params, FLOPs on one real device |
| **A1** | Ablation: buffer size | best attack | fixed | 4 | Does a bigger buffer help or hurt the attacker? |
| **A2** | Ablation: class-IL vs CII | best attack | fixed | 4 | Is CII harder for the attacker? |
| **A3** | Ablation: task order | best attack | fixed | 4 | Order sensitivity (report ≥ 3 orders) |

That is 7 experiments plus 3 ablations. **Cut to E1–E4 + E6 if time is short.** Cutting order, if you must: A3 → A2 → E7 → E5 → E3.

### 5.8 Evaluation protocol and statistical honesty

1. **Report the full task-accuracy matrix** for every experiment. Period.
2. **Report ACC, BWT, FWT and Forgetting** — cite arXiv:1810.13166 for the definitions.
3. **For Gap 2, always report clean accuracy *and* ASR together.** A backdoor with 0.97 clean accuracy and 95% ASR is *worse* than a model that dropped to 0.80 accuracy, because nobody notices it. Make that argument in your discussion — it is your most quotable insight.
4. **Three seeds minimum**, mean ± standard deviation, and a paired test (Wilcoxon signed-rank) for your method vs each baseline. No p-values on single runs.
5. **Fix and report everything:** buffer size (e.g. 500 or 1000 samples — huge buffers are unrealistic), number of epochs per task, learning rate, batch size, optimiser, and whether you tuned hyperparameters on a validation split of the *current* task only (you must, otherwise you leak future data — a subtle and common error).
6. **Repeat the task sequence with at least two different orderings**, because CL results are notoriously order-sensitive.
7. **Report compute:** GPU hours, wall-clock training time. Cheap credibility.

### 5.9 Literal query strings to run (document your search)

Run these on **Google Scholar**, **IEEE Xplore**, **Scopus** and the **arXiv API** (http://export.arxiv.org/api/query?search_query=...). Paste the results table into your report appendix — showing your search protocol is a Phase-2-grade move.

```
"continual learning" AND "intrusion detection"
"class-incremental" AND ("IDS" OR "intrusion detection")
"continual learning" AND ("poisoning" OR "backdoor" OR "adversarial")
("novelty detection" OR "open-world" OR "unknown attack") AND "poisoning"
"federated" AND "continual learning" AND "poisoning"
"replay buffer" AND ("poisoning" OR "backdoor" OR "manipulation")
"concept drift" AND ("adversarial" OR "poisoning") AND "intrusion detection"
"CICIDS2017" AND ("limitations" OR "pitfalls" OR "data quality")
```

Record, for each: date run, database, number of hits, and how many you judged relevant. This is your reproducible novelty claim.

### 5.10 Deliverables and a 12-week timeline

Adjust to your actual semester length. Assumes two students working part-time.

| Week | Deliverable | Notes |
|---|---|---|
| 1 | **Proposal finalised** — RQ, hypotheses, threat model, experiment matrix (Parts 5.1–5.7 of this document, rewritten in your own words) | Get supervisor sign-off **before** coding |
| 1 | Search protocol table (§5.9) + 10 new references integrated into the gap table | Cheap, high value |
| 2 | **Repo stood up**: data loader, cleaning script, task-sequence builder, metric functions, logging | No models yet |
| 3 | **E1** — one baseline (ER) end-to-end; task-accuracy matrix + BWT printed correctly | Prove the harness on a *known* result first |
| 4 | Baselines 1–6 complete; `results/baseline_table.csv` | This is when you know your plumbing is right |
| 5 | **E2** — label flipping at 3 budgets; first real result | Reproduces published behaviour (H1) |
| 6 | **E3** — backdoor with feature trigger; trigger-realism discussion written | |
| 7 | **E4** — novelty poisoning (**headline**). Start with suppression, then fake-class | Budget 2 weeks mentally; this is the risky one |
| 8 | **E5 + E6** — evasion and defences | |
| 9 | **A1–A3** ablations; **E7** bonus table on real hardware | |
| 10 | Statistics: 3 seeds, mean±std, Wilcoxon; regenerate all figures | |
| 11 | **Write-up**: report/the paper. Reuse Phase 1's three-paper summaries as related work | |
| 12 | Buffer week: reproducibility run on a clean checkout, code release, final polish | Always keep this week |

**Division of labour between Saneedullah and Ahmed Bilal** (team of two): one owns *data + protocol + baselines* (E1, E2, E7, statistics), the other owns *attack implementation + defence* (E3, E4, E5, E6). Both write. **Do not split by "one codes, one writes"** — examiners spot it instantly.

### 5.11 Threats to validity (write this section; it earns marks)

- **Construct validity:** CICIDS2017 is itself criticised; our attack success does not automatically transfer to production traffic.
- **Internal validity:** single dataset, three seeds; task-order sensitivity; hyperparameters may favour one method.
- **External validity:** no real federated deployment; no real attacker traffic (we simulate).
- **Ethical:** all work is offline on public data with no live systems targeted.

---

## Part 6 — Tools, datasets and your development environment

### 6.1 Environment

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install numpy pandas scikit-learn matplotlib seaborn torch torchvision
pip install avalanche-lib          # or clone github.com/aimagelab/mammoth
pip install flwr                    # Flower, optional (federated)
pip install codecarbon              # energy measurement, optional (Gap 3)
```

**Compute:** a laptop CPU is genuinely enough for the models involved; a free Kaggle Notebook (30 GPU-hours/week) or Colab T4 makes E4–E6 faster. You do not need an institutional cluster. **Do not let compute become an excuse** — the bottleneck in this project is protocol design, not FLOPs.

### 6.2 Dataset sources

| Dataset | Link | Size / notes |
|---|---|---|
| **CICIDS2017** | https://www.unb.ca/cic/datasets/ids-2017.html (also mirrored at cicresearch.ca and Kaggle) | ~2.8M flows, 8 CSVs (one per day/attack), ~78 features. Your primary |
| **CICDDoS2019** | https://www.unb.ca/cic/datasets/ddos-2019.html | 12+ DDoS types; training/testing CSVs; very large — subsample |
| **CICIoT2023** | https://www.unb.ca/cic/datasets/iotdataset-2023.html | 33 attacks, 7 categories, 105 devices |
| **NSL-KDD** | https://www.unb.ca/cic/datasets/nsl.html | Only for reproducing Paper 1 exactly |
| **UNSW-NB15** | https://research.unsw.edu.au/projects/unsw-nb15-dataset | Widely used modern-ish alternative |
| **ToN-IoT** | https://research.unsw.edu.au/projects/toniot-datasets | Paper 2's dataset |
| **X-IIOTID** | IEEE DataPort (search "X-IIOTID") | Paper 2's second dataset |
| **N-BaIoT** | UCI ML Repository (search "N-BaIoT") | IoT botnet; used by SecureDyn-FL |

⚠️ Download links and mirrors change; verify each before citing. Some CIC files are large (hundreds of MB to GB) — start downloads on day 1, not week 5.

### 6.3 A repo layout that will not embarrass you

```
cl-ids-adversarial/
├── README.md                 # what/how to reproduce, in 1 page
├── requirements.txt
├── data/
│   ├── raw/                  # gitignored
│   └── processed/
├── src/
│   ├── data/clean.py         # dedup, inf/NaN, label normalisation
│   ├── data/sequence.py      # builds the day-based task sequence
│   ├── attacks/flip.py       # label flipping
│   ├── attacks/backdoor.py   # trigger injection
│   ├── attacks/novelty.py    # novelty poisoning (your contribution)
│   ├── models/               # encoder + heads
│   ├── cl/                   # EWC, LwF, ER, DER++ (or Avalanche wrappers)
│   ├── defenses/             # purification, auditing, aggregation
│   ├── metrics.py            # ACC, BWT, FWT, F, ASR
│   └── run_experiment.py     # config-driven: python run_experiment.py --config e4.yaml
├── configs/                  # one YAML per experiment (E1..E7, A1..A3)
├── results/                  # CSV + figures, committed (small)
└── paper/ or report/
```

**Rule:** every number in your report must be regenerated by `python run_experiment.py --config <file>`. If you cannot reproduce your own table in week 12, you will not be able to write it up.

---

## Part 7 — Annotated reading list

Grouped by why you need it. IDs are arXiv (verify before citing; journal versions exist for several).

**A. Must read before writing the proposal (your closest neighbours)**

1. **arXiv:2608.04602** — CL-IDS with replay on CICIDS2017; introduces CII; **poisons its own replay buffer** with label flipping (collapse at 1%) and a backdoor (0.97 clean accuracy, 95% ASR). *Your competitor, your motivation, your comparison point.*
2. **arXiv:2409.13864** — *Persistent Backdoor Attacks in Continual Learning* (USENIX Security 2025): Blind/Latent Task Backdoor; evades SentiNet and I-BAU. *Proof that CL is specifically vulnerable because it remembers.*
3. **arXiv:2609.06346** — CLUBA: CL under backdoor attack + a purification/recovery defence. *Your defence baseline and evidence the defence side is newly open.*
4. **arXiv:2607.10914** — SoK: FL for IDS (vehicular). *The "recurring pitfalls" list justifies gaps 1, 2 and 3 at once.*
5. **arXiv:2602.13062** — Backdoors on contrastive CL for IoT: replay *reinforces* embedding-level attacks. *Closest to your network-security setting.*

**B. Foundations of continual learning (skim, cite, don't re-derive)**

6. **arXiv:1810.13166** — Díaz-Rodríguez et al., CL metrics (ACC/BWT/FWT + memory + compute, fused score). *Define your metrics from here.*
7. **arXiv:2104.00405** — Avalanche library (Lomonaco et al.). *Your tooling reference.*
8. **arXiv:2202.00275** — *Architecture Matters in Continual Learning*. *Cite when explaining your architecture choices.*
9. Kirkpatrick et al., PNAS 2017 — EWC. ([arXiv:1612.00796](https://arxiv.org/abs/1612.00796))
10. Li & Houlsby 2017 — LwF. ([arXiv:1606.09282](https://arxiv.org/abs/1606.09282))
11. Rebuffi et al. 2017 — iCaRL. ([arXiv:1611.07725](https://arxiv.org/abs/1611.07725))
12. Buzzega et al., NeurIPS 2020 — DER++. ([arXiv:2004.07211](https://arxiv.org/abs/2004.07211))
13. Rolnick et al. 2019 — Experience Replay. ([arXiv:1811.11682](https://arxiv.org/abs/1811.11682))
14. Lopez-Paz & Ranzato 2017 — GEM. ([arXiv:1706.08840](https://arxiv.org/abs/1706.08840))

**C. Continual learning for intrusion detection (your field)**

15. **arXiv:2603.00363** — *Quantifying Catastrophic Forgetting in IoT IDS* (Feb 2026): domain-IL, 48 domains, 5 methods; Replay best overall, SI near-zero forgetting. *Best single citation for "CL is necessary and which methods work".*
16. **arXiv:2412.16264** — SSF: strategic selection + forgetting for IDS with concept drift (INFOCOM 2025). *State of the art, on NSL-KDD/UNSW-NB15.*
17. **arXiv:2412.00911** — SOUL: semi-supervised open-world CL for IDS; **the 0.985 → 0.506 decay number**. *Use in your introduction.*
18. **arXiv:2601.21318** — QCL-IDS: quantum CL with generative replay (3-stage stream, UNSW-NB15 + CICIDS2017). *Shows the range of active variants; cite as recent momentum.*
19. **arXiv:2506.19877** — ML models on CICIDS2017, known vs unseen attacks. *Evidence that supervised IDS collapses on novel attacks.*

**D. Adversarial ML for network security**

20. **arXiv:2409.18736** — *Adversarial Challenges in NIDS* (survey). *Your "structured data is under-explored" citation.*
21. **arXiv:2409.09794** — FL poisoning testbed on Raspberry Pi/Jetson with Flower. *Gap 3 blueprint + FL vulnerability evidence.*
22. **arXiv:2601.06466** — SecureDyn-FL (IEEE TNSM): gradient-auditing poisoning detection, up to 50% malicious clients. *Defence baseline.*
23. **arXiv:2312.04432** — FreqFed (NDSS 2024): frequency-domain filtering, evaluated on IoT intrusion detection. *Defence baseline.*
24. Baruch et al. 2019 — *A Little Is Enough: Circumventing Defenses for Distributed Learning*. *The Byzantine attack you should implement.*

**E. Data, datasets and evaluation honesty**

25. **arXiv:2009.07352** — Taxonomy of 8 NIDS dataset challenges; "sandbox datasets" critique. *Gap 1 backbone.*
26. Engelen et al., *Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study*, IEEE SPW 2021. ⚠️ *Cited from domain knowledge, not fetched — verify before use.*
27. **arXiv:2604.06972** *(if you use industrial metrics)* / **arXiv:2404.06972** — *Toward industrial use of continual learning: new metrics for CIL*. *Alternative metric framing for Gap 3.*

**F. Deployment cost (Gap 3 bonus only)**

28. **arXiv:2311.11420** — LifeLearner (SenSys 2023): memory/latency/energy on real edge devices + MCU. *Measurement methodology.*
29. **arXiv:2007.13631** — Memory-latency-accuracy trade-offs for CL on a RISC-V extreme-edge node.
30. **arXiv:2608.26720** — 6.5× lower energy with parameter-efficient CL. *Shows energy is now a publishable axis.*

---

## Part 8 — Glossary

| Term | Definition |
|---|---|
| **ACC / AA** | Average accuracy across all tasks after the full sequence |
| **Ablation** | Removing one component to prove it matters |
| **ASR** | Attack Success Rate — fraction of triggered inputs the attacker successfully misroutes |
| **Benign** | Normal (non-attack) traffic |
| **BWT** | Backward Transfer — average change in old-task accuracy after learning new tasks (negative = forgetting) |
| **Buffer / memory** | Stored old samples used for replay |
| **Catastrophic forgetting** | Loss of previously learned knowledge when training on new data |
| **CII** | Class-Instance Incremental — benign traffic reappears in every task |
| **Class-IL** | Class-incremental learning — new classes over time, no task ID at test time |
| **Concept drift** | The data distribution changes over time |
| **CIL** | Class-Incremental Learning |
| **CL** | Continual Learning |
| **DER++** | Dark Experience Replay — replay old logits as well as labels |
| **Dirichlet(α) partition** | Standard way to split one dataset unevenly across federated clients; smaller α = more heterogeneous |
| **Domain-IL** | Same classes, shifting distribution |
| **EER** | Equal Error Rate — where false-accept = false-reject; used in authentication |
| **Epoch** | One pass over the training data |
| **ER** | Experience Replay |
| **EWC** | Elastic Weight Consolidation — weight-importance regularisation |
| **FCL** | Federated Continual Learning |
| **FedAvg / FedProx** | Standard federated aggregation algorithms |
| **Flow** | One conversation between two network endpoints, summarised as a feature vector |
| **FWT** | Forward Transfer — benefit of past learning for new tasks |
| **HDBSCAN** | Density-based clustering that infers the number of clusters; used by Paper 1 for attack discovery |
| **iCaRL** | Incremental Classifier and Representation Learning |
| **Joint / Oracle** | Baseline trained on all tasks' data at once — the upper bound |
| **Krum / Trimmed Mean** | Byzantine-robust aggregation rules |
| **LwF** | Learning without Forgetting — distillation from the previous model |
| **Non-IID** | Clients' local data distributions differ |
| **Open-world / novelty detection** | Detecting and learning inputs belonging to no known class |
| **Plasticity** | Ability to learn new tasks (vs stability) |
| **Poisoning** | Attacker corrupts training data or model updates |
| **Replay** | Training on a mix of new data and stored old data |
| **Seed** | Random seed; run ≥3 to get error bars |
| **SI** | Synaptic Intelligence — online importance weights |
| **SOTA** | State of the art |
| **Stability** | Ability to retain old knowledge (vs plasticity) |
| **Task sequence** | The ordered list of tasks/chunks the model learns |
| **Task-accuracy matrix** | T×T table of accuracy on task j after task i |
| **Threat model** | Explicit statement of attacker goals, capabilities, knowledge and timing |
| **Trigger** | Pattern planted by a backdoor attack that flips the model's output |

---

## Part 9 — Supervisor Q&A

Rehearse these out loud. Each answer should be under 30 seconds.

**Q: Why is this not just "re-running known attacks"?**
A: Because 15 papers combine continual learning with intrusion detection, and only **one** combines continual learning, adversarial evaluation and intrusion detection (arXiv:2608.04602), and that one attacks a single-node replay buffer. The *open-world discovery* stage and *federated* continual aggregation are untested. We also test whether defences that work in the static setting survive when the data distribution is itself drifting — that confusion has not been measured.

**Q: What if your attacks don't work?**
A: Then we publish a robustness characterisation: "the discovery stage resisted crafted-novelty poisoning at budgets up to X%." That is a positive assurance result for a mechanism currently deployed without any such guarantee, and the paper becomes a defence-relevant evaluation.

**Q: Isn't CICIDS2017 itself flawed?**
A: Yes — it has documented duplication, unidirectional flow artefacts and inf/NaN features, which is exactly why we (a) report our cleaning protocol and removed-row counts, (b) derive task sequences from real capture days, and (c) frame any conclusion as dataset-conditional. Using a flawed benchmark honestly is better than using a legacy one uncritically, which is the criticism we are raising against NSL-KDD.

**Q: Is this ethical?**
A: All experiments are offline, on public datasets, on models we train ourselves. We do not attack live systems. We follow the standard practice of publishing attacks so defences can be built, and we will disclose our attack code with the paper.

**Q: Do you need a GPU cluster?**
A: No. Tabular IDS models are small; free Kaggle/Colab GPU hours are sufficient, and the protocol design — not compute — is the bottleneck.

**Q: What if the supervisor prefers Gap 1 or Gap 3?**
A: We will run the same threat-model experiments on the modern carrier datasets (that *is* Gap 1's fix), and add the deployment-cost table (Gap 3) as a bonus. Only the ordering of contributions changes, not the work.

---

## Part 10 — This week's checklist

Do these in order. Nothing here requires a decision you haven't already been given.

- [ ] **1.** Read arXiv:2608.04602 in full (2–3 hours). It is the closest paper to your project and it decides your framing. Note its threats to validity — you will need them.
- [ ] **2.** Read arXiv:2409.13864 (persistent backdoors in CL) — at least the method and threats sections. This is where your threat model comes from.
- [ ] **3.** Run the eight query strings in §5.9 on Google Scholar and IEEE Xplore. Record hits and dates. Save the table.
- [ ] **4.** Download CICIDS2017 **today** and start the cleaning script. Datasets are slow; do not let this block week 2.
- [ ] **5.** Build the day-based task sequence (Monday → Friday) and print the class counts per task. If the counts look absurd, you have found your first real problem early.
- [ ] **6.** Install Avalanche or Mammoth and get **one** baseline (ER) training on your sequence, printing a task-accuracy matrix. Do not move on until this works.
- [ ] **7.** Fill in the **threat-model table (§5.5)** with your supervisor in a single meeting. This is the one thing you cannot do alone, and the single most important hour of Phase 2.
- [ ] **8.** Rewrite Parts 5.1–5.7 of this document in your own words as the Phase 2 proposal. If you cannot explain a sentence without looking at this file, you do not yet own it.
- [ ] **9.** Decide the two-role split (data/protocol/baselines vs attacks/defences) and write it into the proposal.
- [ ] **10.** Commit the repo skeleton (Part 6.3) and create `results/` with a placeholder table. Momentum matters.

**The one thing to remember:** Phase 2 succeeds when you can say, in one sentence, what you will show that nobody has shown. Yours is:

> *"Nobody has tested whether an attacker can manipulate what a continual-learning intrusion detection system decides to learn — only what it predicts — and we will show whether the defences we currently trust survive in that setting."*

Everything else in this document exists to make that sentence true.
