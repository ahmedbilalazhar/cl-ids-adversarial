# Development result registry and synthetic analysis contract

Continuation v2, 25 October 2026. This implements the local result-collection
boundary identified in K05. Final experiment scope, target runtime and human
authorization remain unresolved. There is no final import or dispatch mode.

## Storage and identity

`phase3_delivery.catalog` uses a local SQLite database with explicit
`BEGIN IMMEDIATE` transactions, `synchronous=FULL`, unique physical-condition
keys and separate alias records. A retry with exactly the registered payload is
idempotent and adds zero trajectories. Changed payloads, unknown runs and aliases
whose parent has not been imported are rejected. Each successful or rejected
registered import appends an attempt record; it never replaces an earlier result.

Before initialization, the caller supplies the SHA256 of an independently
reviewed import manifest. The database embeds its exact bytes. Every operation
checks that external hash, validates source/protocol/taxonomy/settings bindings,
and accepts only development seeds101–103 or explicit fabricated synthetic
fixtures. The caller must not derive this trust pin from an incoming worker's
self-declared identity. Actual Kaggle exports still require `handoff.inspect`
before count ingestion; this catalog does not replace checkpoint verification.

The manifest specifies every physical run, metric hash and optional CPU sidecar
hash; aliases name a physical parent without chains or cycles. Its arm must agree
with the learner/admission policy. Unsupported intervention names are rejected.

Input bytes are copied into a content-addressed sibling `.objects` directory,
flushed, and published by an atomic hard link before the database commit. Hashes
are checked on publication and on every verification. A crash can leave unused
objects; verification lists them without deleting or counting them. Keep the
database **and** its object directory together. SQLite and filesystem durability
depend on the storage implementation; this local test does not qualify Kaggle
session persistence or a network-mounted database.

`verify_catalog` reruns integer-count validation from the stored metric bytes,
checks the separate CPU run sidecar where applicable, compares reconstructed
endpoints to the database, and checks SQLite integrity and foreign keys. Its
report explicitly lists missing runs, aliases, attempts and unreferenced files.
The attempt API is append-only; the database is not an authenticated audit log
against a person who can arbitrarily edit local files. The externally pinned
manifest and retained raw payloads protect result-identity validation.

Manifest validation caches only approval of immutable JSON bytes and the three
bound configuration hashes. Returned row dictionaries are freshly parsed.
Changing a bound configuration invalidates approval. This removes repeated
whole-manifest validation without relaxing payload or identity checks.

