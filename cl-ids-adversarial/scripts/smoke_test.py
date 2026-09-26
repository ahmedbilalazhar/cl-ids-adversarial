from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cl.base import set_seed, to_loader
from src.cl.derpp import DERpp
from src.cl.er import ExperienceReplay
from src.cl.ewc import EWC
from src.cl.finetune import FineTune
from src.cl.lwf import LwF
from src.metrics import backward_transfer, forgetting, summarize
from src.models.mlp import TabularMLP
from src.attacks.flip import label_flip
from src.defenses.purification import small_loss_filter


def make_synthetic_tasks(n_tasks: int = 5, n_features: int = 20, samples: int = 400, seed: int = 0):
    rng = np.random.RandomState(seed)
    tasks = []
    n_classes_total = 1 + (n_tasks - 1) * 2
    for t in range(n_tasks):
        n_cls = 1 if t == 0 else 2
        labels = [0] if t == 0 else [1 + 2 * (t - 1), 2 + 2 * (t - 1)]
        if t == 0:
            y = np.zeros(samples, dtype=np.int64)
            X = rng.randn(samples, n_features) * 0.5 + 1.0
        else:
            y = np.concatenate(
                [
                    np.full(samples // 2, labels[0], dtype=np.int64),
                    np.full(samples - samples // 2, labels[1], dtype=np.int64),
                ]
            )
            X = rng.randn(samples, n_features)
            for li, lab in enumerate(labels):
                X[y == lab] += (li + 1) * 2.5
            if t >= 1:
                n_ben = samples // 4
                Xb = rng.randn(n_ben, n_features) * 0.5
                X = np.vstack([X, Xb])
                y = np.concatenate([y, np.zeros(n_ben, dtype=np.int64)])
        idx = rng.permutation(len(y))
        X, y = X[idx].astype(np.float32), y[idx]
        split = int(0.7 * len(y))
        tasks.append(
            {
                "day": f"synthetic_{t}",
                "labels": [str(int(v)) for v in np.unique(y)],
                "X_train": X[:split],
                "y_train": y[:split],
                "X_test": X[split:],
                "y_test": y[split:],
            }
        )
    return tasks, {str(i): i for i in range(n_classes_total + 2)}


def run_method(cls, tasks, n_classes, seed=42, epochs=2, batch_size=64, **kwargs):
    set_seed(seed)
    in_dim = tasks[0]["X_train"].shape[1]
    model = TabularMLP(in_dim, n_classes)
    method = cls(model, lr=1e-3, device="cpu", **kwargs)
    R = np.zeros((len(tasks), len(tasks)))
    for t in range(len(tasks)):
        loader = to_loader(tasks[t]["X_train"], tasks[t]["y_train"], batch_size=batch_size)
        bound = int(max(n_classes, tasks[t]["y_train"].max() + 1))
        method.before_task(t, loader, class_bound=bound)
        method.train_task(loader, epochs=epochs)
        method.after_task(t, loader)
        for j in range(t + 1):
            pred = method.predict(tasks[j]["X_test"])
            R[t, j] = float(np.mean(pred == tasks[j]["y_test"]))
    return R


def main():
    print("=== smoke_test: harness validation (synthetic data, no CICIDS2017) ===")
    tasks, label_map = make_synthetic_tasks()
    n_classes = int(max(label_map.values())) + 2

    results = {}
    for name, cls, kw in [
        ("finetune", FineTune, {}),
        ("ewc", EWC, {"ewc_lambda": 10.0}),
        ("lwf", LwF, {}),
        ("er", ExperienceReplay, {"buffer_size": 200}),
        ("derpp", DERpp, {"buffer_size": 200}),
    ]:
        R = run_method(cls, tasks, n_classes=n_classes, seed=42, **kw)
        s = summarize(R)
        results[name] = s
        print(f"{name:10s} acc={s['acc']:.3f} bwt={s['bwt']:.3f} F={s['forgetting']:.3f}")
        assert R.shape == (len(tasks), len(tasks))
        assert np.all(np.isfinite(R))

    assert results["finetune"]["forgetting"] >= 0.0
    print("OK: task-accuracy matrix finite for all baselines")

    y = tasks[2]["y_train"]
    y_flip, flipped = label_flip(y, budget=0.1, mode="random", seed=0)
    assert flipped.sum() > 0
    print(f"OK: label_flip flipped {flipped.sum()}/{len(y)} samples")

    model = TabularMLP(tasks[0]["X_train"].shape[1], n_classes)
    keep = small_loss_filter(model, tasks[2]["X_train"], tasks[2]["y_train"], keep_ratio=0.75)
    assert keep.sum() > 0
    print(f"OK: small_loss_filter kept {keep.sum()}/{len(keep)} samples")

    print("=== SMOKE TEST PASSED ===")


if __name__ == "__main__":
    main()
