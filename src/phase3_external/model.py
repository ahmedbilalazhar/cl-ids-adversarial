"""Variable-input MLP that mirrors the Phase 3 reference shape for extensions."""
from __future__ import annotations

import torch
from torch import nn

from src.phase3.common import torch_seed


class ExternalMLP(nn.Module):
    def __init__(self, input_dim: int, output_width: int, seed: int):
        super().__init__()
        if input_dim <= 0 or output_width <= 0:
            raise ValueError("Invalid external model dimensions")
        self.input_dim = input_dim
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(torch_seed(4, seed))
            self.backbone = nn.Sequential(nn.Linear(input_dim, 128), nn.ReLU(), nn.Dropout(.1),
                                          nn.Linear(128, 64), nn.ReLU(), nn.Dropout(.1))
            self.classifier = nn.Linear(64, output_width)
        self.initialize_rows(0, 1, seed)

    def initialize_rows(self, old_width: int, stage: int, seed: int) -> None:
        with torch.random.fork_rng(devices=[]), torch.no_grad():
            torch.manual_seed(torch_seed(5, seed, stage))
            nn.init.xavier_uniform_(self.classifier.weight[old_width:], gain=1)
            self.classifier.bias[old_width:].zero_()

    def expand(self, output_width: int, stage: int, seed: int) -> None:
        old = self.classifier
        if output_width <= old.out_features:
            raise ValueError("External task head must append newly observed labels")
        with torch.random.fork_rng(devices=[]):
            new = nn.Linear(64, output_width)
        with torch.no_grad():
            new.weight[:old.out_features].copy_(old.weight)
            new.bias[:old.out_features].copy_(old.bias)
        self.classifier = new
        self.initialize_rows(old.out_features, stage, seed)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != 2 or x.shape[1] != self.input_dim:
            raise ValueError("External feature dimension differs from initialized model")
        return self.classifier(self.backbone(x))
