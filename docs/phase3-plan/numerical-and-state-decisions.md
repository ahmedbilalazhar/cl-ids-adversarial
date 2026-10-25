# Numerical and state decisions to freeze

Implementation checklist, 24 October 2026. These details close reproducibility gaps before development; they do not report completed checks.

## 1. Initialization

Resolve initial E1 head initialization explicitly. Recommended convention: initialize all newly active rows, including the first active head, using the documented Xavier-uniform/zero-bias rule. This is a prospective clarification of the current wording and must be recorded before development.

For an appended block with h input features and r new rows, record whether Xavier fan-out is r (the new block) or the full expanded output width. The current helper initializes the appended slice, so its fan-out is r. Different choices give different bounds. Pin the gain, dtype and RNG context rather than relying on a constructor's incidental initialization. [PyTorch initialization reference](https://docs.pytorch.org/docs/2.14/nn.init.html).

Record the framework-standard encoder initializer and exact framework version. Generating initial/head arrays once on CPU and storing their hashes can simplify pairing, if that convention is frozen consistently. It does not make subsequent CPU/GPU training bitwise identical.

## 2. Stable RNG namespaces

Use a versioned integer namespace/key scheme with `SeedSequence` or a cryptographic digest of a canonical structured key. Do not derive seeds from Python's salted `hash()`. Avoid allocating child streams in outcome-dependent order; stream identity should not depend on which arm happened to launch first.

