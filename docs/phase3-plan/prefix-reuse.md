# Exact prefix reuse plan

Planning only. Reuse is valid only when every state and transition that can affect the suffix matches. Different workflow labels do not prevent reuse; different scientific or runtime semantics do.

## Primary E1 sharing

Filters are off in E1 and poisoning begins only in E2. For each final seed:

| Prefix | Logical primary consumers | Required complete state |
|---|---|---|
| FT E1 | FT at four doses | Model, registry, order/head/dropout and other RNG states, manifests |
| EI E1 | EI at four doses | Above plus final shared anchor and sampled empirical importance |
| DR E1 | DR/DG/DM/DC at four doses each | Above plus every client's replay slots, widths, counter/cursor and RNG |

The six-arm primary matrix has 24 logical E1 executions per seed but can use three compatible E1 prefixes. The five-arm core has 20 logical E1 executions per seed and also uses three prefixes. This saves repeated E1 work, not 21/24 or 17/20 of the whole trajectory's training time. E1 is smaller than later attack-heavy stages in the legacy inventory.

Do not share FT and EI automatically: selected learning rates may differ, and EI requires importance/anchor state. Do not share FT and DR automatically: replay begins within E1 and changes the trajectory even before any later task arrives.

## Extensions

- Keep-fraction variants of DM/DC share the ordinary DR E1 prefix because all admission filters are disabled in E1.
- DQ also shares that prefix if its only change is later admission selection and it does not consume future stream RNG during E1.
- FIFO, class-balanced eviction, no-logit and no-label ablations change E1 behavior and need their own prefixes. Their clean/poisoned dose pairs can share within each unchanged ablation setting.
- The external dataset needs its own prefix and independently locked data/model contract.
- A recurrence protocol that reserves some early-family records changes E1 data. It needs its own prefix even if DM/DC are later compared within that protocol.

Conditional E1 prefix counts per final seed are therefore:

| Package | Logical full trajectories per seed | Distinct E1 prefixes |
|---|---:|---:|
| Core | 20 | 3 |
| Course | 26 | 6 |
| Complete | 46 | 8 |
| Strengthened candidate | 54 | 9 |

These assume exact compatible settings and reuse of the declared ablations; they do not include development workloads or new interventions not in those packages.

## E2 scorer reuse

Expanded E2 scorer logits may be reused across DR-family admission arms/doses if E1 state, new head initialization, active slot order, feature rows and runtime are identical. Labels differ across doses, so compute cross-entropy from the appropriate supplied labels for each condition. Never reuse E2 accepted IDs or losses blindly across doses.

After E2, admission arms have different weights/memory. Their later scorers are not common merely because the architecture and seed match. The cost of testing cache compatibility must not exceed the saved tiny forward pass; this is a secondary optimization.

## Clone identity

Record `scientific_run_id`, `execution_id`, `cache_parent_id`, source/data/config hashes and a complete checkpoint hash. Restore all client/process RNG streams. Treat cloned controls as aliases, never independent seeds. A verified cache is immutable; a consumer must make a private mutable state copy before training.

Use **two configuration identities**. The full scientific-run hash includes the method, dose and all future settings. A separate `prefix_spec_hash` includes only a documented projection of settings/data/state transitions that can affect the prefix. DR/DG/DM/DC full run hashes necessarily differ; requiring their entire configurations to match would make the intended E1 reuse impossible.

For E1, the projection includes source/runtime, exact initial arrays/registry, current input/ownership, learning rate/budget, optimizer/dropout, active loss terms, replay capacity/policy, relevant named RNGs and stage-end state. The E2 dose and later admission keep fraction can be excluded only because the protocol proves they are unused in E1. Do not create exclusions opportunistically from a matching outcome. The consumer retains its full configuration identity and records the validated parent/projection rather than pretending to be the parent's complete run.

An extra future stream, such as DQ's random admission priorities, may be initialized deterministically from its fixed namespace at its first use without advancing copied training streams. Record this state extension explicitly. It does not license reconstructing already-consumed dropout/replay state from a seed alone.

Reuse should be established by an implementation acceptance check before final dispatch. If exact parity cannot be established, run the prefix normally and retain the more conservative compute budget.
