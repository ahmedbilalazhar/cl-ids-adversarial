"""Acceptance evidence for one trajectory and its identical recovered suffix.

This is a bounded reference acceptance command, not the legacy test suite.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .common import canonical, digest, load_state, read_json, state_identity, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--recovered", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    first, recovered = [read_json(p/"run.json") for p in (args.run, args.recovered)]
    checks = []
    def check(name, passed, evidence):
        checks.append({"name": name, "passed": bool(passed), "evidence": evidence})
    check("Complete one clean four-stage reference", first["status"] == recovered["status"] == "complete_reference"
          and first["total_commits"] == recovered["total_commits"] == 12, "3 rounds x 4 stages; recovery is the same logical run")
    check("Matched identities", first["execution"] == recovered["execution"], first["execution"])
    check("No final-test access or GPU dispatch", not first["final_test_accessed"] and not first["gpu_grid_launched"], "Reference executable is CPU-only; training package omits development/test arrays")
    admissions = [row for row in first["ledger"] if row["kind"] == "admission"]
    check("Append-only observed-label head widths", [r["expanded_head_width"] for r in admissions] == [3, 8, 13, 16], [r["expanded_head_width"] for r in admissions])
    first_checkpoints = {r["file"]: r for r in first["checkpoints"]}
    check("Recovered suffix is nonempty", bool(recovered["checkpoints"]), len(recovered["checkpoints"]))
    for row in recovered["checkpoints"]:
        expected = first_checkpoints[row["file"]]
        m1, a1 = load_state(args.run/row["file"])
        m2, a2 = load_state(args.recovered/row["file"])
        identical = m1 == m2 and set(a1) == set(a2) and all(np.array_equal(a1[k], a2[k]) for k in a1)
        check("Exact recovered state: "+row["file"], identical and state_identity(m1, a1) == row["state_identity"] == expected["state_identity"],
              "Every model/replay/admission/dropout array, cursor, counter, ledger and full PCG64 state compared")
    check("Final model equality", first["final_model_sha256"] == recovered["final_model_sha256"], first["final_model_sha256"])
    check("Recovered accounting ledger equality", first["ledger"] == recovered["ledger"], "No duplicate proposals or repeated committed transitions")
    proposal_totals = [0]*5
    for admission in admissions:
        for client in admission["clients"]:
            for quota in client["quotas"]:
                n = quota["raw"]
                expected = n if quota["protected"] else (3*n+3)//4
                check(f"DC quota E{admission['stage']} client{client['client']} source{quota['source_code']}", quota["admitted"] == expected,
                      {"raw": n, "admitted": quota["admitted"], "protected": quota["protected"]})
    for row in first["ledger"]:
        if row["kind"] != "round":
            continue
        counts = [c["admitted"] for c in row["clients"]]
        expected_weights = [float(np.float32(n/sum(counts))) for n in counts]
        check(f"FedAvg E{row['stage']} R{row['round']}", row["weights_fp32"] == expected_weights,
              "Distinct admitted-current counts; fixed increasing client order")
        for client in row["clients"]:
            i = client["client"]
            proposal_totals[i] += client.get("proposals", 0)
            expected_proposals = client["admitted"] if row["round"] == 1 else 0
            check(f"Stream/Adam E{row['stage']} R{row['round']} client{i}",
                  client.get("proposals", 0) == expected_proposals and (client["inactive"] or client["adam_reset"]),
                  "One proposal per admitted first-pass record; fresh optimizer each broadcast")
    check("Replay independent of current short batch", sum(c.get("full_replay_with_short_current_batches", 0)
          for row in first["ledger"] if row["kind"] == "round" for c in row["clients"]) > 0,
          "Observed 128 replay records on batches with fewer than 128 current records")
    final = first["checkpoints"][-1]
    meta, arrays = load_state(args.run/final["file"])
    for i, info in enumerate(meta["clients"]):
        size = info["size"]
        ids = arrays[f"client{i}.ids"][:size]
        width = arrays[f"client{i}.width"][:size]
        check(f"Reservoir client{i}", info["seen"] == proposal_totals[i] and size == min(500, info["seen"])
              and np.unique(ids).size == size and np.all((width > 0) & (width <= 16)),
              {"seen": info["seen"], "occupancy": size, "unique_ids": int(np.unique(ids).size)})
        check(f"Lossless PCG64 representation client{i}", all(isinstance(v, str) for name in ["draw", "insert"] for v in info[name]["state"].values()),
              "128-bit state integers serialized as decimal strings")
    result = {"status": "passed" if all(c["passed"] for c in checks) else "failed", "checks": checks,
              "reference_run_sha256": digest(args.run/"run.json"), "recovered_run_sha256": digest(args.recovered/"run.json"),
              "scope": "Executed clean DR+DC CPU reference and exact round-boundary suffix recovery, not full grid qualification",
              "remaining_gates": ["FT/EI/DM/DQ and poisoning/control acceptance", "CPU/GPU agreement and profiling", "Clean development pilots/tuning", "Final scope/runtime lock"]}
    write_json(args.output, result)
    print(canonical({"status": result["status"], "checks": len(checks), "failures": [c for c in checks if not c["passed"]]}))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
