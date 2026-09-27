from __future__ import annotations

import numpy as np
import torch


def small_loss_filter(
    model: torch.nn.Module,
    X: np.ndarray,
    y: np.ndarray,
    keep_ratio: float = 0.75,
    device: str = "cpu",
) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        logits = model(torch.from_numpy(X).float().to(device))
        losses = torch.nn.functional.cross_entropy(logits, torch.from_numpy(y).long().to(device), reduction="none")
        losses = losses.cpu().numpy()
    k = max(1, int(round(len(y) * keep_ratio)))
    idx = np.argsort(losses)[:k]
    mask = np.zeros(len(y), dtype=bool)
    mask[idx] = True
    return mask