SQLite's transaction model is described in its [atomic commit documentation](https://www.sqlite.org/atomiccommit.html).
Connections are explicitly closed: Python's connection context manager manages
transactions but does not close the connection, as documented in the
[Python SQLite guide](https://docs.python.org/3.12/library/sqlite3.html#how-to-use-the-connection-context-manager).

## Interfaces

Run commands from the repository root using the pinned reference interpreter.
Use fresh output paths so earlier receipts survive.

```powershell
$py = '.\tmp\phase3-reference-env\Scripts\python.exe'
& $py -m phase3_delivery.catalog init --database tmp/catalog.sqlite --manifest reviewed-manifest.json --manifest-sha256 REVIEWED_SHA256 --output results/catalog-init.json
& $py -m phase3_delivery.catalog ingest --database tmp/catalog.sqlite --manifest-sha256 REVIEWED_SHA256 --run-id REGISTERED_ID --metrics downloaded/metrics.json --run-manifest downloaded/run.json --output results/catalog-import-001.json
& $py -m phase3_delivery.catalog verify --database tmp/catalog.sqlite --manifest-sha256 REVIEWED_SHA256 --output results/catalog-verified.json
& $py -m phase3_delivery.assemble --database tmp/catalog.sqlite --manifest-sha256 REVIEWED_SHA256 --output results/catalog-summary.json
```

Omit `--run-manifest` for Kaggle metrics, which embed execution identity. CPU
metrics require that separately hashed complete from-start run manifest.
Output receipts use exclusive creation and failed CLI attempts retain their
exception. Do not copy an open SQLite file as a portable snapshot; use the
verified JSON export as evidence and reconstruct the database from its pinned
manifest and raw artifacts, or use an explicitly qualified SQLite backup method.

For the already published CPU delivery, the supported import driver verifies
completion and every receipt against commit b77a7bb, then checks metric/run bytes
against the receipt inventory. Historical Windows paths are relocated under the
current repository's development tree; escape paths are rejected. No feature or
checkpoint file is loaded.

```powershell
& $py -m phase3_delivery.development --database tmp/phase3-count-catalog-v2/catalog.sqlite --output results/phase3-continuation-v2/development-final
```

## Analysis boundary

Development catalogs retain a separate endpoint row for each physical pilot or
tuning profile. They do not pool different settings as additional seeds and do
not run the final inferential family.

Only fabricated synthetic catalogs exercise the twelve-seed assembler. It joins
each poisoned condition to its same-arm/same-seed clean reference, requires the
same banks and denominators, rejects mixed execution profiles within a paired
seed, and requires matching training data across arms at each seed/dose. It
computes H and immediate recall change once, then delegates the unchanged
29 contrasts, exact signed-rank/Holm calculations and bootstrap to the frozen
analysis engine. Missing clean references remain unavailable; available A/FAR
counts remain descriptive rather than becoming invented security endpoints.

The full integration fixture contains **240 fabricated count trajectories**
(five arms × four doses × twelve seed labels), no model training or final-test
records. It verifies all29 contrasts, all-zero effects and missing-seed handling.
Removing the FT clean reference for seed42 leaves twelve affected contrasts
unavailable in the same all_29 family. These fabricated null outcomes provide
software acceptance evidence, not a research finding.

## Acceptance and remaining work

Tests cover two competing import processes, an abrupt process exit before SQL
commit, retry and alias idempotency, damaged identities and stored endpoints,
orphan visibility, failed-receipt preservation, manifest amendments and final-mode
rejection. A Windows fixture initially left a direct SQLite connection open;
the failed log is retained and the fixture now closes it explicitly. The first
slow intermediate test was stopped after profiling redundant manifest hashing;
it is not reported as passed.

This completes a development/synthetic registry and assembler. The final registry
must still be derived from an explicitly adopted scope and target runtime. Actual
provider durability, GPU qualification, final-grid authorization and final
artifact/analysis gates remain closed.


## Verified v5 worker import

`phase3_delivery.worker_import` is the combined path for returned v5 development
exports. A reviewed registry must already bind every run, exact metric payload
and execution identity. Supply a JSON list of objects with exactly `run_id`,
`job_prefix` and `metrics_path`; for example the registered seed101 FT ID, `FT`,
and `FT-development/metrics.json`. Do not derive trust pins from incoming metadata.

```powershell
& $py -m phase3_delivery.worker_import --database tmp/catalog.sqlite --manifest-sha256 REVIEWED_REGISTRY_SHA256 --archive downloaded/output.zip --archive-sha256 NOTEBOOK_EXPORT_SHA256 --mapping reviewed-mapping.json --output results/import-attempt-001.json
```

The importer verifies one private archive snapshot, bounds JSON/NPZ size and
shape claims, rejects object arrays, verifies checkpoint lineage and checks
evaluation commits/model tensors. All mapped counts validate before the first
write; observations commit independently. An I/O failure identifies already
accepted IDs for idempotent retry. CLI failures retain a fresh failure receipt.

Count checks now include displayed class/binary/provenance rates and labels.
Exact canonical comparisons distinguish metadata booleans and integers. CPU
sidecar schemas/parents, persisted retry conditions and alias parents are checked.
Hashing and parsing use the same bounded snapshot. All 72 CPU observations and
nine aliases pass the stricter validator.

The [nonzero fabricated oracle](../../results/phase3-two-hour-audit-v1/nonzero-oracle-final.json)
verifies 348 paired values in all_29. Removing one FT clean reference leaves
12 contrasts unavailable without changing family membership. These are software
fixtures, not research outcomes.


## Portable count-catalog recovery

Use `python -m phase3_delivery.snapshot export` and `restore` for logical
count-catalog recovery; see the [procedure and evidence](../phase3-cpu-v3/recovery-improvements-2026-10-25.md).
Snapshots include the reviewed manifest, observations, aliases, all attempts and
raw objects, including orphans. Restore builds and verifies a fresh catalog,
retains attempt IDs and adds zero research trajectories. Only
`restore.commit.json` marks completion; partial destinations are preserved and
never overwritten. Unknown schema extensions/counters reject. This does not
replace training-checkpoint recovery or qualify provider/power-loss durability.

Worker mappings now validate before archive work and place physical parents
before aliases without changing caller input. A missing parent must already
exist in the catalog or be explicitly included in the batch.
