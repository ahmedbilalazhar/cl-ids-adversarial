# Independent development count audit

This delivery tool reconstructs endpoint arithmetic from committed development
JSON counts. It reads no features, prediction arrays or final-test outcomes,
and performs no confirmatory inference on the three development seeds.

`scripts/audit_phase3_endpoints.py` independently checks all16 source-code
confusion rows/columns, registered head order, eligible true-row filtering,
unsupported rare outputs, class TP/FP/FN, exact macro-F1, full-seen binary counts,
Hulk partitions, benign provenance, cohort accuracy and bank/support identity
across conditions. A prediction into a registered rare class remains an error
in the eligible bank. It reconstructs acquisition A, E4 FAR, ACC/BWT/forgetting
and mean four-stage macro-F1 as rational values. The paired selected-condition
FT diagnostic additionally reports H and the immediate source-recall change.
Control outcomes remain separate one-seed engineering evidence.

The auditor does not independently regenerate predictions from model features.
Its assurance concerns count consistency, endpoint arithmetic and input lineage;
the model/evaluator integration and recovery checks supply different evidence.
Original evaluation artifacts are never edited by this tool.

Run from the workspace root after the declared grid and selected-condition
diagnostic/control tools complete:

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m scripts.audit_phase3_endpoints
```

For a snapshot of immutable completed receipts during a grid, use
`--receipt-preflight --output <fresh-path>`. This does not select settings or
aggregate partial results as completed research. The actual first successful
snapshot audited17 valid rows and rejected eight intentionally corrupted copies.

The first preflight assertion incorrectly required arrived-cohort counts to
partition the whole cumulative bank at early stages. The fixed FAR bank includes
all-period benign cohorts from E1, while R[t,j] is available only for j<=t.
The corrected assertion bounds the omitted records/correct counts by benign
support/correct/false-alarm totals and requires an exact full partition at E4.
The failed attempt is retained in
`results/phase3-endpoint-audit-v1/preflight-attempt1.json`; no learner or frozen
evaluator change was required. Each successful audit includes eight corrupted
count/endpoint rejection checks, input/source hashes and exact derived values.
