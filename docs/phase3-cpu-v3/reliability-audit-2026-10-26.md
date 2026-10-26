# Delivery reliability audit — 26 October 2026

The user requested a new two-hour improvement pass. Baseline commit:
`985d206ab50879c36d546435c232989f54c1e9cf`; branch:
`codex/phase3-continuation-readiness`. The interval began at 01:34:16 UTC
(06:34:16 Asia/Karachi). The [completion record](../../results/phase3-reliability-audit-v2/completion.json)
records the actual end and elapsed time. This is engineering, inspection and
fixture execution time, not two hours of model training.
The work spans a later conversation interruption; elapsed UTC time must not be
interpreted as continuous work or continuously charged computation.

## Findings and corrections

| Finding | Consequence | Correction and evidence |
|---|---|---|
| A restore success marker existed before its flush succeeded | An injected flush error left both `restore.commit.json` and `restore.failed.json`, making publication status ambiguous | Serialize and flush a private receipt before exclusively publishing its final name. The [baseline reproduction](../../results/phase3-reliability-audit-v2/restore-prefx-reproduction.json) records the defect; regression tests assert no commit marker on flush failure |
| A rehashed prediction file could disagree with the reported confusion counts | Hash consistency alone did not establish that saved predictions and count artifacts described the same marginal outcomes | Validate exact NPZ members, canonical IDs/bank hash, typed shapes, source-code slots, prediction index range and confusion-column totals before catalog writes. The [guaranteed baseline reproduction](../../results/phase3-reliability-audit-v2/prediction-baseline-guaranteed-reproduction.log) changes one prediction and updates its hash; the old importer accepts it and the corrected importer rejects it |
| Parent and alias mappings repeated the same expensive evaluation checks | Large alias batches repeated checkpoint/prediction validation for identical evidence | Cache validated payloads only inside the private immutable archive operation, keyed by physical parent and both mapped paths. Each alias still undergoes its own transactional lineage/idempotency checks and adds zero trajectories |
| Recovery tests were primarily isolated fixtures | Short tests gave limited evidence about sustained writer/export interleavings, rolled-back histories and resource lifetime | Add a bounded counts-only concurrency/recovery qualifier, with forced process exits, snapshot-prefix checks, orphan preservation and a hash-linked cycle ledger. This supplies local stress evidence, not provider durability |
| Kaggle expands uploaded archives, but the notebook expects the original mounted ZIP | Following the earlier direct-ZIP upload instructions can leave the expected file unavailable; re-zipping would change the trusted archive hash | Prepare a private Base64 transport file and a notebook bootstrap that restores and verifies the exact original ZIP before existing v5 cells run. Local emulation verifies all 82 payloads; actual provider upload remains pending |
| Count import deep-copied every freshly decoded metric before changing one schema label | Profiling showed redundant recursive copying in a read-only validation path | Use a top-level dictionary copy; complete 72-row verification results are identical in six paired benchmark runs, and the final source matches the benchmarked candidate hash |

`phase3_delivery.io.publish_new_bytes` uses a unique staging file on the same
filesystem, flushes its bytes, then atomically creates a hard link at the final
name. The final name cannot overwrite earlier evidence. Failed writes, flushes
or publication retain their staging file. A cleanup error after publication
leaves redundant staging evidence and does not reclassify the committed receipt
as failed. Unsupported hard links fail closed. Serialization happens before
publication, so invalid JSON cannot leave a misleading empty success file.

This strengthens all delivery receipts through the existing `create_output`
interface. It does not change their JSON schemas or acceptability rules.
Filesystem directory-entry persistence after sudden power loss is not qualified.
If storage is completely unavailable, writing a separate failure receipt can
also fail; the original exception and command log remain relevant evidence.

## Prediction checks and their limits

`phase3_delivery.prediction_integrity.validate_predictions` uses pickle-disabled
NumPy loading after checking the NPZ/NPY size envelope. It requires exactly:

* `ids`: one-dimensional, strictly increasing, unique little-endian uint64,
  with the reported bank's exact array identity and row count;
* `predicted_slots`: one-dimensional uint8, with one in-range slot per ID;
* `source_codes_in_slot_order`: int16, exactly matching the stage model's
  registered source-code order.

Prediction totals are binned by **source code**, not slot number, and compared
exactly to every column of the full 16×16 integer confusion matrix. This uses
neither reference labels nor features. It cannot reconstruct individual confusion
cells, class-conditioned errors, or prove that predictions came from a model's
forward pass. A regression deliberately permutes per-ID predictions while
preserving their totals and demonstrates that limitation. Existing model and
payload bindings remain separate requirements.

The [published-artifact audit](../../results/phase3-reliability-audit-v2/published-prediction-audit.json)
checks **288 saved prediction files**, **644,903,280 bytes**, from all **72 physical
CPU development runs** against Git-bound original receipts. All passed. The nine
aliases were not reexecuted, and no labels, features or new inference were used.
The original seed103 FTP failure and null/adverse outcomes remain preserved.

