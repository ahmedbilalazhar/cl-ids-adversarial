from __future__ import annotations

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from src.cl.base import BaseCLMethod


class EWC(BaseCLMethod):
    name = "ewc"

    def __init__(self, *args, ewc_lambda: float = 100.0, fisher_batches: int = 32, **kwargs):
        super().__init__(*args, **kwargs)
        self.ewc_lambda = ewc_lambda
        self.fisher_batches = fisher_batches
        self.fisher: dict[str, torch.Tensor] = {}
        self.anchor: dict[str, torch.Tensor] = {}

    def after_task(self, task_id: int, train_loader: DataLoader) -> None:
        self.model.eval()
        fisher = {n: torch.zeros_like(p) for n, p in self.model.named_parameters() if p.requires_grad}
        n = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(self.device), yb.to(self.device)
            self.model.zero_grad()
            logits = self.model(xb)
            loss = nn.functional.cross_entropy(logits, yb)
            loss.backward()
            for name, p in self.model.named_parameters():
                if p.grad is not None:
                    fisher[name] += p.grad.detach() ** 2
            n += 1
            if n >= self.fisher_batches:
                break
        for k in fisher:
            fisher[k] = fisher[k] / max(n, 1)
        if not self.fisher:
            self.fisher = fisher
        else:
            # Phase 0 fix: accumulate across tasks (Kirkpatrick et al. sum
            # over previous tasks). Old code overwrote, regularising only
            # toward the immediately previous task. Keys with changed shapes
            # (head expansion) are re-initialised to the new shape.
            merged: dict[str, torch.Tensor] = {}
            for k, v in fisher.items():
                if k in self.fisher and self.fisher[k].shape == v.shape:
                    merged[k] = self.fisher[k] + v
                else:
                    merged[k] = v
            self.fisher = merged
        self.anchor = {
            n: p.detach().clone()
            for n, p in self.model.named_parameters()
            if p.requires_grad
        }

    def extra_loss(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        if not self.fisher:
            return torch.tensor(0.0, device=self.device)
        loss = torch.tensor(0.0, device=self.device)
        for n, p in self.model.named_parameters():
            if n in self.fisher and n in self.anchor:
                f = self.fisher[n]
                a = self.anchor[n]
                # Phase 0 fix: skip stale entries whose shapes predate a
                # head expansion instead of crashing on broadcast.
                if f.shape != p.shape or a.shape != p.shape:
                    continue
                loss = loss + (f * (p - a) ** 2).sum()
        # Published EWC (Kirkpatrick et al. 2017, eq. 3) carries a 1/2
        # factor: (lambda/2) * sum F*(theta-theta*)^2. Previous code used
        # lambda * sum (2x effective strength at the same lambda value).
        return 0.5 * self.ewc_lambda * loss
