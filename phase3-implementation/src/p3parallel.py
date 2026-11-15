"""Parallel experiment runner for p3lib.

Each worker is a separate process (spawn) that loads the data once, keeps it on its device, and runs one experiment at a time.
GPU mode: workers share the visible GPU(s) round-robin. Every run is written to its own JSON file, so a stopped session resumes
by skipping finished runs. Results of different devices are never mixed inside one comparison (the device is stored in every file).
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import time
import traceback
from dataclasses import asdict

_G = {}


def _init(ctx):
    import torch
    import p3lib as L
    idx = (mp.current_process()._identity or (1,))[0] - 1
    device = "cpu"
    if ctx["device"] == "cuda":
        if not torch.cuda.is_available(): raise RuntimeError("device='cuda' requested but CUDA is not available")
        device = f"cuda:{idx % torch.cuda.device_count()}"
    torch.set_num_threads(ctx["threads"])
    _G.update(ctx=ctx, device=device, L=L, tax=L.load_taxonomy(ctx["tax_path"]), dev=L.load_dev(ctx["dev_dir"]), stages={})


def _task(job):
    cfg_dict, out_path = job
    L, ctx = _G["L"], _G["ctx"]
    t0 = time.time()
    try:
        cfg = L.Cfg(**cfg_dict)
        if cfg.seed not in _G["stages"]:                      # keep one seed in memory at a time (12 seeds would not fit otherwise)
            _G["stages"].clear(); L._UPLOADS.clear()
            _G["stages"][cfg.seed] = L.load_stages(ctx["pkg_dirs"][str(cfg.seed)])
        r = L.run(cfg, _G["stages"][cfg.seed], _G["dev"], _G["tax"], threads=ctx["threads"], device=_G["device"])
        tmp = out_path + ".tmp"
        with open(tmp, "w") as f: json.dump(r, f)
        os.replace(tmp, out_path)
        return ("ok", os.path.basename(out_path), time.time() - t0, _G["device"])
    except Exception:
        return ("error", os.path.basename(out_path), traceback.format_exc(), _G["device"])


def run_grid(cfgs, out_dir, ctx, workers=4):
    """ctx: dict(device='cpu'|'cuda', threads=int, tax_path=..., dev_dir=..., pkg_dirs={'101': train_dir, ...})."""
    os.makedirs(out_dir, exist_ok=True)
    tags = [c.tag() for c in cfgs]
    assert len(set(tags)) == len(tags), "duplicate experiment tags in the grid"
    jobs = [(asdict(c), os.path.join(out_dir, f"{c.tag()}.json")) for c in cfgs]
    todo = sorted((j for j in jobs if not os.path.exists(j[1])), key=lambda j: j[0]["seed"])   # same-seed jobs run together
    print(f"{len(jobs)} runs in the grid, {len(jobs) - len(todo)} already finished, {len(todo)} to run on {workers} worker(s) [{ctx['device']}]", flush=True)
    if not todo: return {"ok": 0, "error": 0, "skipped": len(jobs)}
    t0, ok, errors, times = time.time(), 0, [], []
    with mp.get_context("spawn").Pool(min(workers, len(todo)), initializer=_init, initargs=(ctx,)) as pool:
        for status, name, info, dev in pool.imap_unordered(_task, todo):
            if status == "ok":
                ok += 1; times.append(info); eta = (len(todo) - ok - len(errors)) * (time.time() - t0) / max(ok + len(errors), 1)
                print(f"[{ok + len(errors)}/{len(todo)}] {name} {info:.0f}s on {dev} | elapsed {time.time() - t0:.0f}s, ETA {eta:.0f}s", flush=True)
            else:
                errors.append((name, info)); print(f"[ERROR] {name} on {dev}\n{info}", flush=True)
    summary = {"ok": ok, "error": len(errors), "skipped": len(jobs) - len(todo), "wall_seconds": time.time() - t0,
               "mean_run_seconds": sum(times) / len(times) if times else None}
    print("grid finished:", summary, flush=True)
    if errors: raise RuntimeError(f"{len(errors)} run(s) failed; first: {errors[0][0]}\n{errors[0][1]}")
    return summary
