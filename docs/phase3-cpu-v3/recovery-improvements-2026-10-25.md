# Catalog recovery and import improvements

Continuation requested for 30 minutes, 25 October 2026, starting 15:24:38 UTC.
Baseline: `8af4460`; branch: `codex/phase3-continuation-readiness`.
Actual finish and test results are recorded in
[completion.json](../../results/phase3-recovery-improvements-v1/completion.json).

The frozen scientific engine and v5 Kaggle worker are unchanged. This work adds
author-side count-catalog recovery and corrects import ordering. Actual Kaggle
CPU/CUDA qualification, provider durability, final scope and final authorization
remain outstanding. No research condition or final-test inference was executed.

## Verified catalog snapshots and restores

`phase3_delivery.snapshot` exports a logical snapshot while holding the SQLite
writer slot. It verifies the catalog, captures its reviewed manifest, physical
observations, aliases and complete attempt history, and includes every raw object,
including unreferenced failure artifacts. It checks the written ZIP's metadata
and payload hashes before returning a success receipt. Fixed archive metadata
makes repeat exports of unchanged state deterministic in the tested runtime.

Restore requires two independently obtained pins: the export archive SHA256 and
the reviewed import-manifest SHA256. It verifies a private archive copy, rejects
extra/unsafe entries and bounded-size violations, builds a fresh database from
the supported schema, restores exact raw objects and attempt IDs, then reruns
integer-count validation. It never opens an incoming SQLite binary database.

Publication reserves a new destination directory. Only `restore.commit.json`
marks a complete restore. A failure during publication leaves the partial
directory and `restore.failed.json`; a retry must use a fresh destination.
Existing destinations and archives are never replaced. Unrecognized database
extensions and nonstandard attempt counters are rejected rather than silently
discarded or changing the next attempt ID.

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m phase3_delivery.snapshot export --database tmp/catalog.sqlite --manifest-sha256 REVIEWED_MANIFEST_SHA256 --archive tmp/catalog-backup-001.zip --output results/catalog-export-001.json
& $py -m phase3_delivery.snapshot restore --archive tmp/catalog-backup-001.zip --archive-sha256 TRUSTED_EXPORT_SHA256 --manifest-sha256 REVIEWED_MANIFEST_SHA256 --destination tmp/restored-catalog-001 --output results/catalog-restore-001.json
```

The [actual CPU catalog export](../../results/phase3-recovery-improvements-v1/cpu-catalog-export.json)
contains 72 physical observations, nine aliases, 81 attempts and 144 objects.
Its 19,018,187 uncompressed bytes occupy 1,980,850 archive bytes. The
[restoration check](../../results/phase3-recovery-improvements-v1/cpu-catalog-restore.json)
found identical verification results and logical table contents. This is a
reconstruction of existing evidence and adds zero research trajectories.

This is a count-catalog backup, not training-checkpoint or whole-project recovery.
It does not qualify Kaggle storage, a network filesystem or recovery after a
physical power loss. Files are flushed, but guarantees still depend on storage
and operating-system behavior. Retain the original archive and trusted receipt.

SQLite's [transaction documentation](https://www.sqlite.org/lang_transaction.html)
supports the single-writer consistency strategy. The implementation reads an
explicit ZIP inventory instead of extracting arbitrary names, following the
validation concerns in the [Python ZIP documentation](https://docs.python.org/3.12/library/zipfile.html#zipfile.ZipFile.extractall).

## Import ordering and validation

A valid worker batch failed when an alias preceded its physical parent. The
[pre-fix reproduction](../../results/phase3-recovery-improvements-v1/alias-order-reproduction.log)
retains that failure. `prepare_mapping` now validates exact mapping fields, types,
run IDs, duplicate IDs and paths before archive processing, and makes a separate
ordered copy with physical parents before aliases. Caller input is unchanged.
An alias requires its physical parent in the batch or existing catalog. Retries
and aliases still add zero independent trajectories.

Observation commits remain independently transactional: this does not make a
multi-row batch atomic. A storage failure can leave earlier verified rows,
which the existing failure receipt identifies for idempotent retry.

## Validation and preserved attempts

The expanded pinned suite covers empty and populated recovery, retries, aliases,
missing rows, orphan visibility, deterministic export, writer exclusion,
corruption, traversal/extra entries, unsupported schemas/counters, partial
publication and failed CLI receipt preservation. Toy FT/EI/DR archive integration
also covers alias-first batches. Current results and source hashes are in
[acceptance.json](../../results/phase3-recovery-improvements-v1/acceptance.json).

The first snapshot test failed because Windows cannot flush a read-only file
descriptor; the archive is now flushed through a writable handle. Its failed log
is retained. An ad-hoc actual-catalog report also failed to JSON-encode exact
Fractions after restoration had succeeded; the reporting retry used the existing
restore and the established exact-value encoder. Neither failure reran a model.

The [earlier two-hour audit](two-hour-implementation-audit.md) remains historical
evidence. Its source and test snapshots describe that earlier revision. The
current continuation does not change the scientific identity, worker identity,
selected settings, seeds, gates or single all_29 comparison family.
