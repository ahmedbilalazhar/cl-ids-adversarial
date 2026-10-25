# Protocol details that must be executable

Second audit, 24 October 2026. These are concrete **proposed predevelopment conventions**, not implemented learner behavior or final experimental findings. Record adoption in the amendment register. The original primary endpoints and 29-test family remain unchanged.

## 1. Deterministic whole-component client allocator

The earlier plan said “minimize a weighted deviation” without defining the objective or ties. Two independent implementations could therefore produce different clients from the same seed. Use this narrow reference specification unless a documented alternative is adopted before development.

**Inputs:** the final retained training components after calibration exclusion, quarantine, duplicate-survivor selection and benign-pool selection; fixed canonical family order; five clients; the ownership RNG. Count only retained, scheduled model records. Preserve the larger provenance component identity.

1. For every family f, let N_f be its number of retained training records. Draw one five-vector pi_f from Dirichlet(0.5,...,0.5), in canonical family order. The continuous target is T[k,f] = N_f*pi_f[k]. Do not round targets into independent row allocations.
2. Let v[g,f] be the number of retained records of family f in component g. Order components by decreasing sum_f v[g,f], then increasing minimum immutable provenance ID. A component with no retained records is not assigned as a training unit.
3. Start A[k,f]=0. For each component, compute the change in

   `L(A) = sum_f:N_f>0 sum_k ((A[k,f] - T[k,f]) / N_f)^2`

   if its complete count vector is assigned to each candidate client. Choose the smallest change. Use fixed-order FP64 arithmetic and the smallest logical client ID on an exact tie. Commit the complete vector and never split the component.
4. Assign all records arriving in later stages from that component to the same owner. Do not redraw by stage, method, dose, corrupted label or admitted subset. Do not repeatedly redraw until an aesthetically balanced partition appears.
5. Save pi, T, realized A, component ordering/owners, objective, implementation version and all hashes. Report per-stage per-client row/family support, inactive sites, largest-component share and target error.

The normalization gives each family's relative allocation error equal weight. This is a deterministic heuristic, not an optimality theorem or independent row-level Dirichlet sample. A different normalization is a different allocation protocol. No minimum client size is imposed by this proposal; inactive clients follow the existing state-machine rule.

The builder uses all scheduled **training** family counts to construct persistent synthetic sites. This is an offline benchmark construction using future training inventory, not evidence that real organizations or an online allocator know future traffic. No development/test rows enter ownership.

With at least 50 retained training Hulk rows and five owners, at least one client has ten Hulk rows by the pigeonhole principle. The required source support gate therefore also ensures a nonempty eligible-attacker set, provided eligibility is counted on these same retained records. Save the eligible population anyway; do not select an attacker by model performance.

### A concrete benign-only selection heuristic

The earlier “jointly approach 3,500 rows” instruction also needs an algorithm. The all-rows interpretation was found to force 17,960 E4 benign records. The recommended prospective `benign-subset-by-component` interpretation retains prescribed attack rows, starts B=(0,0,0,0), and treats all benign members of each training component as one four-stage bundle b_g. Sort by canonical component ID, then apply one fixed seed-2027 permutation. Visit once; select the complete benign bundle only if adding b_g strictly decreases `sum_t (B_t-3500)^2`, updating B when kept. Reject exact ties. Keep excluded members reserved to the same train role; no row is reused or reassigned. [Detailed amendment](benign-component-selection-amendment.md).

This transparent O(number of components) heuristic is a proposed reference choice, not a closest-subset solver. Report final stage counts, rejected bundle sizes and empty-stage/large-deviation failures. If it cannot provide the required nonempty stage pools, resolve the data gate prospectively; do not silently search selection seeds or claim an optimum. Split/ownership atomicity is preserved even though an excluded training record is not retained for learning. The stricter all-rows policy remains a separately identified option.

Five-fold group stratification is likewise a candidate allocator, not a feasibility proof. Fifteen total family components is a necessary minimum for five in each of three splits; it is not sufficient under the 60/20/20 row target or a particular five-fold allocator. Publish realized support and repair the data protocol before model outcomes if necessary.

