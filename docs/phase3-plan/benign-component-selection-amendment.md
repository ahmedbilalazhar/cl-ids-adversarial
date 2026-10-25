# Resolve benign sampling without weakening split isolation

24 October 2026. Prospective methodology clarification/amendment based on data-only evidence. No trained-model outcomes were used. The two sampling policies are retained as separate conditional audit artifacts.

## 1. The earlier rule is over-constrained

The previous plan kept **all rows** of every training component containing an attack, then added benign-only components toward 3,500 benign examples per stage. On the conditional original candidate this produces benign counts **3,508 / 3,515 / 3,501 / 17,960**. E4 cannot approach 3,500 because its mandatory component members already exceed the target.

This is not a software rounding problem or a reason to trim a few inconvenient rows. It is a consequence of conflating two rules:

- A component must never span train/development/test or multiple training owners.
- Every source record in a training component must be retained for model training.

The first is the declared isolation constraint. The second is an additional sampling choice. Whole-component role assignment alone does not require retaining every row.

## 2. Recommended explicit benign-selection interpretation

Keep each full source component assigned to one role. After assigning train components, retain all prescribed attack records. For benign selection, treat **all benign members of a component** as one indivisible selection bundle, including across stages. Select that benign bundle either completely or not at all. Attack members remain retained regardless of whether the component's benign bundle is selected.

Every retained training member of that component has the same persistent owner. Unselected benign records remain excluded and reserved to the train role; they do not move into development/test, reappear as fresh data or become hidden replay history.

This is called `benign-subset-by-component` in the data-audit utility. It is a specific interpretation/change to document, not an assertion that the original wording unambiguously required it.

## 3. Exact selection algorithm

1. Use the fixed component-isolated split and the canonical minimum-provenance component IDs.
2. Build each train component's four-stage benign count vector b_g. Start B=(0,0,0,0).
3. Sort candidate components by canonical ID, then apply the fixed seed-2027 PCG64 permutation. Candidates have at least one eligible benign record, whether or not they also contain attacks.
4. In that one pass, select the complete benign bundle only when it strictly reduces `sum_t (B_t-3500)^2`, using integer arithmetic. Reject exact ties; report the realized counts and any feasibility failure.
5. Combine all retained attack records with the selected benign bundles. Compute client Dirichlet targets and whole-component ownership from these retained training counts, consistently across arms/doses.

The component's splitting/ownership identity remains the original complete provenance component; selection does not create a new component or erase a dependency. The fixed benign pool is shared across training seeds. This is an outcome-independent heuristic, not an optimal subset theorem or a per-row random sampler.

## 4. Why role isolation is preserved

For every original component C, sigma(C) is one split. Retained training records are a subset of the union of C with sigma(C)=train. Removing a record from that subset cannot place C in a held-out role. Likewise, assigning one owner to C assigns all retained members consistently. No remaining exact-input/session link crosses roles under the original graph.

This does **not** make the sample naturally representative of traffic. Selection still uses benchmark labels and targets a constructed training volume, as the original 3,500-row design already did. Report the policy and source-to-retained counts.

## 5. Required reporting and rerun consequences

- Keep the strict `mandatory-all-rows` audit as evidence of why the previous assumption failed.
- Publish actual benign/attack counts by stage and client, unused train-role counts, whole-bundle selection IDs and hashes.
- Recompute ownership, attacker eligibility, source ordering and dose ledgers after selecting the policy. Never carry an old ownership cache across changed retained records.
- Keep final test/development bank identities unchanged if the split and other preprocessing are unchanged; do not treat the new sampling policy as another independent dataset.
- If adopted, record the interpretation in the Phase 3 methodology-change table before development. Existing trained runs under another policy would need retuning/rerunning; none have been produced here.

If the instructor instead requires retaining every row of each selected mixed component, retain that stricter policy and explicitly amend/report the 17,960 E4 benign count. Do not claim both a hard 3,500 target and mandatory retention when the data cannot satisfy them.
