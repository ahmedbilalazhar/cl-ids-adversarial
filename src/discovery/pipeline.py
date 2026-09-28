"""Train-only discovery and frozen out-of-sample assignment."""
from __future__ import annotations

import numpy as np
import torch
from sklearn.cluster import HDBSCAN
from sklearn.metrics import adjusted_rand_score

from src.models.mlp import Autoencoder


def recon_scores(ae: Autoencoder, X: np.ndarray, device: str = "cpu", batch: int = 4096) -> np.ndarray:
    ae.eval()
    out: list[np.ndarray] = []
    with torch.no_grad():
        for i in range(0, len(X), batch):
            xb = torch.from_numpy(X[i : i + batch]).float().to(device)
            out.append(ae.recon_error(xb).cpu().numpy())
    return np.concatenate(out).astype(np.float32) if out else np.zeros(0, dtype=np.float32)


def fit_threshold(clean_scores: np.ndarray, quantile: float = 0.95) -> float:
    if clean_scores.size == 0:
        raise ValueError("benign calibration flows are required")
    return float(np.quantile(clean_scores, quantile))


def cluster_novel(X_novel: np.ndarray, min_cluster_size: int = 15, min_samples: int = 5) -> np.ndarray:
    n = len(X_novel)
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    if n < max(min_cluster_size, min_samples + 1):
        return np.full(n, -1, dtype=np.int64)
    mcs = int(min(min_cluster_size, max(2, n // 4)))
    ms = int(min(min_samples, mcs))
    return HDBSCAN(min_cluster_size=mcs, min_samples=ms, copy=True).fit_predict(X_novel).astype(np.int64)


def fit_discovery(
    ae: Autoencoder, threshold: float, X_train: np.ndarray, poison_mask: np.ndarray,
    *, device: str = "cpu", min_cluster_size: int = 15,
    max_cluster_candidates: int = 4000, seed: int = 42,
) -> dict:
    """Fit HDBSCAN on training candidates; retain frozen assignment geometry.

    Out-of-sample membership uses the nearest training centroid within its
    maximum training-member Euclidean radius. This is an explicit approximation
    to HDBSCAN membership, not HDBSCAN's own prediction rule.
    """
    poison_mask = np.asarray(poison_mask, dtype=bool)
    if len(poison_mask) != len(X_train):
        raise ValueError("poison mask length does not match training data")
    if max_cluster_candidates < min_cluster_size:
        raise ValueError("max_cluster_candidates must be at least min_cluster_size")
    novel = recon_scores(ae, X_train, device=device) >= threshold
    candidate_index = np.flatnonzero(novel)
    if len(candidate_index) > max_cluster_candidates:
        fit_index = np.sort(np.random.RandomState(seed).choice(
            candidate_index, size=max_cluster_candidates, replace=False,
        ))
    else:
        fit_index = candidate_index
    labels = cluster_novel(X_train[fit_index], min_cluster_size=min_cluster_size)
    train_labels = np.full(len(X_train), -1, dtype=np.int64)
    train_labels[fit_index] = labels
    centers, radii = {}, {}
    for cluster in sorted(set(labels) - {-1}):
        idx = fit_index[labels == cluster]
        members = X_train[idx]
        center = members.mean(axis=0)
        centers[int(cluster)] = center
        radii[int(cluster)] = float(np.linalg.norm(members - center, axis=1).max())
    fitted_geometry = {"centers": centers, "radii": radii}
    remaining = np.setdiff1d(candidate_index, fit_index, assume_unique=True)
    train_labels[remaining] = assign_clusters(X_train[remaining], fitted_geometry)
    poison_fraction = {
        int(cluster): float(poison_mask[train_labels == cluster].mean())
        for cluster in centers
    }
    return {
        "train_labels": train_labels, "novel_train": novel,
        "poison_mask": poison_mask,
        "n_fit_candidates": len(fit_index), "n_novel_candidates": len(candidate_index),
        "centers": centers, "radii": radii, "poison_fraction": poison_fraction,
        "fictitious": sorted(c for c, fraction in poison_fraction.items() if fraction >= 0.5),
    }


def assign_clusters(X: np.ndarray, fitted: dict, *, batch: int = 4096) -> np.ndarray:
    """Assign to the nearest frozen training centroid within its radius."""
    result = np.full(len(X), -1, dtype=np.int64)
    ids = sorted(fitted["centers"])
    if not ids:
        return result
    centers = np.stack([fitted["centers"][c] for c in ids])
    radii = np.array([fitted["radii"][c] for c in ids])
    for start in range(0, len(X), batch):
        distances = np.linalg.norm(X[start : start + batch, None, :] - centers[None, :, :], axis=2)
        nearest = distances.argmin(axis=1)
        accepted = distances[np.arange(len(nearest)), nearest] <= radii[nearest]
        result[start : start + len(nearest)][accepted] = np.asarray(ids)[nearest[accepted]]
    return result


def provisional_labels(y_train: np.ndarray, fitted: dict, next_class: int) -> tuple[np.ndarray, dict[int, int]]:
    """Replace clustered candidate labels with contiguous task-unique IDs."""
    labels = np.asarray(y_train).copy()
    mapping = {cluster: next_class + i for i, cluster in enumerate(sorted(fitted["centers"]))}
    for cluster, class_id in mapping.items():
        labels[fitted["train_labels"] == cluster] = class_id
    return labels, mapping


def evaluate_discovery(
    ae: Autoencoder, threshold: float, fitted: dict, X_test: np.ndarray,
    y_test: np.ndarray, *, device: str = "cpu", benign_label: int = 0,
) -> dict:
    """Evaluate held-out flows against fixed training clusters, without refit."""
    novel = recon_scores(ae, X_test, device=device) >= threshold
    assigned = np.full(len(X_test), -1, dtype=np.int64)
    assigned[novel] = assign_clusters(X_test[novel], fitted)
    attack = y_test != benign_label
    benign = ~attack
    flagged_attack = attack & novel
    absorbed = flagged_attack & np.isin(assigned, fitted["fictitious"])
    n_attack = int(attack.sum())
    n_flagged = int(flagged_attack.sum())
    n_benign = int(benign.sum())
    n_poison = int(fitted["poison_mask"].sum())
    n_poison_novel = int((fitted["poison_mask"] & fitted["novel_train"]).sum())
    clean_train = ~fitted["poison_mask"]
    assigned_mask = assigned >= 0
    n_assigned = int(assigned_mask.sum())
    purity_count = sum(
        int(np.unique(y_test[assigned == cluster], return_counts=True)[1].max())
        for cluster in fitted["centers"] if (assigned == cluster).any()
    )
    return {
        "threshold": float(threshold), "n_clusters": len(fitted["centers"]),
        "n_fictitious": len(fitted["fictitious"]),
        "discovery_miss_rate": float((~novel[attack]).mean()) if n_attack else None,
        "benign_false_alert_rate": float(novel[benign].mean()) if n_benign else None,
        "attack_flagged_rate": n_flagged / n_attack if n_attack else None,
        "absorbed_attack_rate": int(absorbed.sum()) / n_attack if n_attack else None,
        "absorbed_flagged_attack_rate": int(absorbed.sum()) / n_flagged if n_flagged else None,
        "clustered_attack_rate": float((assigned[flagged_attack] >= 0).mean()) if n_flagged else None,
        "noise_rate_attack": float((assigned[flagged_attack] < 0).mean()) if n_flagged else None,
        "fictitious_absorption": float(np.isin(assigned[benign & novel], fitted["fictitious"]).mean()) if (benign & novel).any() else None,
        "test_novel_rate": float(novel.mean()) if len(novel) else None,
        "test_noise_rate": float((assigned[novel] < 0).mean()) if novel.any() else None,
        "cluster_assignment_purity": purity_count / n_assigned if n_assigned else None,
        "cluster_assignment_ari": float(adjusted_rand_score(y_test[assigned_mask], assigned[assigned_mask])) if n_assigned >= 2 else None,
        "n_test_assigned": n_assigned,
        "n_attack_test": n_attack, "n_benign_test": n_benign,
        "n_attack_flagged": n_flagged, "n_attack_absorbed": int(absorbed.sum()),
        "n_poison": n_poison, "n_poison_novel": n_poison_novel,
        "poison_novel_rate": n_poison_novel / n_poison if n_poison else None,
        "clean_novel_rate": float(fitted["novel_train"][clean_train].mean()) if clean_train.any() else None,
        "n_novel_train": int(fitted["novel_train"].sum()),
        "n_clustered_train": int((fitted["train_labels"] >= 0).sum()),
        "n_novel_test": int(novel.sum()),
    }
