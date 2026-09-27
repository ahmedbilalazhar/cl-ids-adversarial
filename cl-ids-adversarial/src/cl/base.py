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


def limit_threads(n: int | None = None) -> int:
    """Pin BLAS/OMP/torch thread pools. REQUIRED when several grid workers
    share one machine: 5 workers x 8 default threads thrash 8 cores and a
    single federated run was measured at 4.3 h (vs ~100 s at 2 threads).
    Env vars must be set before numpy/torch import; torch's pool is settable
    at runtime. Returns the thread count actually applied."""
    import os

    if n is None:
        n = int(os.environ.get("CL_THREADS", "2"))
    for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(var, str(n))
    try:
        torch.set_num_threads(n)
    except Exception:
        pass
    return n


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
