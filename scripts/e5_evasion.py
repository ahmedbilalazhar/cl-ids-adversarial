from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.sequence import load_tasks
from src.discovery.pipeline import fit_threshold, recon_scores
from src.runner import train_autoencoder


def craft(ae, X: np.ndarray, lo: np.ndarray, hi: np.ndarray, sign: int, eps: float, steps: int, device: str) -> np.ndarray:
    """sign=+1 ascend recon (pollution), sign=-1 descend recon (evasion)."""
    if len(X) == 0:
        return X
    ae.eval()
    out = X.copy()
    for i in range(0, len(out), 2048):
        xb = torch.from_numpy(out[i : i + 2048]).float().to(device)
        xb.requires_grad_(True)
        for _ in range(steps):
            err = ae.recon_error(xb).sum()
            ae.zero_grad()
            if xb.grad is not None:
                xb.grad.zero_()
            err.backward()
            with torch.no_grad():
                g = xb.grad.clone()
                xb = xb + sign * eps * torch.sign(g)
                xb = torch.clamp(xb, torch.from_numpy(lo).to(device), torch.from_numpy(hi).to(device))
                xb.requires_grad_(True)
        out[i : i + 2048] = xb.detach().cpu().numpy()
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="E5: evasion of the novelty detector (attack stealth) and benign discovery pollution")
    ap.add_argument("--config", default="configs/novelty/e4_novelty_nopois.yaml")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--eps", type=float, default=0.5)
    ap.add_argument("--steps", type=int, default=5)
    ap.add_argument("--benign_sample", type=int, default=500)
    args = ap.parse_args()

    cfg = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    cfg["seed"] = args.seed
    seed = int(args.seed)
    device = str(cfg.get("device", "cpu"))
    thr_q = float((cfg.get("attack") or {}).get("threshold_quantile", 0.95))
    tasks, _label_map = load_tasks((ROOT / cfg["data"]["tasks"]).resolve())
    in_dim = tasks[0]["X_train"].shape[1]
    rng = np.random.RandomState(seed)

    per_task = []
    for t, task in enumerate(tasks):
        X_tr, y_tr = task["X_train"], task["y_train"]
        X_te, y_te = task["X_test"], task["y_test"]
        X_ae = X_tr[y_tr == 0] if (y_tr == 0).any() else X_tr
        if len(X_ae) < 64:
            X_ae = X_tr
        ae = train_autoencoder(X_ae, in_dim=in_dim, device=device, seed=seed + t)
        thr = fit_threshold(recon_scores(ae, X_tr, device=device), quantile=thr_q)
        lo, hi = X_tr.min(axis=0), X_tr.max(axis=0)

        att = np.where(y_te != 0)[0]
        ben = np.where(y_te == 0)[0]
        row: dict = {"task": t, "threshold": float(thr), "n_attack_test": len(att), "n_benign_test": len(ben)}

        if len(att):
            s_att = recon_scores(ae, X_te[att], device=device)
            novel = s_att >= thr
            row["attack_discovery_base"] = float(novel.mean())
            if novel.any():
                ev = craft(ae, X_te[att[novel]], lo, hi, sign=-1, eps=args.eps, steps=args.steps, device=device)
                s_ev = recon_scores(ae, ev, device=device)
                evaded = s_ev < thr
                row["evasion_rate"] = float(evaded.mean())
                row["n_novel_attack"] = int(novel.sum())
                row["attack_discovery_crafted"] = float((novel.sum() - evaded.sum()) / len(att))
            else:
                row["evasion_rate"] = None
                row["n_novel_attack"] = 0
                row["attack_discovery_crafted"] = float(novel.mean())
        else:
            row["attack_discovery_base"] = None
            row["evasion_rate"] = None
            row["n_novel_attack"] = 0
            row["attack_discovery_crafted"] = None

        if len(ben):
            idx = rng.choice(len(ben), size=min(args.benign_sample, len(ben)), replace=False)
            s_ben = recon_scores(ae, X_te[ben[idx]], device=device)
            novel_b = s_ben >= thr
            row["benign_discovery_base"] = float(novel_b.mean())
            pu = craft(ae, X_te[ben[idx]], lo, hi, sign=+1, eps=args.eps, steps=args.steps, device=device)
            s_pu = recon_scores(ae, pu, device=device)
            newly = (s_pu >= thr) & (~novel_b)
            row["pollution_rate"] = float(newly.mean())
            row["benign_discovery_crafted"] = float((s_pu >= thr).mean())
            row["n_benign_crafted"] = len(idx)
        else:
            row["benign_discovery_base"] = None
            row["pollution_rate"] = None
            row["benign_discovery_crafted"] = None
            row["n_benign_crafted"] = 0

        per_task.append(row)
        print(
            f"t{t} thr={thr:.3f} attNovel={row['attack_discovery_base']:.3f} "
            f"evade={row['evasion_rate']:.3f} benNovel={row['benign_discovery_base']:.3f} "
            f"pollute={row['pollution_rate']:.3f}",
            flush=True,
        )

    attack_rows = [r for r in per_task if r["n_attack_test"] > 0]
    benign_rows = [r for r in per_task if r["n_benign_test"] > 0]
    def _mean_or_none(rows, key):
        vals = [float(r[key]) for r in rows if r.get(key) is not None]
        return float(np.mean(vals)) if vals else None
    summary = {
        "seed": seed,
        "eps": args.eps,
        "steps": args.steps,
        "evasion_rate_mean": _mean_or_none(attack_rows, "evasion_rate"),
        "attack_discovery_base_mean": _mean_or_none(attack_rows, "attack_discovery_base"),
        "pollution_rate_mean": _mean_or_none(benign_rows, "pollution_rate"),
        "benign_discovery_base_mean": _mean_or_none(benign_rows, "benign_discovery_base"),
        "benign_discovery_crafted_mean": _mean_or_none(benign_rows, "benign_discovery_crafted"),
        "per_task": per_task,
    }
    out = ROOT / "results" / f"e5_evasion_seed{seed}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "per_task"}, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
