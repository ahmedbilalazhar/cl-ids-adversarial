from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class TrainState:
    task_id: int = 0
    buffer: list = field(default_factory=list)


def to_loader(X: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool = True) -> DataLoader:
    ds = TensorDataset(torch.from_numpy(X), torch.from_numpy(y))
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class BaseCLMethod:
    name = "base"

    def __init__(self, model: nn.Module, lr: float = 1e-3, device: str = "cpu", **kwargs):
        self.model = model
        self.device = torch.device(device)
        self.model.to(self.device)
        self.lr = lr
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.kwargs = kwargs
        self.state = TrainState()

    def _refresh_optimizer(self) -> None:
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

    def _maybe_expand(self, n: int) -> None:
        if hasattr(self.model, "expand_head"):
            old = self.model.classifier
            self.model.expand_head(n)
            if self.model.classifier is not old:
                self._refresh_optimizer()

    def before_task(self, task_id: int, train_loader: DataLoader, class_bound: int) -> None:
        self.state.task_id = task_id
        self._maybe_expand(class_bound)

    def after_task(self, task_id: int, train_loader: DataLoader) -> None:
        pass

    def extra_loss(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return torch.tensor(0.0, device=self.device)

    def observe(self, x: torch.Tensor, y: torch.Tensor) -> float:
        self.model.train()
        self.optimizer.zero_grad()
        logits = self.model(x)
        loss = nn.functional.cross_entropy(logits, y) + self.extra_loss(x, y)
        loss.backward()
        self.optimizer.step()
        return float(loss.item())

    def train_task(self, train_loader: DataLoader, epochs: int) -> list[float]:
        losses = []
        for _ in range(epochs):
            for xb, yb in train_loader:
                losses.append(self.observe(xb.to(self.device), yb.to(self.device)))
        return losses

    @torch.no_grad()
    def predict(self, X: np.ndarray) -> np.ndarray:
        self.model.eval()
        x = torch.from_numpy(X).to(self.device)
        logits = self.model(x)
        return logits.argmax(dim=1).cpu().numpy()
