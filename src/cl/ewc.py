from __future__ import annotations

import torch
from torch import nn
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

    def _maybe_expand(self, n: int) -> None:
        super()._maybe_expand(n)
        self._align_head_state()

    def _align_head_state(self) -> None:
        """Protect old classifier rows; newly added rows have zero importance."""
        for name, parameter in self.model.named_parameters():
            if name not in self.fisher or name not in self.anchor:
                continue
            fisher, anchor = self.fisher[name], self.anchor[name]
            if fisher.shape == parameter.shape == anchor.shape:
                continue
            if not (
                name.startswith("classifier.") and fisher.shape == anchor.shape
                and fisher.ndim == parameter.ndim
                and fisher.shape[1:] == parameter.shape[1:]
                and fisher.shape[0] <= parameter.shape[0]
            ):
                raise ValueError(f"EWC state shape mismatch for {name}")
            expanded_fisher = torch.zeros_like(parameter)
            expanded_anchor = parameter.detach().clone()
            expanded_fisher[:fisher.shape[0]] = fisher
            expanded_anchor[:anchor.shape[0]] = anchor
            self.fisher[name] = expanded_fisher
            self.anchor[name] = expanded_anchor

    def after_task(self, task_id: int, train_loader: DataLoader) -> None:
        self._align_head_state()
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
        for k, v in fisher.items():
            fisher[k] = v / max(n, 1)
        if not self.fisher:
            self.fisher = fisher
        else:
            # Accumulated batch-gradient importance around the latest anchor:
            # an online approximation, not the exact sum of per-task penalties.
            # Head state was aligned above, preserving old-row importance.
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
        self._align_head_state()
        loss = torch.tensor(0.0, device=self.device)
        for n, p in self.model.named_parameters():
            if n in self.fisher and n in self.anchor:
                f = self.fisher[n]
                a = self.anchor[n]
                loss = loss + (f * (p - a) ** 2).sum()
        # Published EWC (Kirkpatrick et al. 2017, eq. 3) carries a 1/2
        # factor: (lambda/2) * sum F*(theta-theta*)^2. Previous code used
        # lambda * sum (2x effective strength at the same lambda value).
        return 0.5 * self.ewc_lambda * loss