```powershell
$phase3Python = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $phase3Python -m scripts.verify_development_predictions --output results/fresh-prediction-audit.json
```

This prediction correction is an author-side delivery change. The v5 private notebook bundle contains
the matching worker and scientific sources, not these local catalog tools; no
new worker archive or notebook is required by the prediction correction.

## Byte-preserving Kaggle upload

Kaggle's [dataset documentation](https://www.kaggle.com/docs/datasets) states
that uploaded archives are expanded for notebook access. The original first
cell requires the exact `qualification.zip` file and SHA256. A transport wrapper
resolves that documented integration mismatch without reconstructing a different
ZIP or relaxing the pin. Upload the generated `.b64` file as a private Dataset,
then import the accompanying notebook; follow the
[short setup instructions](../kaggle-phase3/QUICKSTART.md).

`scripts.prepare_kaggle_upload` requires independently reviewed archive and
notebook hashes. It encodes a private verified snapshot, not a second race-prone
read of the incoming archive. The generated standard-library bootstrap bounds
encoded/decoded sizes, strictly decodes Base64, hashes the bytes actually used,
flushes the verified original ZIP and publishes it exclusively. Existing corrupt
targets and failed staging are preserved. Hashes detect changes; Base64 does
not encrypt the private data. The original 51,767,791-byte ZIP becomes a
69,023,724-byte upload, an approximately one-third size overhead.

The [preparation receipt](../../results/phase3-reliability-audit-v2/kaggle-upload/receipt.json)
binds both notebooks, archive and transport hashes. All original v5 cells are
retained; only the input ZIP path and session-clock initialization change. The
clock starts before decoding, so the existing shared budget still covers setup.
The worker source and original notebook/archive remain unchanged. The private
transport is ignored by Git; no upload or account operation occurred.

The [local mount emulation](../../results/phase3-reliability-audit-v2/kaggle-upload-emulation.json)
executes the real bootstrap and original extraction cell against the actual
transport and verifies all 82 original payload hashes. Other code cells compile
but were not executed. Six tests cover multi-block exact round trip, reuse,
tampering/truncation, an input race after preflight hashing, flush failure,
wrong pins/layout and no overwrite. The standard-library path was also tested
under local Python 3.14; the scientific environment remains pinned to 3.12.14.
This is local preparation evidence, not an observed Kaggle upload, CUDA result
or fresh-session provider recovery.

## Sustained recovery qualification

`scripts.qualify_delivery_recovery` constructs 30 fabricated count records and
five aliases. Each cycle shuffles submission order for a valid import, a rejected
payload, an alias import, a process that exits before SQL commit and a concurrent
logical export. Every sixteenth forced exit also leaves a flushed uncommitted
object inside the writer transaction. Every successful snapshot is restored and
checked against an independent prefix oracle for observations and complete
attempt history. Rolled-back attempts must never appear; preserved orphan bytes
must remain equal. Recovery reads must not change the source database.

The long attempt ended without a final completion receipt. The
[interruption audit](../../results/phase3-reliability-audit-v2/soak-interruption-audit.json)
independently verifies its 819 completed cycles and retained catalog/history.
It does **not** turn the incomplete attempt into a continuous 90-minute pass.
A [fresh bounded post-change qualification](../../results/phase3-reliability-audit-v2/soak-post-change/acceptance.json)
records its own actual duration and counts separately. The fixture seed controls test-case
selection and task submission order; OS scheduling remains nondeterministic.
The ledger hashes every cycle and its predecessor. Hash linkage detects changes
relative to its trusted final hash; it is not an authenticated log against an
administrator who can rewrite both the ledger and receipt.

The source catalog, raw objects, first and latest successful snapshot fixtures,
and failed cycles remain in the new private `tmp/` workspace. Intermediate
successful **fabricated** snapshot copies are retired after verification to
bound disk use. Every cycle's hashes remain in the durable ledger. No research
artifact is pruned. Windows process handle and working-set measurements are
observational; they do not establish Kaggle capacity or a universal memory bound.

```powershell
& $phase3Python -m scripts.qualify_delivery_recovery --seconds 60 --fixture-seed 20261026 --output results/fresh-recovery-soak --workspace tmp/fresh-recovery-soak
```

The default is 60 seconds; the command enforces 1–7,200 seconds and distinct new
evidence/workspace directories. The duration bounds starting another cycle;
an in-progress bounded verification finishes afterward. Each process is owned
by the qualifier, and subprocess waits have explicit timeouts. A failed run
retains its evidence and requires a fresh output path. This is a local Windows
concurrency/process-crash qualification. It does not simulate a physical power
loss, a corrupted disk, a network filesystem or an actual Kaggle session ending.

## Verification and provenance

