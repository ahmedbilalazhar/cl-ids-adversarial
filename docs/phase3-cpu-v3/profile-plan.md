# Complete CPU worker-job profiling plan

24 October 2026. After the fixed development grid, timing disposition and control
verification, run one fresh CPU worker process for each FT,EI,DR at seed101 and
its selected feasible settings. If a learner has no feasible selection, use its
fixed pilot defaults and label it unqualified engineering profiling. Do not pick
the best infeasible score. These are three measured verification executions of
existing conditions, not new independent replicates or extra tuning.

Each worker includes interpreter/library startup, exact package validation,
complete four-stage training/checkpoints, independent development evaluation,
local bundle export and hashing. Compare every committed scientific state and
all evaluation stages to the matching original condition before claiming
equivalent work. Record peak process working-set memory when supported; report
an unavailable measurement explicitly rather than zero.

At E4, benchmark fixed first1/256 development feature rows in eval/no-grad mode,
20 warmups and100 measured calls per batch shape. Record individual call times,
mean/median/p95 and fixed batch-ID hashes. No training stream or final feature
is consumed. This is local CPU inference latency on this batch, not deployed
traffic latency or a GPU estimate.

For communication, record raw FP32 parameter bytes and actual uncompressed NPZ
serialization sizes for a concrete model-message template at each head width.
Show active-client-only and all-five-client downlink scenarios, active update
uplinks, and an explicitly separate potential EI final-anchor downlink. The
sequential simulator has no network transport; these are logical payload and
serialization accounting, not measured wire latency/bandwidth. Do not mistake
the central checkpoint's replay/importance state for a per-round model message.
Report actual checkpoint/prediction/local export bytes separately.

Keep all physical durations, source identities and measured costs. Profiling
does not replace the tuning tie costs or take a favorable timing minimum.
The timing disposition's controlled remeasurement is a separately versioned
procedure. Cold dependency installation, remote uploads and eventual GPU worker
jobs remain unmeasured and cannot be forecast as completed work.
