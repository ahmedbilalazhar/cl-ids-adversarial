# Federated controls audit (2026-09-28)

This is a source audit for Phase D of `docs/plan.md`, not an experimental
result. Current `main` is `a4558b582a46352bc8f3708af3ce09aeadb8ef49`.
Changing any `src/*.py` file changes the manifest-v3 source fingerprint and
would invalidate the nine current E4 diagnostics against the live tree;
preserve or archive those results before implementing these controls. This
already happened once: nine earlier diagnostics were archived under
`results/_archive/discovery_pre_commit_asr_20260928/` and rerun after
the ASR-null and buffer-poison fixes.

| Requirement | Current implementation | Consequence and next control |
|---|---|---|
| Client identity | `run_federated` calls `dirichlet_partition` with `seed + 1000 + task` at each task. No site/client ID is read from the task artifact. CL method objects persist by client index. | Describe the existing experiment as **resampled simulated clients with persistent CL state**. A stable-client comparison needs a source-backed site identity or an explicitly synthetic fixed assignment; do not call either a real network segment. |
| Rounds and work | One broadcast, local training call, and aggregation occur per task. `local_epochs` and shard size are available, but optimizer steps and communication bytes are not recorded. | Add a bounded 1-versus-multiple-round sensitivity only with matched training-work accounting and logged messages/bytes. |
| Optimizer | Each client owns an Adam optimizer. `load_state_dict` broadcasts model weights without resetting its moments. Head expansion rebuilds the optimizer. | Persistent moments follow client index across new shards. Compare carried versus reset moments or keep this as an explicit protocol dependency; log optimizer steps and resets. |
| Replay | ER and DER++ buffers persist by client index, use global NumPy sampling, and cap at `buffer_size` by random dropping. DER++ stores logits after the update, with width padding when needed. | Log buffer occupancy, class mix, memory, and logit source per task. Changed replay semantics require versioned arms and fresh runs. |
| EWC | Each client estimates Fisher from at most 32 post-training minibatches, accumulates matching-shape matrices, and stores a local anchor. The federated wrapper later sets the anchor to local weights immediately before loading aggregate weights. | Audit the intended anchor semantics and loss scaling with a tiny analytic test, then version any change. Do not attach old EWC numbers to a changed anchor rule. |
| Aggregators | FedAvg weights by retained shard size. Median, Krum, Multi-Krum, and trimmed mean consume unweighted client deltas. Config validation already rejects Krum/Multi-Krum unless `n_clients > 2*n_mal + 2`, and requires `n_mal` to match malicious IDs. | Run a clean control under each aggregator before interpreting attacked outcomes. A clean FedAvg result is not a same-aggregator control. Check actual active clients after filtering, since empty clients still submit zero-weight model copies to unweighted rules. |
| Architecture | `TabularTransformer.forward` projects the full feature vector then adds a length-one token dimension. | Call it a **single-token transformer block**. It does not model attention between feature tokens. A true feature-token architecture would need a separate, compute-matched protocol. |

The next source change should add per-client task records (pre/post-defense
sample count, class counts, participation, optimizer steps, buffer occupancy,
and communication bytes) and reject or explicitly handle empty submissions
for unweighted aggregators. Inspect the resulting small synthetic federated
run before selecting matched controls or launching expensive comparisons.

## Implementation addendum (2026-09-28, decisions #71–72)

Done, with the nine E4 diagnostics copy-preserved first (they no longer pass
live checks under the new fingerprint; record in
`results/_archive/discovery_prefedcontrols_20260928/`):

- `src/federated/fedavg.py::run_federated` records per client-task:
  `pre_defense_n`, `post_defense_n`, `class_counts_pre/post`,
  `participated`, `optimizer_steps` (`local_epochs * ceil(post/batch)`),
  `buffer_n`/`buffer_class_counts`/`buffer_bytes_est`, and `comm_bytes`.
  Summary gains `comm_bytes_total`, `fed_participation_rate`,
  `fed.excluded_inactive_clients`, and `fed_exclusions`.
- Inactive (empty-shard or defense-emptied) submissions are excluded from
  trimmed-mean/median/Krum/multi-Krum/dynamic-trust aggregation; the
  plain-FedAvg weighted path is byte-unchanged, and delta-path FedAvg still
  uses weights. Krum `n_mal` is clamped to the active count. A fully
  inactive round keeps global weights.
- `DynamicTrust.__call__` accepts an optional client `index` map (behavior
  identical when absent) so trust persists per client across exclusions.
- `tests/test_fedcontrols.py` (4 tests): record consistency, rigged-empty
  median/Krum exclusion (participation 0.8, finite R), trust index mapping,
  empty-input helpers. Full suite: 28 passed.

Still pending: stable-client/site comparison, 1-vs-multi-round sensitivity
with work accounting, same-aggregator clean controls, EWC anchor/loss
audit with an analytic test, and any claim of a true feature-token
architecture. The resampled-simulated-clients description stands.
