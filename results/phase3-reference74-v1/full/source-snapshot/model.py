"""CPU FP32 reference MLP with isolated, append-only head initialization."""
from __future__ import annotations

import torch
from torch import nn

from .common import torch_seed


class ReferenceMLP(nn.Module):
    def __init__(self, width, seed):
        super().__init__()
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(torch_seed(4, seed))
            # PyTorch Linear.reset_parameters: Kaiming uniform with a=sqrt(5),
            # bias uniform +/- 1/sqrt(fan_in). Version is pinned by the runner.
            self.backbone = nn.Sequential(nn.Linear(74, 128), nn.ReLU(), nn.Dropout(.1),
                                          nn.Linear(128, 64), nn.ReLU(), nn.Dropout(.1))
            self.classifier = nn.Linear(64, width)
        self.initialize_rows(0, 1, seed)

    def initialize_rows(self, old_width, stage, seed):
        with torch.random.fork_rng(devices=[]), torch.no_grad():
            torch.manual_seed(torch_seed(5, seed, stage))
            nn.init.xavier_uniform_(self.classifier.weight[old_width:], gain=1)
            self.classifier.bias[old_width:].zero_()

    def expand(self, width, stage, seed):
        old = self.classifier
        if width <= old.out_features:
            raise ValueError("Stage must append newly observed annotation classes")
        with torch.random.fork_rng(devices=[]):
            new = nn.Linear(64, width)
        with torch.no_grad():
            new.weight[:old.out_features].copy_(old.weight)
            new.bias[:old.out_features].copy_(old.bias)
        self.classifier = new
        self.initialize_rows(old.out_features, stage, seed)

    def forward(self, x):
        return self.classifier(self.backbone(x))
