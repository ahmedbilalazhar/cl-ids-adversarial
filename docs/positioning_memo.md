# Positioning Memo (locked 2026-09-26) — which finding headlines the Computers & Security paper

Basis: the verified literature landscape (search_protocol.md 2026-09-26
arXiv-API pass + full reads of Paper-1/2/3), NOT completeness of our runs.

## Candidates

1. **Federated poisoning + Byzantine × FCIL-IDS × CL-method comparison.**
   Two independent verified future-work calls name exactly this: Su 2025
   (content-verified: "future research ... federated learning poisoning and
   non-IID client data") and EdgeFedCIL §3.1 (read in full: malicious-client
   attacks, model poisoning, backdoor injection "outside the scope"). The
   adjacent FL-IDS poisoning literature (Lavaur C&S 2025, BRFID 2026,
   FedSecure 2026, WeiDetect 2025, Nowroozi 2025, 2609.03420) is uniformly
   STATIC — no continual dimension anywhere. Korba 2024 owns CIL×FL without
   an adversary. Our results in hand: EWC immunity (p=0.0156 ranking,
   p=0.94 transfer), no dose-response (honest null), matched-memory control.
   Phase 3 (Byzantine set + robust aggregators + adaptive attacker +
   breaking-point sweeps) makes this unassailable as the spine.
2. **Discovery-stage poisoning (AE→HDBSCAN).** Real but narrower: Sonic owns
   clustering-poisoning, 2002.02741 owns AE-poisoning; our intersection claim
   (continual-IDS discovery pipeline + nopois control) holds on current
   evidence but rests on a 0-vs-small effect with n.s.-adjacent costs
   (p=0.078). Strong secondary, weak headline.
3. **Drift-vs-poison defense confusion.** Significant in hand (small-loss
   helps p=0.0156 without removing flips; kNN harms p=0.031 with 0.000 rare
   retention) and conceptually journal-grade — but it is an ANALYSIS finding
   about defences, not an attack contribution; it strengthens a paper whose
   spine is (1), cannot carry one alone.

## Locked decision

**Headline = (1): poisoning (+Byzantine) of federated class-incremental IDS
with a CL-method comparison.** Secondary-A = (3) (threats-to-validity-grade
defence analysis). Secondary-B = (2) (separated discovery result).
The paper's one-sentence claim: *the first adversarial evaluation of
federated class-incremental IDS — answering the deferred poisoning+non-IID
calls of Su 2025 and EdgeFedCIL — showing EWC transfers intact where
finetune/DER++ do not, defences confuse drift with poison, and discovery
poisoning misfiles rather than suppresses.* "First" stays attached to the
verified citations, never unqualified; Scholar/Xplore/Scopus manual counts
must land before submission.
