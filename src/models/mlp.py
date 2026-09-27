from __future__ import annotations

import copy

import torch
import torch.nn as nn


class TabularMLP(nn.Module):
    def __init__(self, in_dim: int, num_classes: int, hidden: list[int] | None = None):
        super().__init__()
        hidden = hidden or [128, 64]
        layers: list[nn.Module] = []
        prev = in_dim
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(0.1)]
            prev = h
        self.backbone = nn.Sequential(*layers)
        self.classifier = nn.Linear(prev, num_classes)
        self._out_features = prev

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.backbone(x))

    def expand_head(self, new_num_classes: int) -> None:
        if new_num_classes <= self.classifier.out_features:
            return
        old = self.classifier
        new = nn.Linear(old.in_features, new_num_classes)
        with torch.no_grad():
            new.weight[: old.out_features] = old.weight
            new.bias[: old.out_features] = old.bias
            nn.init.xavier_uniform_(new.weight[old.out_features :])
            new.bias[old.out_features :].zero_()
        self.classifier = new

    def clone(self) -> "TabularMLP":
        return copy.deepcopy(self)


class Autoencoder(nn.Module):
    def __init__(self, in_dim: int, latent: int = 16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(),
            nn.Linear(64, latent),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent, 64),
            nn.ReLU(),
            nn.Linear(64, in_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))

    def recon_error(self, x: torch.Tensor) -> torch.Tensor:
        return torch.mean((self.forward(x) - x) ** 2, dim=1)
