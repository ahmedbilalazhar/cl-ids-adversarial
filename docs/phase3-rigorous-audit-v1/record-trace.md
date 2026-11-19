# Representative record trace

Immutable training ID `17179917883` maps to component `17179903332`, E2 row index12196, reference label4(Hulk), supplied label0(benign), attacker client3. Its74-dimensional FP32 bytes hash to `496684a6388b0dfcb1df00115f46b4c09c4c6ec0c7a33b2da44d4bbe3c3423ee`. The independent T0 reconstruction checks this row along with every exported row.

The ID is present in the E2 admitted first-pass reservoir during exact DR+DC replay. This proves admission and insertion for this exemplar. Replay samples use only supplied labels/features/teacher logits; poison IDs are joined only for external bookkeeping and the explicitly scoped oracle. Later ordinary versus repaired buffer observations are in representative-record-trace.json. The training ID never enters the development bank; evaluation uses a separate fixed Hulk bank of31,694 records and benign bank of216,158 records.

A record remaining in memory is not proof of its exact draw count or causal responsibility for predictions. Per-update replay exposure by ID was not retained in the archived result; this missing diagnostic is disclosed rather than inferred from occupancy.