The [copy benchmark](../../results/phase3-reliability-audit-v2/translation-copy-candidate-benchmark.json)
compares the original and optimized validators on the existing 72-row catalog.
Three alternating paired trials gave median process CPU times of 3.828125 and
3.59375 seconds, respectively. Every reconstructed record, alias, attempt and
missingness field was exactly equal. These are descriptive local count-audit
timings under concurrent stress, not training or GPU speed estimates. The
optimization removes a redundant deep copy of a newly parsed local dictionary;
the validators only read its nested values. No numerical formula changes.

The long interrupted qualifier used the pre-optimization count-copy revision.
The final source matches the previously benchmarked candidate exactly; the
fresh bounded qualifier and final full suite check that delivered revision.
Both source variants and the incomplete long attempt remain identifiable.

The final pinned suite discovered **123 tests: 122 passed and one POSIX FIFO
fixture was skipped on Windows**, in 392.717 seconds. The post-change qualifier
completed 19 cycles in 123.712 seconds, with 19 forced exits/rejected payloads,
62 retained attempts, five aliases and one preserved interrupted object.
The separate long attempt retains 819 completed cycles in its ledger; all
120 task-submission permutations and all four snapshot history-prefix lags
were observed. Its 5,309.758-second completed prefix is **incomplete**, and
no continuous 90-minute acceptance receipt is asserted.

Current commands, outcomes and source hashes are in
[acceptance.json](../../results/phase3-reliability-audit-v2/acceptance.json).
The pinned suite includes both existing numerical/analysis tests and the new
delivery regressions. The new tests cover publication/flush/cleanup failures,
competing receipt publishers, restore failure markers, malformed prediction
arrays and 80 seeded cases checked with an independent scalar-loop oracle.

The first targeted attempt overlapped the correction and used a weak all-zero
prediction mutation, which can coincide with a toy model's output. That attempt
is retained and is not final acceptance. The regression now changes exactly one
slot to a different valid class, guaranteeing changed count marginals. The
separate baseline execution loads the old importer from Git without reverting
the working tree and reproduces the rejection gap. No assertion was weakened.

Frozen scientific identity remains
`38830e8b9e156c5c0db8285278de4666fca1c08b1d46e033f2009ef661e9e17c`.
Worker v5 identity remains
`768b1eceb5da05904f2ac3b183df5dab2721dfc73d7f974632e13adb1463c658`.
The [protected baseline](../../results/phase3-reliability-audit-v2/baseline.json)
records 58 scientific/analysis/worker/configuration files. Scientific equations,
protocol/decision pins, the selected 12-round/1-epoch schedule, coefficients,
gates, doses, seeds and the single all_29 family are unchanged.

The existing real count catalog was also reconstructed with the corrected receipt
publisher: [restore receipt](../../results/phase3-reliability-audit-v2/published-catalog-restore.json).
This reuses its previously verified snapshot and preserves 72 physical rows,
nine aliases and 81 attempts, adding zero research trajectories.

GitHub main was checked read-only and remains at
`b77a7bbf11c1e4ae7cc06f79e5d7d7d452dbf932`. Its pinned CI run has no executed
steps: GitHub still reports an account billing lock in the
[retrieved annotation](../../results/phase3-reliability-audit-v2/hosted-pinned-ci-annotations.json).
Local success is not a hosted Linux CI pass. Changes remain on the dedicated
local branch; no default-branch push, account access or remote dispatch occurred.

The [historical preservation audit](../../results/phase3-reliability-audit-v2/historical-preservation.json)
rehashes all 7,200 original trajectory files (6,891,394,713 bytes) and 287 source
archive payloads. It checks the original nine aliases and historical 559/1,080/104
acceptance evidence without rerunning those model checks. Original evidence,
invalidated attempts and weak outcomes were not replaced.

## Engineering guidance and remaining release gates

The implementation follows concrete library contracts:

* [Python file synchronization](https://docs.python.org/3.12/library/os.html#os.fsync)
  informs flushing before publishing the final receipt name; it is not proof of
  power-loss durability on every filesystem.
* [NumPy loading](https://numpy.org/doc/2.3/reference/generated/numpy.load.html)
  supports explicit pickle-disabled array loading; bounded schemas and archive
  checks remain additional application responsibilities.
* [NumPy bin counting](https://numpy.org/doc/2.3/reference/generated/numpy.bincount.html)
  supplies exact integer marginal totals after validating slot types/ranges.

These are tested engineering practices, not an industry certification or proof
that one architecture is universally best. The architecture continues to keep
the frozen numerical engine, versioned notebook worker, verified artifacts and
author-side count registry separate. No second training implementation or new
distributed framework was introduced.

Actual CUDA semantics and clean confirmations, fresh-session provider recovery,
measured complete-job costs, final scope/adapters, runtime/data/analysis freeze
and explicit human final-grid authorization remain required. The full poisoned
EI/DR/filter matrix and final twelve paired seeds remain unexecuted. The next
experimental action is still K01/K03 on an actual Kaggle allocation using the
unchanged matching v5 notebook, followed by scientific disposition of its
evidence. This local audit grants no final/GPU release.
