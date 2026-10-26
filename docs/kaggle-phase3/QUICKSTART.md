# Run the Phase 3 qualification on Kaggle

**Next action: qualification, before the final twelve-seed experiment.**

1. Create a **private** Kaggle Dataset containing
   [qualification.zip.b64](../../results/phase3-reliability-audit-v2/kaggle-upload/qualification.zip.b64).
   This local file is about 69 MB and is intentionally excluded from Git.
   Kaggle automatically extracts uploaded archives, according to its
   [dataset documentation](https://www.kaggle.com/docs/datasets). This encoded
   transport restores the exact reviewed ZIP and checks both hashes; it does not
   change the worker or scientific source. Base64 is encoding, not encryption.

2. Import [phase3-kaggle-start.ipynb](../../results/phase3-reliability-audit-v2/kaggle-upload/phase3-kaggle-start.ipynb)
   into a private Kaggle notebook. Attach the private Dataset and enable Internet
   for the isolated dependency setup. In the first code cell, set
   `ENCODED_BUNDLE` to the attached file's actual `/kaggle/input/...` path.

3. In the existing v5 configuration cell, use `DEVICE = 'cpu'` and
   `RUN_FULL_DATA = False`. Set `SESSION_REMAINING_SECONDS` from the actual
   remaining session allowance; 7,200 is an example, not a quota guarantee.
   Run all cells and retain `synthetic-acceptance.json`, the exported output ZIP
   and its adjacent receipt. Require `status: passed`; preserve any failure.

4. Start a separate GPU qualification allocation using
   **Settings → Accelerator → GPU**, as described in Kaggle's
   [notebook documentation](https://www.kaggle.com/docs/notebooks). Set
   `DEVICE = 'cuda:0'`, keep `RUN_FULL_DATA = False`, and rerun the notebook.
   The worker creates a separate pinned CUDA environment and output directory.
   Require actual CUDA fixture success. After reviewing those receipts, enable
   `RUN_FULL_DATA = True` for the already authorized **clean seed101 FT/EI/DR
   development confirmations**. This flag cannot run final seeds.

The [local transport emulation](../../results/phase3-reliability-audit-v2/kaggle-upload-emulation.json)
restored the exact original archive and verified its 82 payload files. This does
not prove that the upload or CUDA run has succeeded on Kaggle. The original v5
notebook/bundle remain archived unchanged. The shared session clock includes
decoding, extraction, setup, tests, confirmation and saving. Save and download
the outputs before ending the session; follow K03 in the
[execution contract](../phase3-plan/kaggle-execution-contract.md) to verify
fresh-session restore/resume and state/prediction parity.

If the local upload files are absent after cloning, regenerate them from the
reviewed private bundle; Git intentionally contains no copy of the private data:

```powershell
python -m scripts.prepare_kaggle_upload --archive results/phase3-two-hour-audit-v1/candidate-v5/bundle-final/qualification.zip --archive-sha256 51fa652d5b47de0d2e7935b861988ac7ed7d1abd8526fb2d82196ff23527fa7b --notebook results/phase3-two-hour-audit-v1/candidate-v5/notebook-final/phase3-qualification.ipynb --notebook-sha256 54db44c770fc73c7f398ae9fe09220a2383bf65a99a2dcee5af9a4c272a4c214 --output results/phase3-reliability-audit-v2/kaggle-upload
```

Use a fresh output directory if that destination already exists. The script
checks both reviewed pins and never uploads or starts a remote job.

## How complete is Phase 3?

| Milestone | Verified progress |
|---|---|
| CPU v3 development delivery | **100% of its declared scope:** 81 logical rows, 72 physical runs and nine aliases |
| Actual Kaggle/CUDA qualification and fresh-session recovery | **Pending:** local tests do not count as provider evidence |
| Final twelve paired seed blocks | **0/12 completed — 0%** |
| Final-grid authorization | **Not ready / not granted** |

A single overall completion percentage would be misleading: the final scope has
not been adopted, and the cost of target-runtime qualification is unmeasured.
The remaining work is concrete: actual CUDA semantics/clean checks, saved-session
recovery, complete-job cost measurement, final scope and missing intervention
adapters, source/data/runtime/analysis freeze, then explicit final authorization.
Core software improvements alone cannot satisfy those experimental gates.

See the [current reliability audit](../phase3-cpu-v3/reliability-audit-2026-10-26.md)
for changes, exact validation and limitations. Do not start the final study with
the qualification notebook or silently substitute unimplemented interventions.
