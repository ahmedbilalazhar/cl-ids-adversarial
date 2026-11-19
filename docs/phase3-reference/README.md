
## Inference cost characterization

`benchmark_reference_inference.py` measures forward-pass-only latency for each of the four accepted reference checkpoints on the recorded one-thread CPU runtime. It uses 10 warmups and 100 measured calls for batch sizes 1 and 256, and writes raw observations plus a summary under `evidence/inference-latency/`. Batch-1 median latency is 62.6–64.1 microseconds/record; batch-256 median latency is 0.181–0.196 milliseconds/batch (0.706–0.764 microseconds/record). These measurements exclude preprocessing, data loading, serialization, network transport and queueing; they do not establish deployment throughput or general hardware performance. Process RSS, communication bytes, energy and training component costs remain unmeasured.


**Status note (17 Nov 2026):** the lambda_z=.5 trajectory described here is a separate one-seed implementation reference. It is not the later 240-run adopted-profile CPU extension, which used the historically selected DR lambda_z=.1 and is documented in [`submissions/phase3-overnight/appendix.md`](../../submissions/phase3-overnight/appendix.md) with its independent audit at [`docs/phase3-plan/phase3-overnight-independent-audit.json`](../phase3-plan/phase3-overnight-independent-audit.json). Neither evidence track includes held-out outcomes.
