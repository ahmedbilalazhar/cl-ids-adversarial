from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from src.cl.base import BaseCLMethod


class DERpp(BaseCLMethod):
    name = "derpp"

    def __init__(self, *args, buffer_size: int = 500, alpha: float = 0.5, beta: float = 0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer_size = buffer_size
        self.alpha = alpha
        self.beta = beta
        self.buffer_x: list[np.ndarray] = []
        self.buffer_y: list[int] = []
        self.buffer_logits: list[np.ndarray] = []

    def _sample(self, batch: int):
        if not self.buffer_y:
            return None
        idx = np.random.choice(len(self.buffer_y), size=min(batch, len(self.buffer_y)), replace=False)
        xs = torch.from_numpy(np.stack([self.buffer_x[i] for i in idx])).float().to(self.device)
        ys = torch.tensor([self.buffer_y[i] for i in idx], dtype=torch.long, device=self.device)
        ls = torch.from_numpy(np.stack([self.buffer_logits[i] for i in idx])).float().to(self.device)
        return xs, ys, ls

    def observe(self, x: torch.Tensor, y: torch.Tensor) -> float:
        self.model.train()
        self.optimizer.zero_grad()
        logits = self.model(x)
        loss = nn.functional.cross_entropy(logits, y)

        sample = self._sample(x.size(0))
        if sample is not None:
            bx, by, blogits = sample
            need = max(int(by.max()) + 1, blogits.shape[1], logits.shape[1])
            if need > logits.shape[1]:
                self._maybe_expand(need)
                logits = self.model(x)
                loss = nn.functional.cross_entropy(logits, y)
                blogits = self._pad_logits(blogits, need)
            bl = self.model(bx)
            if bl.shape[1] != blogits.shape[1]:
                blogits = self._pad_logits(blogits, bl.shape[1])
            loss = loss + self.alpha * nn.functional.mse_loss(bl, blogits)
            loss = loss + self.beta * nn.functional.cross_entropy(bl, by)

        loss.backward()
        self.optimizer.step()

        with torch.no_grad():
            store_logits = self.model(x).detach().cpu().numpy()
        for xi, yi, li in zip(x.detach().cpu().numpy(), y.detach().cpu().numpy(), store_logits):
            self.buffer_x.append(xi)
            self.buffer_y.append(int(yi))
            self.buffer_logits.append(li)
        if len(self.buffer_y) > self.buffer_size:
            n = len(self.buffer_y)
            overflow = n - self.buffer_size
            drop = np.random.choice(n, size=overflow, replace=False)
            keep = np.ones(n, dtype=bool)
            keep[drop] = False
            self.buffer_x = [self.buffer_x[i] for i in range(n) if keep[i]]
            self.buffer_y = [self.buffer_y[i] for i in range(n) if keep[i]]
            self.buffer_logits = [self.buffer_logits[i] for i in range(n) if keep[i]]
        return float(loss.item())

    @staticmethod
    def _pad_logits(t: torch.Tensor, width: int) -> torch.Tensor:
        if t.shape[1] == width:
            return t
        pad = torch.zeros(t.shape[0], width - t.shape[1], device=t.device)
        return torch.cat([t, pad], dim=1)