Pin a splitter version containing the documented SGKF `shuffle=True` stratification fix, introduced in scikit-learn 1.8. The old generic `scikit-learn>=1.3` requirement does not ensure that behavior. The conditional split audit uses 1.9.1 in an isolated data-audit environment; it is not the final learner runtime lock. [Official 1.8 release notes](https://scikit-learn.org/stable/whats_new/v1.8.html).

## 2. Canonicalization and quarantine order

An audit must make the order explicit because quarantine, duplicate collapse, T0 exclusion and FP32 projection can interact.

1. Assign immutable provenance IDs on original source rows and retain raw annotations/metadata.
2. Parse source fields under a versioned schema; reject malformed numeric/metadata records under a reason-coded rule. Keep reason counts and family/day denominators. Parsing must not silently infer a different schema per file.
3. Normalize only declared label aliases. Unknown labels fail the census instead of disappearing. A release-specific attempted-label decision precedes reference-annotation conflict classification. Record pre-transform conflicts for the learning/evaluation exclusion audit; cross-day annotations must not select T0 fitting records.
4. Construct operational session links on parseable original records. Preserve links and component provenance before collapsing duplicate copies. A quarantined record is never a learner record; decide explicitly whether its already established session/provenance links remain in the conservative isolation graph. **Proposed default: retain those links.** Removing an ambiguous bridge must not create artificial split independence.
5. Fix T0 fitting IDs using **Monday-only** source validity and its supplied benign reference annotation. Do not exclude a Monday fitting row because a future day's identical feature vector has a different annotation. Fit the specified scaler once. Keep fitting IDs distinct from the component exclusion closure; no later closure member is added to fitting.
6. Produce the ordered final FP32 inputs, with signed zero normalized. Detect exact-input conflicts and same-label duplicate groups on these actual inputs; confirm candidate hashes with byte equality. Preserve all established session/content links. Never use approximate similarity as an undeclared deduplication rule.
7. Quarantine conflicting-input records from **learning/evaluation**, choose deterministic same-label survivors, finalize the full component graph and exclude the complete closure touching T0. T0 closure membership can change after final-input collisions; scaler statistics and fitting IDs do not. Report fitting rows that later share an ambiguous final input; they remain calibration-only observations and are never weight-training examples. This is a predeclared calibration-role distinction, not proof that the reference annotation is certified truth.
8. Allocate whole components to the fixed split. Select the prescribed training benign pools without breaking components, then allocate retained training records to clients. Save which counts are before/after each operation.

**Required census columns:** raw rows, parsing exclusions by reason, attempted remaps, conflicts, duplicate copies, T0 fitting rows, T0-linked excluded rows, retained rows, components, largest component, class/day coverage, realized split counts and eligibility. Record a row's multiple diagnostic flags but use one documented precedence for mutually exclusive exclusion totals, so the flow diagram adds up.

The full graph can contain a large connected component through repeated generic feature vectors. Do not remove inconvenient equality links to rescue the support floor. Report infeasibility and amend before model outcomes if the original benchmark cannot support the declared isolation.

**Iteration correction:** the first conditional component audit excluded Monday fitting rows using cross-day raw-label conflicts and then stopped on new FP32 conflicts. This made calibration eligibility depend on future annotations and introduced a circular validity criterion. Version 2 uses Monday-only fitting eligibility, then freezes the transform and excludes all linked/conflicting learning/evaluation records. The superseded v1 evidence is retained explicitly; no model results informed this correction.

## 3. Admission changes dose-dependent training volume

Let n be the attacked client's fixed E2 current-row count, b its honest benign count, and q its flipped Hulk count. In this schedule the other supplied attack classes are protected as new. With n_B=b+q and the declared benign quota K_B, DC admits

`n_DC(q) = n - (b + q - K_B)`.

DM and DQ use exactly this same per-client admitted total in the matching dose. For the ordinary 75% branch, the rejected count is `floor((b+q)/4)`. For n_B<20 it is zero. Thus more label corruption can change optimizer-step count and the affected client's FedAvg weight even though raw feature rows never change. The small-pool exception can also create a discontinuity at n_B=20.

Consequences:

- DC–DM within a fixed dose controls volume and aggregation weights; their composition and subsequent learned states differ.
- Clean-subtracted H for a filtered pipeline measures the total poisoning-plus-admission response, including these weight/work changes. It does not isolate an effect of a fixed count of corrupted gradient contributions.
- Unfiltered FT/EI/DR keep fixed current-data volume across doses, although their gradients and retained state change.
- Report the per-dose accepted counts, active clients, optimizer updates, relative aggregation weights, rejected honest/poison counts and quota floor. A plot against nominal rho alone is insufficient.

Do not freeze the clean quota across poisoned conditions as a silent “fairness fix”: that would define another admission method. Such a control is optional and would require its own prospective protocol and budget.

## 4. Expanded-head scoring diagnostics

The frozen scorer includes freshly initialized output rows. Its benign cross-entropy ranking can therefore depend on random new-class logits as well as previously learned benign recognition. All paired arms share the declared head initialization, so this is part of the specified treatment; it is not evidence that the score identifies malicious traffic reliably.

After protocol lock, use evaluator-side annotations to describe honest-benign versus flipped-Hulk score distributions, ties, rank discrimination, actual selected IDs and distance from the quota's theoretical floor. No annotation is exposed to admission. Optionally compute the old-head-only benign ranking from the **same frozen snapshot** as an offline diagnostic: disagreement can reveal sensitivity to new rows without training extra trajectories. It does not estimate the performance of a different scorer or justify selecting one after testing.

Store summaries or a compact E2 score/ID artifact when feasible. A mechanism claim about new-head initialization would require a separately specified training intervention, rather than a correlation or an appealing histogram.

## 5. Initialization and EI naming

Keep the existing proposed Xavier/zero-bias head convention and explicit encoder initializer. Call EI an **online EWC-style diagonal supplied-label empirical-importance baseline**. The declared estimator squares each supplied-label per-example gradient before averaging. It is not a model-expectation Fisher, and corrupted supplied labels intentionally enter it. A correct implementation of this estimator does not establish that it is the strongest EWC variant. [Van de Ven, ICLR 2025 blogpost track](https://arxiv.org/abs/2502.11756).

If the intended claim is superiority over competitive EWC broadly, evaluate a justified model-label/exact Fisher variant with its own development settings and compute budget. For the narrower comparison of specified retention pipelines, precise naming, correct arithmetic and clean-learning evidence are sufficient. Do not silently replace the baseline and keep the old hyperparameter identity.

## 6. Classification of these decisions

The allocator, quarantine-link policy and initialization conventions need a predevelopment versioned choice. Dose-volume arithmetic and scorer limitations clarify consequences of the current protocol; they do not change it. New baselines, operational thresholds, different data releases or different primary inference require explicit amendments. None of this file makes the planning manifest dispatchable.
