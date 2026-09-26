# Threat Model — Federated Poisoning (Primary) + Discovery-Stage (Secondary, Separated)

**Status:** locked 2026-09-26 for the Computers & Security submission track.
**Framing sentence for the paper:**

> We assume a white-box, persistent, low-budget adversary who controls a
> minority of federated clients (data poisoning and Byzantine update attacks)
> but cannot influence the server or the aggregation rule, and we evaluate
> whether continual-learning IDS methods and defences that succeed in the
> static or single-node setting still hold when the data distribution is
> itself drifting and the model is aggregated across mutually untrusted
> clients. A second, clearly separated threat model covers poisoning of the
> novelty-discovery stage (Paper 1's domain), explicitly NOT drift-spoofing
> against a fixed-identity re-authentication system (Paper 3's domain).

---

## Six answers — PRIMARY (federated poisoning + Byzantine)

| # | Question | Answer |
|---|----------|--------|
| 1 | **What is the adversary's goal?** | **Availability:** make the global IDS permanently miss a real attack family (elevated forgetting / suppressed recall). **Integrity:** make attack traffic look benign (targeted flips, backdoor trigger → benign) or degrade the shared model (Byzantine). Primary metric differs per attack (missed detections vs. ASR vs. global ACC). |
| 2 | **What can the adversary control?** | (a) The local training shard of a minority of federated clients (label flips, backdoor implants in local data); (b) the *updates* those clients submit — sign-flip, "little is enough" scaling (Baruch et al.), model replacement (Bagdasaryan et al.); (c) the traffic itself for trigger design (evader). **All of (a)–(c) are in scope; (a)+(b) are primary.** |
| 3 | **How much can they control?** | Stream budgets ρ ∈ {0.5%, 1%, 5%} of samples per task (unit = flows); federated shard budgets swept from 0% PAST 10% to a characterised breaking point × malicious fractions 1/5, 2/5 and higher (Phase 3). Persistent multi-task arm: each task's own majority attack class flipped. |
| 4 | **What does the adversary know?** | **White-box** for attack design (architecture, CL method, AE threshold, defence). **Black-box** for defence evaluation (defence never sees attack code) — conservative, accepted default. **Adaptive:** every defence in the paper faces an attack crafted specifically to evade it (e.g. loss-preserving flips vs small-loss filtering). |
| 5 | **When can they act?** | **Persistent** — at every task in the sequence. Persistent is the interesting case in CL; it is what makes CL different from static poisoning. One-shot reported as a comparison row only. |
| 6 | **What are they assumed NOT to do?** | Cannot modify the server; cannot alter the aggregation algorithm; cannot change global benign traffic statistics; cannot read any client's private replay buffer directly (must go through the training stream); cannot physically destroy hardware. |

---

## SECONDARY (discovery-stage — related but distinct)

Tests evasion/manipulation of unknown-class DISCOVERY (Paper 1's domain: AE
novelty → HDBSCAN clustering deciding *which traffic deserves a new class*),
NOT spoofing drift against a FIXED re-authenticated identity set (Paper 3's
RF-fingerprint domain). The paper frames it as a secondary, clearly-separated
result. Locked findings (n=7): threshold-suppression unreachable by design
(miss rate invariant); anchor poison absorbs ~12–14% of novel attacks into
fictitious clusters (nopois: 0); nopois control has 0 fictitious clusters.

---

## Attack classes mapped to pipeline stages

| Attack | Stage targeted | Concrete action | Metric |
|--------|----------------|-----------------|--------|
| Label flipping (stream/buffer) | Replay buffer / training stream | Relabel ρ of flows (random or targeted: `DoS Hulk` → `Benign`) | Clean ACC + BWT |
| Backdoor / trigger | Buffer / classifier | Feature-space trigger now; physically-grounded Scapy/hping3 trigger as realism comparison (Phase 3) | ASR + clean ACC (stealth) |
| Byzantine update | Federated aggregation | Sign-flip, little-is-enough scaling, model replacement via malicious clients | Global ACC / ASR |
| Adaptive evasion per defence | Defence layer | Loss-preserving flips (vs small-loss), mimicry updates (vs robust aggregators), trigger variants (vs kNN) | Defence-held-or-broken |
| **Novelty poisoning (secondary)** | **Autoencoder → HDBSCAN discovery** | Craft "novel" samples (max reconstruction error / attack-anchored); let clustering absorb them | Missed detections; fictitious-class false alarms |
| Evasion of novelty detector | Autoencoder | Craft attack traffic the AE does *not* flag → never discovered | Undetected real attacks |

---

## Why this is not already done

- **arXiv:2608.04602** (Aug 2026) does single-node *replay-buffer* poisoning (label-flip + backdoor) on CICIDS2017 — **taken; do not pitch as sole claim.**
- **Lavaur et al., Comput. Secur. 2025, 156:104462** does systematic label-flip × federated IDS — **taken for static FL; our gap is the continual dimension** (federated × class-incremental × CL-method comparison under poisoning). Cite and distinguish.
- Generic backdoor-on-continual-learning is well studied (vision, prompt-based, contrastive-IoT).
- **Open-world discovery pipeline (autoencoder + clustering) has no published adversarial evaluation** found in arXiv metadata/abstract search (see `docs/search_protocol.md`); full protocol-specified re-search in Phase 1.
- Federated continual IDS without adversaries exists (EdgeFedCIL/Wu et al. 2026 — honest server/clients explicitly assumed, §3.1; Mao et al. 2024; Fed-CLIDS 2025); poisoning × FCIL-IDS intersection is the gap.

**Threatening recent literature to cite and distinguish from (do not ignore):**

| ID | Why it threatens | How we distinguish |
|----|------------------|--------------------|
| Lavaur et al., C&S 2025 | Label-flip × FL IDS systematic study | Static FL, no continual learning; we add the CIL × method-comparison dimension |
| arXiv:2606.14987 (Jun 2026) | Continual backdoor training in IoT/CPS on CIC-IDS-2018 | Targets SI-regularised anomaly detector, not an open-world discovery pipeline or federated CIL comparison |
| Pawlak et al., PMLR v330 (Aug 2026) | Single-task poisoning in exemplar-free CL | Exemplar-free (no buffer); image-domain; not discovery-stage |
| arXiv:2205.11736 | Defense against federated backdoor under continuous training | Federated backdoor leakage, not discovery-stage; we compare CL methods under both |
| METANOIA arXiv:2501.00438 | Avoids learning malicious behaviours in incremental IDS | Provenance/graph PIDS, not flow-feature autoencoder+clustering discovery |
| WeiDetect 2025 / FedSecure 2026 / Nowroozi 2025 | FL-IDS poisoning defences/attacks on CIC/UNSW data | Static FL, no continual-learning dimension |
| arXiv:2603.10776 | Incremental FL IDS benchmark under drift | No adversary; drift robustness, not poisoning |

---

## Budget and units (must be stated identically in every experiment)

- ρ is a fraction of the **training samples entering the stream for the current task**, not a fraction of the global dataset and not a fraction of the buffer (unless the experiment is explicitly about buffer corruption — E2 label-flip of buffer).
- Federated ρ is a fraction of the **malicious client's local shard** (decisions_log.md #10); global-stream equivalents reported alongside (≤2% global at current budgets; higher in Phase-3 breaking-point sweeps).
- For H1 reproduction against arXiv:2608.04602: state clearly whether budget is "% of buffer poisoned" or "% of stream poisoned"; the published 0.0053 collapse figure is tied to their buffer-poisoning setup at p = 1%.
