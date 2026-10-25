# Methodology diagram review and Phase 3 architecture

Visual review performed on the current Phase 2 PDF's pages 20–21, 24 October 2026. This review supports the Phase 3 plan; the existing manuscript/diagrams have not been edited in this planning pass.

## 1. What the reviewed diagrams already communicate correctly

- Train/development/test and T0 roles are distinct.
- Development precedes a protocol lock; test outputs have no return arrow to learning.
- Corruption happens before class registration/admission and is limited to E2 training labels.
- Head expansion/admission happen once per stage; optimizer reset happens each round.
- Replay read/write and EI's stage-end importance commitment are separate.
- E3/E4 stop fresh corruption but can retain poisoned state.

The page layouts are legible at normal page scale, with distinct boxes and crossing gaps. No clipped box text was observed in the inspected rendering. This is visual review, not an implementation conformance test.

## 2. Clarifications for the implementation diagram

| Ambiguity | Phase 3 clarification |
|---|---|
| The one-stage figure does not draw the next-stage transition explicitly | Show complete state carried to the next stage and final evaluation only after the locked selected matrix is ready |
| “Server registry + admission” can imply central raw-data scoring | The logical server broadcasts the expanded scorer; admission scores remain client-local and only declared model/count/registry messages reach the logical FL server |
| Research checkpoints include local state | Distinguish the experiment controller/archive from the logical FedAvg server; the simulator physically has all data and provides no deployed privacy guarantee |
| Eight accounts might be mistaken for eight FL clients | Each compute worker runs an independent five-client simulation; workers are parallel experiment resources |
| Final testing may appear to follow whichever run finishes first | Gate final evaluation on the complete locked selected matrix and valid artifacts; no test-driven scope or hyperparameter changes |
| Analysis settings are described but their lock is less visible | Connect the frozen analysis specification to evaluation/analysis explicitly |
| Optional external data appears to inherit a complete protocol | It needs its own release/schema/split/source/stage audit and protocol lock; only method settings transfer |
| Snapshot loss and head growth can be conflated | Create the new active head first, then freeze the scorer, then lock accepted IDs for the stage |

## 3. Study workflow

```mermaid
flowchart TD
    A[Canonical release; schema, clock and own-row domain checks] --> C[Select Monday-only benign fitting IDs; freeze T0 transform]
    C --> D[Project raw and actual FP32 inputs; audit reference conflicts]
    D --> B[Build session and raw/final-input components with provenance]
    B --> TC[Exclude T0-linked closure; quarantine conflicts without refitting]
    TC --> E[Fixed component-isolated split and support gate]
    E --> TR[Training package]
    E --> DV[Development package]
    E --> TE[Sealed final-test package]
    TR --> P[Reference implementation; CPU/GPU profile; dev pilots and tuning]
    DV --> P
    P --> L[Lock protocol, data, code, runtime, scope and analysis]
    L --> W[Eight contributor workers: paired seed jobs]
    TR --> W
    W --> S[Each job simulates all five FL clients over E1-E4]
    S --> V[Complete checkpoint bundles; validate identities and selected matrix]
    V --> Q[Read-only final evaluation]
    TE --> Q
    L -. Frozen evaluation and analysis .-> Q
    Q --> AN[Paired endpoints; 29-test Holm family; exploratory studies]
    AN --> R[Figures, claim ledger, course report and publication decision]
    L -. Method settings only .-> X[Separate external-data audit and protocol lock]
    X --> Y[Independent external runs and qualified comparison]
```

The transform is applied to every split without refitting. No arrow carries a final outcome back to scope selection, tuning or training. The optional external branch is not a pooled estimator.

## 4. Stage and round lifecycle

```mermaid
flowchart TD
    IN[Current client shards and prior complete state] --> LAB[Build supplied labels: flip selected Hulk IDs only in E2]
    LAB --> REG[Logical server registers supplied class IDs; append active head rows]
    REG --> SC[Broadcast frozen expanded scorer; each client scores its own rows]
    SC --> AD[Lock accepted IDs and distinct counts once for the stage]
    AD --> BR[Round: all clients receive the same immutable shared weights]
    BR --> OPT[Reset local Adam; preserve retained state]
    OPT --> UP[Train admitted batches with FT, EI or declared DER losses]
    MEM[Local replay and separate RNG streams] --> UP
    IMP[Local prior importance and fixed stage anchor] --> UP
    UP --> INS[DR: first-pass-only reservoir commit using pre-update targets]
    INS -. First-pass state write .-> MEM
    INS --> MSG[Upload local weights and distinct admitted count]
    MSG --> AVG[Count-weighted FedAvg over active clients]
    AVG --> RD{More locked rounds?}
    RD -- Yes --> BR
    RD -- No --> FB[Final aggregate broadcast]
    FB --> MODE{EI learner?}
    MODE -- Yes --> EI[Per-example importance; commit accumulated state and anchor once]
    EI -. Stage-end state write .-> IMP
    EI --> CK[Atomic complete checkpoint to experiment archive]
    MODE -- No: FT or replay --> CK
    CK --> NX{Another stage?}
    NX -- Yes: preserve retained state --> IN
    NX -- No --> DONE[Training complete; enqueue later read-only evaluation]
```

The archive is controlled by the research simulator. It is not a new raw-data message to the logical FedAvg server. Local replay/importance branches are method-specific; FT uses neither. Registry state is append-only, and all active rows remain trainable. The controller must preserve local state and RNG even though model weights are replaced by broadcasts.

## 5. One replay update: order matters

```text
Read admitted current batch.
Cache pre-update eval-mode current logits when first-pass insertion requires them.
Draw min(128, occupancy) from the existing buffer without replacement.
Compute current CE and replay CE with training dropout.
Compute masked/width-normalized replay MSE with dropout off and gradients enabled.
Average each term separately; update local weights once.
Commit eligible first-pass records through Algorithm R using the pre-update cache.
Continue with the saved cursor and independent RNG states.
```

Evaluation mode does not disable gradients. `no_grad` is appropriate for cached teachers; it is not appropriate for the replay MSE student forward. Replaying before insertion prevents a new current record from becoming its own same-update replay example.

The diagrams are native editable specifications. When producing final report figures, render them as vector diagrams with a readable minimum font and verify the exported pages again.
