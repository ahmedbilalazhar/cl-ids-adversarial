# CPU versus Kaggle assessment — 25 October 2026

Recommendation: finish the current versioned CPU development grid locally.
Evaluate a separately qualified Kaggle worker for the larger seed matrix before
choosing that runtime. This assessment does not authorize final inference or
change the frozen study, thread count, precision, or selection rules.

At approximately07:40 local, Windows reported an Intel i7-10610U with4 cores and
8 logical processors, approximately32GB visible RAM and16.6GiB available RAM.
The active Python worker used approximately313MiB resident memory with a391MiB
process peak. The reference intentionally uses one PyTorch thread. This checks
capacity, not CPU temperature or hardware condition.

Completed unflagged12-round,1-epoch four-stage training trajectories measured:

| Learner | Runs | Median loop seconds | Observed range seconds |
|---|---:|---:|---:|
| FT |6|201.9|197.4–206.6|
| EI |6|233.9|233.0–239.3|
| DR |3|314.6|310.3–319.3|

These are recorded training-loop costs, not fresh complete-worker profiles.
Evaluation, validation/startup and export costs are reported separately by the
queued profiling tool. No additional benchmark workload was launched for this
assessment. All28 committed logical rows inspected were valid;25 had physically
trained and3 were exact aliases.

The fixed timing rule flags pilot07 DR E2-R3 and tune10 EI E4-R2/R4. Their
multi-hour wall-clock gaps are preserved; their cause has not been established.
The grid process had about89 CPU minutes accumulated across its much longer
wall-clock lifetime. The overnight delay therefore cannot be interpreted as
continuous model computation or evidence that this CPU lacks model capacity.
The declared post-grid repeat/state-comparison procedure determines comparable
replacement costs. This document does not replace those costs or receipts.

Kaggle offers GPU execution with account quotas, but an accelerator helps only
code that uses it ([official guidance](https://www.kaggle.com/docs/efficient-gpu-usage)).
The current runtime is explicitly CPU-only. A small model can also be limited by
host/kernel-launch overhead; GPU speedup is an unmeasured hypothesis for this
specific simulator ([PyTorch tuning guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html)).
CPU/GPU floating-point results need not match bitwise, even with controlled
randomness ([PyTorch numerical accuracy](https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html)).

A Kaggle qualification should pin the actual environment and device, run the
semantic/recovery checks, and measure one full FT/EI/DR worker job including
importance, replay, I/O and bundle handling. Preserve existing CPU evidence;
do not splice an arbitrary GPU continuation into the current CPU trajectory.
No Kaggle account, quota, GPU speed or cross-device equivalence was tested here.
