# Resources and logical messages

Second audit, 24 October 2026. These calculations are theoretical payload accounting, not runtime, peak memory, bandwidth, latency or deployment measurements.

## 1. Model size depends on the active head

For the declared 76 -> 128 -> 64 -> C MLP, parameters are

`P(C) = (76*128+128) + (128*64+64) + (64*C+C) = 18,112 + 65*C`.

An FP32 parameter message has `4*P(C)` raw bytes. If all nominal classes have training support, active widths after E1/E2/E3/E4 are 3/8/12/15, giving 73,228/74,528/75,568/76,348 raw bytes. Report actual registered widths if unsupported families are absent. A 15-slot replay-logit array does not mean that fifteen outputs are active in E1.

The corrected source has an extra confirmed label before taxonomy mapping. It cannot inherit C_max=15 and the 381-byte slot calculation automatically. Any new release needs its own mapped inventory and capacity declaration.

## 2. Retained versus transient state

At C=15, one full FP32 parameter-shaped array occupies 76,348 raw bytes.

| Object | Raw bytes at maximum width | Lifetime / caveat |
|---|---:|---|
| One model parameter copy | 76,348 | Each actual server/local copy counted |
| EI importance plus anchor | 152,696 per client | Retained between stages; excludes model/RNG/schema overhead |
| Five EI retained importance/anchor pairs | 763,480 | Five simulated sites, not one pooled importance vector |
| Declared 500-slot replay tuples | 190,500 per client | Retained; padded 15 logits, 76 inputs, labels/IDs/widths |
| Five declared replay buffers | 952,500 | Excludes counters/RNG/container/alignment |
| Adam first/second moments | 152,696 per active local optimizer | Transient under broadcast reset; step scalars/metadata additional |
| One parameter gradient copy | 76,348 | Working state, not retained memory capacity |

Report actual array allocation and serialized checkpoint bytes separately. A scalar stream counter and saved RNG state matter to recovery even though small. Current shards, accepted IDs, cached teachers, Fisher chunks, activations, CUDA allocator reservations and the Python process are also working resources. Theoretical retained-state bytes are not peak RSS or VRAM.

EI and replay have different retained information and budgets. Equal replay capacity across DR/DM/DC/DQ does not make FT/EI/replay equal-resource learners. Keep the comparison's intended information/resource differences visible.

## 3. Declare a logical message trace

Use a versioned message ledger with:

`run, stage, round, sender, receiver, message_role, model_width, tensor_raw_bytes, serialized_bytes, registry_bytes, count_bytes, reused_transmission_id`.

Roles include class-registry declaration/broadcast, expanded-scoring model, round model download, admitted-count/model upload and final-aggregate download. Never sum the same physical transmission twice merely because the first-round model also serves as the frozen admission scorer.

**Proposed simple protocol:** all five logical clients receive each round's shared model and the final aggregate; only active clients upload an update. The stage setup's expanded scoring broadcast is reused as the first-round download because the weights do not change before local updates. Registry/count messages are counted separately. Under this declared convention,

`raw_parameter_bytes(stage) = [K*R + sum_r active_clients_r + K] * 4*P(C_t)`.

Here K=5 and admission is locked, so the active set normally stays constant over rounds. If all are active, this reduces to `5*(2R+1)*4*P(C_t)`. This is a prospective message convention; another implementation must document its actual trace rather than quietly report this idealized formula.

An inactive client can receive weights/registry without sending an update. Its zero aggregation weight is not a zero-byte upload measurement. The final broadcast is needed for the specified EI state commit and common next-stage state; account for any optimization that combines transmissions explicitly.

## 4. Simulator boundary

This is an in-process five-client experiment. File writes and tensor copies are not real network transmissions. Report logical serialized message volume; benchmark actual networking only if a separate transport implementation is built and measured. A research checkpoint archive holding local replay does not describe what the logical FedAvg server receives.

Registry class names disclose class-presence metadata in the proposed simulation. No secure-aggregation, differential-privacy or encrypted-transport guarantee follows. The comparison can still be valid within its declared threat and message contract.

## 5. Efficiency claims need the complete work ledger

Keep separate totals for CPU data preparation, development, successful final training, failed/retried execution, checkpoints/transfers, final inference and analysis. Record charged accelerator-session time and actual process time. Prefix aliases save physical work, not scientific conditions or independent observations.

Measure cost under compatible hardware/precision and normal logging. Report an isolated reference timing and actual campaign cost if concurrent workers contend for resources. Do not convert GPU hours directly into energy, money or real-time deployment capacity without the missing measurements.
