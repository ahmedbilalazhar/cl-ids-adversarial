from __future__ import annotations

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.cl.base import BaseCLMethod


class LwF(BaseCLMethod):
    name = "lwf"

    def __init__(self, *args, alpha: float = 1.0, temperature: float = 2.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha = alpha
        self.temperature = temperature
        self.old_model: nn.Module | None = None

    def after_task(self, task_id: int, train_loader: DataLoader) -> None:
        if hasattr(self.model, "clone"):
            self.old_model = self.model.clone()
        else:
            import copy

            self.old_model = copy.deepcopy(self.model)
        self.old_model.to(self.device)
        self.old_model.eval()

    def extra_loss(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        if self.old_model is None:
            return torch.tensor(0.0, device=self.device)
        with torch.no_grad():
            old_logits = self.old_model(x)
            old_prob = nn.functional.softmax(old_logits / self.temperature, dim=1)
        new_logits = self.model(x)
        # Phase 0 fix: if the head has grown since old_model was snapshotted,
        # distil only over the old class width (standard LwF practice) instead
        # of crashing on shape mismatch.
        if new_logits.shape[1] != old_logits.shape[1]:
            new_logits = new_logits[:, : old_logits.shape[1]]
        new_log_prob = nn.functional.log_softmax(new_logits / self.temperature, dim=1)
        loss = nn.functional.kl_div(new_log_prob, old_prob, reduction="batchmean")
        return self.alpha * (self.temperature ** 2) * loss
