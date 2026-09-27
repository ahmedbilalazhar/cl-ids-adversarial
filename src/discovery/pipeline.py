from __future__ import annotations

import numpy as np
import torch
from sklearn.cluster import HDBSCAN

from src.models.mlp import Autoencoder


def recon_scores(
    ae: Autoencoder,
    X: np.ndarray,
    device: str = "cpu",
    batch: int = 4096,
) -> np.ndarray:
    ae.eval()
    out: list[np.ndarray] = []
    with torch.no_grad():
        for i in range(0, len(X), batch):
            xb = torch.from_numpy(X[i : i + batch]).float().to(device)
            out.append(ae.recon_error(xb).cpu().numpy())
    if not out:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(out).astype(np.float32)


def fit_threshold(clean_scores: np.ndarray, quantile: float = 0.95) -> float:
    if clean_scores.size == 0:
        return 0.0
    return float(np.quantile(clean_scores, quantile))


def cluster_novel(
    X_novel: np.ndarray,
    min_cluster_size: int = 15,
    min_samples: int = 5,
) -> np.ndarray:
    n = len(X_novel)
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    if n < max(min_cluster_size, min_samples + 1):
        return np.full(n, -1, dtype=np.int64)
    mcs = int(min(min_cluster_size, max(2, n // 4)))
    ms = int(min(min_samples, mcs))
    labels = HDBSCAN(min_cluster_size=mcs, min_samples=ms, copy=True).fit_predict(X_novel)
    return labels.astype(np.int64)


def evaluate_discovery(
    ae: Autoencoder,
    threshold: float,
    X_tr: np.ndarray,
    y_tr: np.ndarray,
    poison_mask: np.ndarray,
    X_te: np.ndarray,
    y_te: np.ndarray,
    device: str = "cpu",
    min_cluster_size: int = 15,
    benign_label: int = 0,
) -> dict:
    """Discovery-stage metrics for Option 2-A / H2.

    Train novel candidates = recon >= threshold on (possibly poisoned) stream.
    Test novel candidates  = recon >= threshold on test set.
    HDBSCAN is fit on the joint set so poison-dominated train clusters can
    absorb benign or attack test points (fictitious class / missed detection).
    """
    scores_tr = recon_scores(ae, X_tr, device=device)
    scores_te = recon_scores(ae, X_te, device=device)
    novel_tr = scores_tr >= threshold
    novel_te = scores_te >= threshold
    poison_mask = np.asarray(poison_mask, dtype=bool)

    attack_te = y_te != benign_label
    benign_te = y_te == benign_label

    n_attack = int(attack_te.sum())
    n_benign = int(benign_te.sum())
    n_poison = int(poison_mask.sum())
    poison_novel = int((poison_mask & novel_tr).sum()) if n_poison else 0

    idx_tr = np.where(novel_tr)[0]
    idx_te = np.where(novel_te)[0]
    if len(idx_tr) + len(idx_te) == 0:
        X_joint = np.zeros((0, X_tr.shape[1]), dtype=X_tr.dtype)
    else:
        X_joint = np.concatenate([X_tr[idx_tr], X_te[idx_te]], axis=0)
    labels_joint = cluster_novel(X_joint, min_cluster_size=min_cluster_size)
    n_tr_joint = len(idx_tr)
    lab_tr = labels_joint[:n_tr_joint]
    lab_te_novel = labels_joint[n_tr_joint:]
    lab_te_full = np.full(len(y_te), -1, dtype=np.int64)
    lab_te_full[idx_te] = lab_te_novel

    clusters = sorted({int(c) for c in lab_tr if c >= 0})
    poison_frac: dict[int, float] = {}
    for c in clusters:
        members = lab_tr == c
        if members.any() and n_poison:
            poison_frac[c] = float(poison_mask[idx_tr[members]].mean())
        else:
            poison_frac[c] = 0.0
    fictitious = sorted(c for c, f in poison_frac.items() if f >= 0.5)

    miss_rate = 0.0
    noise_attack = 0.0
    absorbed_attack = 0.0
    clustered_attack = 0.0
    if n_attack:
        miss_rate = float((~novel_te[attack_te]).mean())
        novel_att = attack_te & novel_te
        if novel_att.any():
            lab_a = lab_te_full[novel_att]
            noise_attack = float((lab_a < 0).mean())
            absorbed_attack = float(np.isin(lab_a, fictitious).mean()) if fictitious else 0.0
            clustered_attack = float((lab_a >= 0).mean())

    absorb = 0.0
    if n_benign and fictitious and (novel_te & benign_te).any():
        lab_b = lab_te_full[novel_te & benign_te]
        absorb = float(np.isin(lab_b, fictitious).mean())

    noise_te = float((lab_te_novel < 0).mean()) if len(lab_te_novel) else 0.0
    clean_novel_rate = 0.0
    clean = ~poison_mask
    if clean.any():
        clean_novel_rate = float(novel_tr[clean].mean())

    return {
        "threshold": float(threshold),
        "n_clusters": len(clusters),
        "n_fictitious": len(fictitious),
        "poison_novel_rate": poison_novel / n_poison if n_poison else 0.0,
        "clean_novel_rate": clean_novel_rate,
        "discovery_miss_rate": miss_rate,
        "noise_rate_attack": noise_attack,
        "absorbed_attack_rate": absorbed_attack,
        "clustered_attack_rate": clustered_attack,
        "fictitious_absorption": absorb,
        "test_novel_rate": float(novel_te.mean()) if len(novel_te) else 0.0,
        "test_noise_rate": noise_te,
        "n_attack_test": n_attack,
        "n_benign_test": n_benign,
        "n_poison": n_poison,
        "n_novel_train": int(novel_tr.sum()),
        "n_novel_test": int(novel_te.sum()),
    }
