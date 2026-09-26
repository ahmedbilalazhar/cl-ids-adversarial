# Threat Model — Gap 2 / Option 2-A (Discovery Stage)

**Status:** to be confirmed with supervisor in a single meeting (Part 10 checklist item 7).  
**Framing sentence for the report:**

> We assume a white-box, persistent, low-budget poisoner who cannot influence the server, and we evaluate whether defences that succeed in the static setting succeed when the data distribution is itself drifting.

---

## Six answers

| # | Question | Answer |
|---|----------|--------|
| 1 | **What is the adversary's goal?** | **Availability:** make the IDS permanently miss a real attack family. **Integrity:** make the IDS detect a fictitious class, or make attack traffic look benign. Both are in scope; primary metric differs (missed detections vs. false-alarm absorption). |
| 2 | **What can the adversary control?** | A fraction ρ of *labelled training samples* entering the stream (stream poisoner). Secondary (only if Option 2-B activated): a fraction of *federated clients*. Tertiary: the *traffic itself* for trigger design (evader). **Primary setting: stream poisoner only.** |
| 3 | **How much can they control?** | Budget ρ ∈ {0.5%, 1%, 5%} of samples per task. Unit = flows (not bytes, not clients). Targeted (single-class) and random flipping both tested; targeted is the realistic threat. |
| 4 | **What does the adversary know?** | **White-box** for attack design (knows architecture, autoencoder threshold, defence). **Black-box** for defence evaluation (defence does not get to see the attack code) — conservative, accepted default. |
| 5 | **When can they act?** | **Persistent** — at every task in the sequence. Persistent is the interesting case in CL; it is what makes CL different from static poisoning. One-shot (static) reported as a comparison row only. |
| 6 | **What are they assumed NOT to do?** | Cannot modify the server; cannot alter the aggregation algorithm; cannot change global benign traffic statistics; cannot read the model's private replay buffer directly (must go through the training stream); cannot physically destroy hardware. |

---

## Attack classes mapped to pipeline stages

| Attack | Stage targeted | Concrete action | Metric |
|--------|----------------|-----------------|--------|
| Label flipping | Replay buffer / training stream | Relabel ρ of stored flows (random or targeted: `DoS Hulk` → `Benign`) | Clean ACC collapse; BWT |
| Backdoor / trigger | Buffer / classifier | Plant feature-space or physically-grounded trigger; attack flows carrying trigger → benign | ASR + clean ACC (stealth) |
| **Novelty poisoning (headline)** | **Autoencoder → HDBSCAN discovery** | Craft "novel" samples (max reconstruction error) that the pipeline flags as unknown; let clustering absorb them | Missed detections over remaining sequence; fictitious-class false alarms |
| Evasion of novelty detector | Autoencoder | Craft attack traffic the AE does *not* flag as novel → never discovered | Undetected real attacks |
| Byzantine update (Option 2-B) | Federated aggregation | Sign-flip, little-is-enough, model replacement | Global model ACC / ASR |

---

## Why this is not already done

- **arXiv:2608.04602** (Aug 2026) does single-node *replay-buffer* poisoning (label-flip + backdoor) on CICIDS2017 — **taken; do not pitch as sole claim.**
- Generic backdoor-on-continual-learning is well studied (vision, prompt-based, contrastive-IoT).
- **Open-world discovery pipeline (autoencoder + clustering) has no published adversarial evaluation** found in arXiv metadata/abstract search (see `docs/search_protocol.md`).
- Federated continual IDS poisoning exists in adjacent work (GFCL, TrustFCL, etc.) but the specific "does compression help/hurt the attacker" question in EdgeFedCIL is unasked.

**Threatening recent literature to cite and distinguish from (do not ignore):**

| ID | Why it threatens | How we distinguish |
|----|------------------|--------------------|
| arXiv:2606.14987 (Jun 2026) | Continual backdoor training in IoT/CPS on CIC-IDS-2018 | Targets SI-regularised anomaly detector, not an open-world discovery pipeline; we attack *what gets discovered* |
| Pawlak et al., PMLR v330 (Aug 2026) | Single-task poisoning in exemplar-free CL | Exemplar-free (no buffer); image-domain; not discovery-stage |
| arXiv:2205.11736 | Defense against federated backdoor under continuous training | Federated backdoor leakage, not discovery-stage; we are single-node primary |
| METANOIA arXiv:2501.00438 | Avoids learning malicious behaviours in incremental IDS | Provenance/graph PIDS, not flow-feature autoencoder+clustering discovery |

---

## Budget and units (must be stated identically in every experiment)

- ρ is a fraction of the **training samples entering the stream for the current task**, not a fraction of the global dataset and not a fraction of the buffer (unless the experiment is explicitly about buffer corruption — E2 label-flip of buffer).
- For H1 reproduction against arXiv:2608.04602: state clearly whether budget is "% of buffer poisoned" or "% of stream poisoned"; the published 0.0053 collapse figure is tied to their buffer-poisoning setup at p = 1%.
