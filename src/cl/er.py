from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from src.cl.base import BaseCLMethod


class ExperienceReplay(BaseCLMethod):
    name = "er"

    def __init__(self, *args, buffer_size: int = 500, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer_size = buffer_size
        self.buffer_x: list[np.ndarray] = []
        self.buffer_y: list[int] = []

    def _sample_buffer(self, batch: int) -> tuple[torch.Tensor, torch.Tensor] | None:
        if not self.buffer_y:
            return None
        idx = np.random.choice(len(self.buffer_y), size=min(batch, len(self.buffer_y)), replace=False)
        xs = torch.from_numpy(np.stack([self.buffer_x[i] for i in idx])).float().to(self.device)
        ys = torch.tensor([self.buffer_y[i] for i in idx], dtype=torch.long, device=self.device)
        return xs, ys

    def observe(self, x: torch.Tensor, y: torch.Tensor) -> float:
        self.model.train()
        self.optimizer.zero_grad()
        logits = self.model(x)
        loss = nn.functional.cross_entropy(logits, y)

        buf = self._sample_buffer(x.size(0))
        if buf is not None:
            bx, by = buf
            if int(by.max()) + 1 > logits.shape[1]:
                self._maybe_expand(int(by.max()) + 1)
                logits = self.model(x)
                loss = nn.functional.cross_entropy(logits, y)
            buf_logits = self.model(bx)
            loss = loss + nn.functional.cross_entropy(buf_logits, by)

        loss.backward()
        self.optimizer.step()

        for xi, yi in zip(x.detach().cpu().numpy(), y.detach().cpu().numpy()):
            self.buffer_x.append(xi)
            self.buffer_y.append(int(yi))
        if len(self.buffer_y) > self.buffer_size:
            n = len(self.buffer_y)
            overflow = n - self.buffer_size
            drop = np.random.choice(n, size=overflow, replace=False)
            keep_mask = np.ones(n, dtype=bool)
            keep_mask[drop] = False
            self.buffer_x = [self.buffer_x[i] for i in range(n) if keep_mask[i]]
            self.buffer_y = [self.buffer_y[i] for i in range(n) if keep_mask[i]]
        return float(loss.item())