For example, ownership, poison, current-order, replay-draw, replay-insert, importance and head namespaces have fixed IDs. Combine the master seed with the applicable client/stage/round/epoch coordinates. Preserve complete state for persistent streams. Pin the chosen bit generator and NumPy version. [NumPy parallel RNG guide](https://numpy.org/doc/stable/reference/random/parallel.html).

## 3. Per-record masked replay loss

For replay record i with stored width omega_i:

```text
row_loss_i = sum_j<omega_i((student_logit_ij - stored_logit_ij)^2) / omega_i
logit_loss = mean_i(row_loss_i)
```

Do not average over padded future coordinates or divide once by the total valid-coordinate count across the batch. Those operations weight old and new stored widths differently. Clip the target tensor to the current active width and require `0 < omega_i <= current_width`; future inactive logits are never predictions.

Mask invalid-coordinate differences before squaring. Squaring very large unused values and masking afterward can create invalid intermediate derivatives. Valid-coordinate overflow still requires the declared numerical-failure policy; masking must not hide a real instability.

Current CE and replay CE are separate batch means, even when their batch sizes differ. Replay size is `min(128,occupancy)`, not the last current-batch length. Restore training mode after eval-mode teacher/logit passes. Do not reuse one dropout-enabled replay forward for both CE and logit matching.

## 4. Empirical importance arithmetic

At the final aggregate, compute each sampled record's log-likelihood gradient, square each parameter gradient, then average over the exact selected records. The square of the mean gradient is not this estimator. The penalty sums parameter contributions with the declared lambda_E/2; no hidden per-layer/per-parameter normalization is added.

Freeze gradient/importance accumulation dtypes, chunk order, finite checks and reference tolerances. FP32 model/Adam settings alone do not fully specify a vectorized reduction. If an accumulation-precision change is needed, apply it commonly, document it and resolve it before final dispatch. Importance state remains fixed inside the stage; only the stage-end transition updates it.

## 5. Prevent mutable aliases

- Copy reference labels before applying corruption; never mutate a shared view or final-test object.
- Treat prepared features and split manifests as read-only.
- A model `state_dict` can hold references to live tensors. A frozen broadcast/scoring snapshot must own immutable values rather than alias a local model being optimized.
- A cached prefix must be cloned into private mutable consumer state.
- Keep the logical server model unchanged until all active clients' local updates are ready.
- Preserve insertion ordering when multiple reservoir proposals target one slot.

These rules prevent code that looks structurally correct from changing the scientific treatment accidentally.

## 6. Precision and determinism

Record torch/CUDA/driver/GPU versions, BLAS/thread settings, deterministic-algorithm policy, matmul precision and any required cuBLAS environment configuration. Use the controls appropriate to the installed version; do not mix incompatible old/new precision APIs. Do not silently enable AMP/TF32 or change batch size for speed.

Document whether an unsupported deterministic operation fails or triggers a prospectively defined common alternative. A warning-only configuration cannot be described as guaranteed deterministic. Different hardware/release execution is not automatically bitwise reproducible.

## 7. Evaluation cache identity

Identical model-weight tensors, class map, bank/transform, evaluation mode and runtime can share inference outputs. Buffer-only differences do not alter inference, but a full-checkpoint hash alone may obscure that distinction. Use an explicit model/evaluation identity and validated aliases. Approximate weight similarity is insufficient for cache reuse.

All final conditions use one declared evaluation contract, even if evaluation runs on CPU while training runs on GPU. Do not reuse development predictions or cross-runtime outputs simply because the seed and architecture match.

## 8. Exact quotas and stable ranking

“Global” in DG/DM means ranking across classes **within one client's current shard**. It does not mean pooling private rows from all five sites into a central ranking. DC/DM quota counts can be computed from supplied-label counts and the shared new-label registry; DM does not need a trained DC model or its accepted-ID artifact.

Represent doses and keep fractions as integer numerator/denominator pairs. Compute the poison count with integer floor division and the kept count with integer ceiling division. This avoids an accidental off-by-one caused by floating arithmetic. For example, the primary 75% keep fraction is 3/4 and dose 30% is 3/10.

The original DG wording does not specify rounding as explicitly as DC. Resolve it before development; the recommended common convention is `K=max(1,ceil(3*n/4))` for a nonempty local shard and K=0 for an empty one. Do not inherit Python's ties-to-even `round()` from the legacy filter silently. This clarification matters even though DG is optional in the focused package.

Sort by `(finite_loss, immutable_record_ID)` with a specified deterministic implementation. Treat non-finite scores as a numerical failure, not as favorable/rejected examples selected by an implicit sort convention. Every accepted set is locked for the whole stage. Record cases where a small benign group or the new-label exception makes a nominal keep-fraction change have no realized treatment difference.

Canonical conflict quarantine occurs before controlled label corruption. Never re-run a reference-label conflict check inside admission to remove intentionally corrupted examples using oracle information.

## 9. Development ties and reuse-independent cost

Freeze exactly what constitutes a tie and the configuration ordering before inspecting development outcomes. Count-derived rational macro-F1 can distinguish an exact tie from floating subtraction noise. Do not invent a convenient numerical tolerance after seeing a preferred candidate.

For tuning ties, “lower measured cost” must describe comparable logical trajectory work, not the zero incremental cost of an aliased run or the order in which a cache became available. Use the same cost fields/runtime for all candidates and attribute cached prefix work to its logical consumer for this comparison. Actual quota accounting still records the real saved executions separately.

The clean gate and model-selection rule also need reconciliation. One defensible prospective clarification is to require all development seeds to be valid, filter candidates by the required average acquisition gates, and then maximize the declared macro-F1 among feasible candidates. The current wording can also be read as selecting the unconstrained macro-F1 winner and stopping if it fails. Choose and document one interpretation before development; do not switch after seeing a favored result.

If the selected common synchronization budget cannot produce a feasible learner within its grid, a second-budget development revision may be justified before final testing. Count that additional tuning rather than presenting the original 81 rows as all development compute. Run the poison diagnostic only after clean settings pass their gates.

## 10. Lossless state serialization

PCG64 exposes two unsigned 128-bit state values as Python integers. JSON numbers read through a binary64 implementation such as ordinary JavaScript can lose integer precision above 2^53-1. A checkpoint that survives Python JSON parsing can therefore change if an importer/dashboard parses and rewrites it through ordinary JavaScript numbers. [NumPy PCG64 state](https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html), [RFC 8259 number interoperability](https://www.rfc-editor.org/rfc/rfc8259).

Use a typed schema: encode large RNG integers as canonical decimal strings and parse them back to bounded Python integers before restoration, or store an explicitly typed binary representation. Preserve the bit-generator name/version and every state field, including cached uint32 state. Torch CPU/CUDA RNG byte states can use dedicated uint8 array payloads. Store uint64 record IDs in typed arrays or lossless strings, never through an unbounded floating-number conversion.

Emit strict UTF-8 JSON with `allow_nan=False`, unique keys, a fixed canonicalization rule and explicit null/status for missing values. NaN/Infinity are not valid portable JSON result values. File/schema hashes must cover the exact bytes; an incidental timestamp/path/worker name belongs in execution metadata rather than scientific identity.

A checksum of an already rounded state does not recover the lost bits. Resume evidence must compare the restored state/next transition under the pinned implementation, not merely show that a checkpoint file parsed. This is planned implementation acceptance work; no learner/resume tests were run in this audit.
